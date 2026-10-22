# Perguntas para Validação do Sistema RAG — Contratações Públicas

## 1. Perguntas Estruturadas (Banco de Dados)

1. Quantas contratações por dispensa existem em 2026?
2. Liste as 10 contratações de 2026 com maior valor estimado.

## 2. Perguntas Documentais (RAG)

As perguntas abaixo possuem evidências documentais reais no banco de dados, conforme informado por Luciano Oliveira.

1. Quais práticas de sustentabilidade são previstas para a contratação de manutenção de elevadores?
2. Quais obrigações de LGPD são previstas nos documentos de contratação?
3. Como ocorre a fiscalização administrativa do contrato?
4. Quais documentos são necessários para verificar a habilitação da contratada?
5. Quais são as condições previstas para reajuste contratual?
6. Quais obrigações da contratada estão relacionadas à execução do contrato?
7. Como funciona a subcontratação nos documentos recuperados?
8. Quais exigências existem para manutenção das condições de habilitação?

## 3. Pergunta Híbrida (Dados Estruturados + RAG)

> Para a contratação `00394502000144-1-009055/2026`, informe o valor estimado e as práticas de sustentabilidade previstas.

### Objetivo da Validação

Verificar a capacidade do sistema de responder a três categorias de consultas:

- **Estruturadas:** consultas sobre registros e valores armazenados no banco de dados.
- **Documentais:** consultas que exigem recuperação de trechos relevantes dos documentos por meio do RAG.
- **Híbridas:** consultas que combinam informações estruturadas do banco com evidências textuais recuperadas dos documentos.

**Critério de avaliação:** as respostas devem apresentar informações corretas, fundamentadas nos dados disponíveis e, quando aplicável, acompanhadas das respectivas evidências documentais.