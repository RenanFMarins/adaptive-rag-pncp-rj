"""Consulta determinística e somente leitura sobre a base PNCP normalizada.

O SQL é construído exclusivamente a partir de mapeamentos internos. Valores
extraídos da pergunta são sempre enviados como parâmetros ao SQLite.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from app.core.text_normalization import normalizar_para_busca

from .schemas import (
    QueryAnalysis,
    QueryEntity,
    StructuredField,
    StructuredOperation,
    StructuredQueryResult,
    ValueFilterField,
)
from .structured_tool import StructuredQueryError


@dataclass(frozen=True)
class _NormalizedEntitySqlConfig:
    from_sql: str
    id_expression: str
    required_tables: frozenset[str]
    fields: dict[StructuredField, str]


_ENTITY_CONFIG: dict[QueryEntity, _NormalizedEntitySqlConfig] = {
    QueryEntity.CONTRATO: _NormalizedEntitySqlConfig(
        from_sql=(
            "contrato AS entity "
            "JOIN unidade AS unit "
            "ON unit.orgao_cnpj = entity.orgao_cnpj "
            "AND unit.codigo_unidade = entity.codigo_unidade "
            "JOIN orgao AS agency ON agency.cnpj = entity.orgao_cnpj "
            "LEFT JOIN fornecedor AS supplier "
            "ON supplier.tipo_pessoa = entity.tipo_pessoa_fornecedor "
            "AND supplier.ni_fornecedor = entity.ni_fornecedor "
            "LEFT JOIN contratacao AS purchase "
            "ON purchase.numero_controle_pncp = entity.contratacao_id"
        ),
        id_expression="entity.numero_controle_pncp",
        required_tables=frozenset(
            {"contrato", "unidade", "orgao", "fornecedor", "contratacao"}
        ),
        fields={
            StructuredField.VALOR_GLOBAL: (
                "CAST(entity.valor_global_centavos AS REAL) / 100.0"
            ),
            StructuredField.VALOR_ESTIMADO: (
                "CAST(entity.valor_inicial_centavos AS REAL) / 100.0"
            ),
            StructuredField.ANO: "entity.ano_contrato",
            StructuredField.DATA_PUBLICACAO: "entity.data_publicacao_pncp",
            StructuredField.MUNICIPIO: "unit.municipio_nome",
            StructuredField.ORGAO: "agency.razao_social",
            StructuredField.FORNECEDOR: (
                "COALESCE(supplier.nome_razao_social, "
                "entity.nome_fornecedor_informado)"
            ),
            StructuredField.MODALIDADE: "purchase.modalidade_nome",
            StructuredField.OBJETO: "entity.objeto_contrato",
        },
    ),
    QueryEntity.CONTRATACAO: _NormalizedEntitySqlConfig(
        from_sql=(
            "contratacao AS entity "
            "JOIN unidade AS unit "
            "ON unit.orgao_cnpj = entity.orgao_cnpj "
            "AND unit.codigo_unidade = entity.codigo_unidade "
            "JOIN orgao AS agency ON agency.cnpj = entity.orgao_cnpj"
        ),
        id_expression="entity.numero_controle_pncp",
        required_tables=frozenset({"contratacao", "unidade", "orgao"}),
        fields={
            StructuredField.VALOR_GLOBAL: (
                "CAST(COALESCE(entity.valor_total_homologado_centavos, "
                "entity.valor_total_estimado_centavos) AS REAL) / 100.0"
            ),
            StructuredField.VALOR_ESTIMADO: (
                "CAST(entity.valor_total_estimado_centavos AS REAL) / 100.0"
            ),
            StructuredField.ANO: "entity.ano_compra",
            StructuredField.DATA_PUBLICACAO: "entity.data_publicacao_pncp",
            StructuredField.MUNICIPIO: "unit.municipio_nome",
            StructuredField.ORGAO: "agency.razao_social",
            StructuredField.MODALIDADE: "entity.modalidade_nome",
            StructuredField.OBJETO: "entity.objeto_compra",
        },
    ),
}

_AGGREGATE_OPERATIONS = {
    StructuredOperation.SUM,
    StructuredOperation.AVG,
    StructuredOperation.MIN,
    StructuredOperation.MAX,
}

_CANONICAL_FIELDS = (
    StructuredField.ANO,
    StructuredField.DATA_PUBLICACAO,
    StructuredField.MUNICIPIO,
    StructuredField.ORGAO,
    StructuredField.FORNECEDOR,
    StructuredField.MODALIDADE,
    StructuredField.OBJETO,
    StructuredField.VALOR_GLOBAL,
    StructuredField.VALOR_ESTIMADO,
)


def _field_expression(
    config: _NormalizedEntitySqlConfig,
    field: StructuredField,
    *,
    required: bool = True,
) -> str | None:
    expression = config.fields.get(field)
    if expression is None and required:
        raise StructuredQueryError(
            f"O campo '{field.value}' não está disponível para esta entidade."
        )
    return expression


def _require_normalized_schema(
    connection: sqlite3.Connection,
    config: _NormalizedEntitySqlConfig,
) -> None:
    existing = {
        str(row[0])
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        )
    }
    missing = sorted(config.required_tables - existing)
    if missing:
        raise StructuredQueryError(
            "Banco normalizado incompleto; tabelas ausentes: " + ", ".join(missing)
        )


def _where_clause(
    analysis: QueryAnalysis,
    config: _NormalizedEntitySqlConfig,
) -> tuple[list[str], list[object]]:
    filters = analysis.filters
    if filters.tipo_entidade and filters.tipo_entidade is not analysis.entity:
        raise StructuredQueryError("tipo_entidade diverge da entidade analisada.")
    if filters.document_id is not None or filters.tipo_documento:
        raise StructuredQueryError(
            "Filtros de documento pertencem à recuperação documental."
        )

    clauses: list[str] = []
    params: list[object] = []
    if filters.numero_controle_pncp:
        clauses.append(f"{config.id_expression} = ?")
        params.append(filters.numero_controle_pncp)

    for field, value in (
        (StructuredField.ORGAO, filters.orgao),
        (StructuredField.MUNICIPIO, filters.municipio),
        (StructuredField.FORNECEDOR, filters.fornecedor),
        (StructuredField.MODALIDADE, filters.modalidade),
        (StructuredField.OBJETO, filters.objeto),
    ):
        if value:
            expression = _field_expression(config, field)
            clauses.append(f"normalizar_busca({expression}) LIKE ?")
            params.append(f"%{normalizar_para_busca(value)}%")

    if filters.ano is not None:
        clauses.append(f"{_field_expression(config, StructuredField.ANO)} = ?")
        params.append(filters.ano)

    publication_date = _field_expression(config, StructuredField.DATA_PUBLICACAO)
    if filters.period_start:
        clauses.append(f"date({publication_date}) >= date(?)")
        params.append(filters.period_start.isoformat())
    if filters.period_end:
        clauses.append(f"date({publication_date}) <= date(?)")
        params.append(filters.period_end.isoformat())

    value_field = filters.campo_valor or ValueFilterField.VALOR_GLOBAL
    value_expression = _field_expression(
        config,
        StructuredField(value_field.value),
    )
    if filters.valor_minimo is not None:
        clauses.append(f"{value_expression} >= ?")
        params.append(filters.valor_minimo)
    if filters.valor_maximo is not None:
        clauses.append(f"{value_expression} <= ?")
        params.append(filters.valor_maximo)
    return clauses, params


def _select_clause(
    analysis: QueryAnalysis,
    config: _NormalizedEntitySqlConfig,
) -> list[str]:
    aggregate_operations = _AGGREGATE_OPERATIONS.intersection(analysis.operations)
    is_aggregate = bool(
        aggregate_operations or StructuredOperation.COUNT in analysis.operations
    )
    if analysis.group_by and not is_aggregate:
        raise StructuredQueryError("group_by exige ao menos uma agregação.")

    if not is_aggregate:
        selections = [f"{config.id_expression} AS numero_controle_pncp"]
        for field in _CANONICAL_FIELDS:
            expression = _field_expression(config, field, required=False)
            selections.append(
                f"{expression} AS {field.value}"
                if expression
                else f"NULL AS {field.value}"
            )
        return selections

    selections = [
        f"{_field_expression(config, field)} AS {field.value}"
        for field in analysis.group_by
    ]
    if StructuredOperation.COUNT in analysis.operations:
        selections.append("COUNT(*) AS count")
    for operation in sorted(aggregate_operations, key=lambda value: value.value):
        field = analysis.aggregation_field
        if field is None:
            raise StructuredQueryError("Operação agregada sem campo de agregação.")
        selections.append(
            f"{operation.value.upper()}({_field_expression(config, field)}) "
            f"AS {operation.value}_{field.value}"
        )
    return selections


def _order_clause(
    analysis: QueryAnalysis,
    config: _NormalizedEntitySqlConfig,
) -> str:
    if not analysis.order_by:
        return ""
    values: list[str] = []
    for order in analysis.order_by:
        expression = (
            "COUNT(*)"
            if order.field.value == "count"
            else _field_expression(config, order.field)
        )
        values.append(f"{expression} {order.direction.value.upper()}")
    return " ORDER BY " + ", ".join(values)


def executar_consulta_normalizada(
    connection: sqlite3.Connection,
    analysis: QueryAnalysis,
) -> StructuredQueryResult:
    """Executa o plano validado nas tabelas relacionais normalizadas."""

    config = _ENTITY_CONFIG.get(analysis.entity)
    if config is None:
        raise StructuredQueryError(
            "A ferramenta normalizada suporta somente contrato ou contratação."
        )
    _require_normalized_schema(connection, config)
    connection.create_function(
        "normalizar_busca",
        1,
        normalizar_para_busca,
        deterministic=True,
    )

    clauses, params = _where_clause(analysis, config)
    selections = _select_clause(analysis, config)
    where_sql = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    group_sql = ""
    if analysis.group_by:
        group_sql = " GROUP BY " + ", ".join(
            _field_expression(config, field) for field in analysis.group_by
        )
    limit = analysis.limit or 20
    query = (
        "SELECT "
        + ", ".join(selections)
        + " FROM "
        + config.from_sql
        + where_sql
        + group_sql
        + _order_clause(analysis, config)
        + " LIMIT ?"
    )
    cursor = connection.execute(query, [*params, limit])
    columns = [description[0] for description in cursor.description or []]
    rows = [dict(zip(columns, row, strict=True)) for row in cursor.fetchall()]
    return StructuredQueryResult(
        entity=analysis.entity,
        columns=columns,
        rows=rows,
        row_count=len(rows),
        limit_applied=limit,
    )
