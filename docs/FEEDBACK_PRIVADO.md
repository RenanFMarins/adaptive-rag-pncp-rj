# Feedback privado das respostas

A interface permite marcar uma resposta como útil ou não útil. A avaliação é
vinculada ao `history_id` retornado por `/query/ask` e só pode ser consultada,
alterada ou removida pelo usuário dono desse evento.

## Dados armazenados

- `history_event_id` e `user_id` internos;
- nota `1` ou `-1`;
- código fechado de motivo;
- datas de criação e atualização.

Não há campo para comentário livre. Perguntas, respostas, prompts, tokens e
credenciais não são copiados para o feedback. Excluir o evento do histórico
remove automaticamente a avaliação relacionada.

## Rotas

```text
POST   /feedback               cria ou atualiza a avaliação
GET    /feedback/{history_id}  consulta a própria avaliação
DELETE /feedback/{history_id}  remove a própria avaliação
```

O corpo aceito pelo `POST` é:

```json
{
  "history_id": 123,
  "rating": 1,
  "reason_code": "helpful"
}
```

Os motivos aceitos são `helpful`, `incorrect`, `incomplete`, `outdated` e
`other`. A interface principal usa `helpful` e `incorrect`; os demais códigos
ficam disponíveis para clientes que ofereçam uma classificação mais detalhada.
