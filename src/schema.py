from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

import yaml


@dataclass(frozen=True)
class SourceConfig:
	id: str
	base: str
	endpoint: str
	base_id: str = "pncp"
	natureza: str = "estruturada"
	resource_type: str = "records"
	params: Mapping[str, Any] = field(default_factory=dict)
	item_path: str | None = None
	key_fields: tuple[str, ...] = ()
	page_param: str = "pagina"
	page_size_param: str = "tamanhoPagina"
	page_size: int = 50
	max_pages: int | None = None
	timeout_seconds: float = 30.0
	rate_limit_seconds: float = 0.0
	headers: Mapping[str, str] = field(default_factory=dict)

	@classmethod
	def from_mapping(cls, value: Mapping[str, Any]) -> "SourceConfig":
		pagination = value.get("pagination", {})
		request = value.get("request", {})
		return cls(
			id=str(value["id"]),
			base=str(value.get("base", "")),
			endpoint=str(value["endpoint"]),
			base_id=str(value.get("base_id", "pncp")),
			natureza=str(value.get("natureza", "estruturada")),
			resource_type=str(value.get("resource_type", "records")),
			params=dict(value.get("params", {})),
			item_path=value.get("item_path"),
			key_fields=tuple(value.get("key_fields", ())),
			page_param=str(pagination.get("page_param", "pagina")),
			page_size_param=str(pagination.get("page_size_param", "tamanhoPagina")),
			page_size=int(pagination.get("page_size", 50)),
			max_pages=(int(pagination["max_pages"]) if pagination.get("max_pages") is not None else None),
			timeout_seconds=float(request.get("timeout_seconds", 30.0)),
			rate_limit_seconds=float(request.get("rate_limit_seconds", 0.0)),
			headers=dict(request.get("headers", {})),
		)

	@property
	def url(self) -> str:
		return f"{self.base.rstrip('/')}/{self.endpoint.lstrip('/')}"


@dataclass(frozen=True)
class Manifest:
	sources: tuple[SourceConfig, ...]

	@classmethod
	def load(cls, path: str | Path) -> "Manifest":
		with Path(path).open(encoding="utf-8") as file:
			document = yaml.safe_load(file) or {}
		return cls(tuple(SourceConfig.from_mapping(item) for item in document.get("sources", [])))

	def source(self, source_id: str) -> SourceConfig:
		for source in self.sources:
			if source.id == source_id:
				return source
		raise KeyError(f"Fonte não encontrada no manifesto: {source_id}")


@dataclass(frozen=True)
class CollectedRecord:
	source_id: str
	payload: Mapping[str, Any]
	source_url: str
	cursor: str
	ordinal: int


@dataclass(frozen=True)
class IngestionResult:
	run_id: str
	source_id: str
	status: str
	records_seen: int
	new: int
	updated: int
	unchanged: int
	failed: int = 0


def value_at_path(value: Any, path: str) -> Any:
	current = value
	for part in path.split(".") if path else ():
		if isinstance(current, Mapping):
			current = current.get(part)
		elif isinstance(current, list) and part.isdigit():
			current = current[int(part)]
		else:
			return None
	return current


def records_from_response(response: Any, item_path: str | None = None) -> list[Mapping[str, Any]]:
	values = value_at_path(response, item_path) if item_path else response
	if isinstance(values, list):
		return [item for item in values if isinstance(item, Mapping)]
	if isinstance(values, Mapping):
		for key in ("data", "items", "content", "resultado", "results"):
			candidate = values.get(key)
			if isinstance(candidate, list):
				return [item for item in candidate if isinstance(item, Mapping)]
	raise ValueError("Resposta PNCP não contém uma lista de registros")
