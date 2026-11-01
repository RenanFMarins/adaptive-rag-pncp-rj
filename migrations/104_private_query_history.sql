-- Histórico técnico mínimo e privado das consultas adaptativas.
-- Não armazena pergunta, resposta, prompt, token ou payload bruto.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS query_history_events (
    id INTEGER NOT NULL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    route VARCHAR(16),
    entity VARCHAR(32),
    status VARCHAR(16) NOT NULL
        CHECK (status IN ('success', 'error', 'refused')),
    question_length INTEGER NOT NULL CHECK (question_length >= 0),
    result_count INTEGER NOT NULL DEFAULT 0 CHECK (result_count >= 0),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_query_history_user_created
    ON query_history_events(user_id, created_at);

CREATE INDEX IF NOT EXISTS idx_query_history_expires
    ON query_history_events(expires_at);

CREATE UNIQUE INDEX IF NOT EXISTS uq_query_history_owner
    ON query_history_events(id, user_id);
