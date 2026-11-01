from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import create_sqlite_engine, get_db, init_db
from app.core.security import get_current_user
from app.main import app
from app.modules.auth.model import User
from app.modules.history.model import QueryHistoryEvent
from app.modules.history.services import record_query_event
from app.modules.query.services import NormalizedDatabaseUnavailable


class TestPrivateQueryHistory:
    def setup_method(self) -> None:
        self.engine = create_sqlite_engine("sqlite:///:memory:")
        init_db(self.engine)
        self.db = Session(self.engine)
        self.user = User(
            username="history-user",
            email="history@example.test",
            password_hash="not-used",
        )
        self.other_user = User(
            username="other-history-user",
            email="other-history@example.test",
            password_hash="not-used",
        )
        self.db.add_all([self.user, self.other_user])
        self.db.commit()
        self.db.refresh(self.user)
        self.db.refresh(self.other_user)

        def test_db():
            yield self.db

        app.dependency_overrides[get_db] = test_db
        app.dependency_overrides[get_current_user] = lambda: self.user
        self.client = TestClient(app)
        self.client.__enter__()

    def teardown_method(self) -> None:
        self.client.__exit__(None, None, None)
        app.dependency_overrides.clear()
        self.db.close()
        self.engine.dispose()

    def test_history_requires_authentication(self) -> None:
        del app.dependency_overrides[get_current_user]

        response = self.client.get("/history")

        assert response.status_code == 401

    def test_lists_only_authenticated_user_without_raw_content(self) -> None:
        own = record_query_event(
            self.db,
            user_id=self.user.id,
            status="success",
            question_length=42,
            route="structured",
            entity="contrato",
            result_count=3,
        )
        record_query_event(
            self.db,
            user_id=self.other_user.id,
            status="success",
            question_length=99,
            route="rag",
            entity="documento",
            result_count=1,
        )

        response = self.client.get("/history")

        assert response.status_code == 200
        payload = response.json()
        assert payload["total"] == 1
        assert payload["items"][0]["id"] == own.id
        assert payload["items"][0]["question_length"] == 42
        item = payload["items"][0]
        for forbidden in ("question", "pergunta", "answer", "resposta", "user_id"):
            assert forbidden not in item

    def test_expired_events_are_removed_before_listing(self) -> None:
        old_now = (
            datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=366)
        )
        expired = record_query_event(
            self.db,
            user_id=self.user.id,
            status="success",
            question_length=10,
            now=old_now,
        )

        response = self.client.get("/history")

        assert response.status_code == 200
        assert response.json()["total"] == 0
        assert self.db.get(QueryHistoryEvent, expired.id) is None

    def test_cannot_delete_another_users_event(self) -> None:
        event = record_query_event(
            self.db,
            user_id=self.other_user.id,
            status="success",
            question_length=12,
        )

        response = self.client.delete(f"/history/{event.id}")

        assert response.status_code == 404
        assert self.db.get(QueryHistoryEvent, event.id) is not None

    def test_deletes_all_events_only_for_authenticated_user(self) -> None:
        for user_id in (self.user.id, self.other_user.id):
            record_query_event(
                self.db,
                user_id=user_id,
                status="success",
                question_length=8,
            )

        response = self.client.delete("/history")

        assert response.status_code == 204
        assert self.db.scalar(
            select(func.count(QueryHistoryEvent.id)).where(
                QueryHistoryEvent.user_id == self.user.id
            )
        ) == 0
        assert self.db.scalar(
            select(func.count(QueryHistoryEvent.id)).where(
                QueryHistoryEvent.user_id == self.other_user.id
            )
        ) == 1

    def test_adaptive_query_records_only_minimal_metadata(self) -> None:
        question = "Olá, bom dia!"
        response = self.client.post(
            "/query/ask",
            json={"pergunta": question},
        )

        assert response.status_code == 200
        history_id = response.json()["history_id"]
        event = self.db.get(QueryHistoryEvent, history_id)
        assert event is not None
        assert event.user_id == self.user.id
        assert event.route is None
        assert event.question_length == len(question)
        assert not hasattr(event, "question")
        assert not hasattr(event, "answer")

    def test_adaptive_query_records_controlled_error(self) -> None:
        with patch(
            "app.modules.query.routes.executar_consulta_adaptativa_api",
            side_effect=NormalizedDatabaseUnavailable("payload privado"),
        ):
            response = self.client.post(
                "/query/ask",
                json={"pergunta": "CPF sintético 000.000.000-00"},
            )

        assert response.status_code == 503
        event = self.db.scalar(
            select(QueryHistoryEvent)
            .where(QueryHistoryEvent.user_id == self.user.id)
            .order_by(QueryHistoryEvent.id.desc())
        )
        assert event is not None
        assert event.status == "error"
        assert event.question_length == len("CPF sintético 000.000.000-00")

    def test_rejects_free_text_in_technical_identifiers(self) -> None:
        for field, value in (
            ("route", "CPF 000.000.000-00"),
            ("entity", "resposta privada"),
            ("status", "token-secreto"),
        ):
            values = {
                "route": "structured",
                "entity": "contrato",
                "status": "success",
            }
            values[field] = value
            try:
                record_query_event(
                    self.db,
                    user_id=self.user.id,
                    question_length=10,
                    **values,
                )
            except ValueError:
                self.db.rollback()
            else:
                raise AssertionError(f"{field} aceitou texto livre")
