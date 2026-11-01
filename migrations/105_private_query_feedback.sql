-- Feedback mínimo e privado vinculado ao histórico autenticado.
-- Não armazena comentários livres ou conteúdo da conversa.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS private_query_feedback (
    id INTEGER NOT NULL PRIMARY KEY,
    history_event_id INTEGER NOT NULL UNIQUE,
    user_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK (rating IN (-1, 1)),
    reason_code VARCHAR(16)
        CHECK (
            reason_code IS NULL OR reason_code IN
            ('helpful', 'incorrect', 'incomplete', 'outdated', 'other')
        ),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (history_event_id, user_id)
        REFERENCES query_history_events(id, user_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_private_feedback_history
    ON private_query_feedback(history_event_id);

CREATE INDEX IF NOT EXISTS idx_private_feedback_user
    ON private_query_feedback(user_id);
