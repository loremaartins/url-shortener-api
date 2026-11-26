import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_urls.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_create_and_redirect_short_url():
    # 1. Criar URL encurtada
    response = client.post("/shorten", json={"target_url": "https://python.org"})
    assert response.status_code == 201
    data = response.json()
    assert data["target_url"] == "https://python.org"
    assert data["clicks"] == 0
    short_code = data["short_code"]

    # 2. Acessar URL encurtada (redirecionamento 307)
    redirect_res = client.get(f"/{short_code}", follow_redirects=False)
    assert redirect_res.status_code == 307
    assert redirect_res.headers["location"] == "https://python.org"

    # 3. Verificar se o contador de cliques subiu para 1
    stats_res = client.get(f"/stats/{short_code}")
    assert stats_res.status_code == 200
    assert stats_res.json()["clicks"] == 1


def test_invalid_url_returns_422():
    response = client.post("/shorten", json={"target_url": "not-a-valid-url"})
    assert response.status_code == 422


def test_nonexistent_short_code_returns_404():
    response = client.get("/stats/inexistente123")
    assert response.status_code == 404


def test_delete_short_url():
    create_res = client.post("/shorten", json={"target_url": "https://tiangolo.com"})
    short_code = create_res.json()["short_code"]

    delete_res = client.delete(f"/urls/{short_code}")
    assert delete_res.status_code == 204

    get_res = client.get(f"/stats/{short_code}")
    assert get_res.status_code == 404
