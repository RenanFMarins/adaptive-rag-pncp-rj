from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import create_sqlite_engine, get_db, init_db
from app.core.security import get_current_user
from app.main import app
from app.modules.auth.model import User
from app.modules.feedback.model import PrivateQueryFeedback
from app.modules.history.services import record_query_event


class TestPrivateFeedbackRoutes:
    def setup_method(self) -> None:
        self.engine = create_sqlite_engine("sqlite:///:memory:")
        init_db(self.engine)
        self.db = Session(self.engine)
        self.user = User(
            username="feedback-user",
            email="feedback@example.test",
            password_hash="not-used",
        )
        self.other_user = User(
            username="other-feedback-user",
            email="other-feedback@example.test",
            password_hash="not-used",
        )
        self.db.add_all([self.user, self.other_user])
        self.db.commit()
        self.db.refresh(self.user)
        self.db.refresh(self.other_user)
        self.own_event = record_query_event(
            self.db,
            user_id=self.user.id,
            status="success",
            question_length=20,
            route="structured",
            entity="contrato",
            result_count=2,
        )
        self.other_event = record_query_event(
            self.db,
            user_id=self.other_user.id,
            status="success",
            question_length=30,
            route="rag",
            entity="documento",
            result_count=1,
        )

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

    def test_feedback_requires_authentication(self) -> None:
        del app.dependency_overrides[get_current_user]

        response = self.client.post(
            "/feedback",
            json={"history_id": self.own_event.id, "rating": 1},
        )

        assert response.status_code == 401

    def test_creates_and_reads_feedback_without_user_identifier(self) -> None:
        response = self.client.post(
            "/feedback",
            json={
                "history_id": self.own_event.id,
                "rating": 1,
                "reason_code": "helpful",
            },
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["history_id"] == self.own_event.id
        assert payload["rating"] == 1
        assert payload["reason_code"] == "helpful"
        assert "user_id" not in payload

        read = self.client.get(f"/feedback/{self.own_event.id}")
        assert read.status_code == 200
        assert read.json() == payload

    def test_second_submission_updates_single_feedback(self) -> None:
        first = self.client.post(
            "/feedback",
            json={"history_id": self.own_event.id, "rating": 1},
        )
        second = self.client.post(
            "/feedback",
            json={
                "history_id": self.own_event.id,
                "rating": -1,
                "reason_code": "incomplete",
            },
        )

        assert first.status_code == second.status_code == 200
        assert first.json()["id"] == second.json()["id"]
        assert second.json()["rating"] == -1
        assert self.db.scalar(select(func.count(PrivateQueryFeedback.id))) == 1

    def test_rejects_feedback_for_another_users_history(self) -> None:
        response = self.client.post(
            "/feedback",
            json={"history_id": self.other_event.id, "rating": 1},
        )

        assert response.status_code == 404
        assert self.db.scalar(select(func.count(PrivateQueryFeedback.id))) == 0

    def test_rejects_feedback_for_expired_history(self) -> None:
        expired = record_query_event(
            self.db,
            user_id=self.user.id,
            status="success",
            question_length=5,
            now=(
                datetime.now(timezone.utc).replace(tzinfo=None)
                - timedelta(days=366)
            ),
        )

        response = self.client.post(
            "/feedback",
            json={"history_id": expired.id, "rating": 1},
        )

        assert response.status_code == 404

    def test_database_rejects_mismatched_history_owner(self) -> None:
        self.db.add(
            PrivateQueryFeedback(
                history_event_id=self.other_event.id,
                user_id=self.user.id,
                rating=1,
                reason_code="helpful",
            )
        )

        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
        else:
            raise AssertionError("SQLite aceitou feedback de outro usuário")

    def test_rejects_free_text_and_invalid_rating(self) -> None:
        invalid_payloads = (
            {
                "history_id": self.own_event.id,
                "rating": 1,
                "comment": "conteúdo privado",
            },
            {
                "history_id": self.own_event.id,
                "rating": 0,
            },
            {
                "history_id": self.own_event.id,
                "rating": -1,
                "reason_code": "texto livre",
            },
        )
        for payload in invalid_payloads:
            response = self.client.post("/feedback", json=payload)
            assert response.status_code == 422

    def test_deletes_only_owned_feedback(self) -> None:
        created = self.client.post(
            "/feedback",
            json={"history_id": self.own_event.id, "rating": 1},
        )
        assert created.status_code == 200

        response = self.client.delete(f"/feedback/{self.own_event.id}")

        assert response.status_code == 204
        assert self.db.scalar(select(func.count(PrivateQueryFeedback.id))) == 0
        assert self.client.get(f"/feedback/{self.own_event.id}").status_code == 404

    def test_feedback_is_deleted_with_history_event(self) -> None:
        created = self.client.post(
            "/feedback",
            json={"history_id": self.own_event.id, "rating": 1},
        )
        assert created.status_code == 200

        deleted = self.client.delete(f"/history/{self.own_event.id}")

        assert deleted.status_code == 204
        assert self.db.scalar(select(func.count(PrivateQueryFeedback.id))) == 0
