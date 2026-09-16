from fastapi.testclient import TestClient
from src.main import App
import fakeredis, pytest, sys

APIclient = TestClient(App)

@pytest.fixture(name="redis_mock", autouse=True)
async def mock_redis(monkeypatch):
    fake_client = fakeredis.FakeAsyncRedis(decode_responses=True)
    monkeypatch.setattr("src.redis_conf.redis_client", fake_client)
    if 'src.main' in sys.modules:
        monkeypatch.setattr(sys.modules["src.main"], "redis_client", fake_client)
    return fake_client


def test_metodo_get_pokemons_retorna_ok():
    resposta = APIclient.get(
        '/pokemons'
    )
    assert resposta.status_code == 200
    assert "rattata" in resposta.json()["resultado"]["Pokemons"]

def test_metodo_get_pokemon_id_retorna_ok():
    resposta = APIclient.get(
        '/pokemons/479'
    )
    assert resposta.status_code == 200
    assert resposta.json()["Pokemon"]["nome"] == "rotom"

def test_metodo_get_pokemons_paginacao():
    resposta1 = APIclient.get(
        '/pokemons'
    )
    assert resposta1.json()["resultado"]["Page"] == 1
    assert resposta1.json()["resultado"]["Limit"] == 20
    resposta2 = APIclient.get(
        'pokemons?page=5&limit=25'
    )
    assert resposta2.json()["resultado"]["Page"] == 5
    assert len(resposta2.json()["resultado"]["Pokemons"]) == 25

def test_metodo_get_pokemons_paginacao_erro():
    resposta1 = APIclient.get(
        '/pokemons?page=0'
    )
    assert resposta1.status_code == 400
    assert resposta1.json()['detail'] == "Página ou Limite estão inválidos!"
    resposta2 = APIclient.get(
        '/pokemons?limit=-5'
    )
    assert resposta2.status_code == 400
    assert resposta2.json()['detail'] == "Página ou Limite estão inválidos!"

def test_metodo_get_pokemons_id():
    resposta = APIclient.get(
        '/pokemons/4799'
    )
    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "Id inválido! Pokemon não encontrado."