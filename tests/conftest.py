import fakeredis, pytest, sys, os
os.environ["DATABASE_URL"] = "sqlite://"
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from src.main import app
from src.db_conf import Base, session_db, PokemonDB
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(name="session", scope="function")
def session_fixture():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(name="client")
def client_fixture(session):
    def override_db():
        try:
            yield session
        finally:
            pass
    app.dependency_overrides[session_db] = override_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture(name="redis_mock", autouse=True)
async def mock_redis(monkeypatch):
    fake_client = fakeredis.FakeAsyncRedis(decode_responses=True)
    monkeypatch.setattr("src.redis_conf.redis_client", fake_client)
    if "src.main" in sys.modules:
        monkeypatch.setattr(sys.modules["src.main"], "redis_client", fake_client)
    return fake_client

@pytest.fixture
def pokemon_salvo(session):
    novo_produto = PokemonDB(nome="teste", altura=40, peso=20, tipos=["Elétrico"])
    session.add(novo_produto)
    session.commit()
    session.refresh(novo_produto)
    return novo_produto