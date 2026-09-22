import pytest, json
def test_metodo_get_pokemons_retorna_ok_db_vazio(client):
    resposta = client.get("/pokemons")

    assert resposta.status_code == 200
    assert resposta.json()["message"] == "Nenhum Pokemon registrado!"

def test_metodo_get_pokemons_retorna_ok_db_ocupado(client, pokemon_salvo,):
    resposta = client.get("/pokemons")

    assert resposta.status_code == 200
    assert resposta.json()["Pokemons"] == [{"id": 1, "nome": "teste"}]

def test_metodo_get_pokemons_paginacao_limit_erro(client):
    resposta = client.get("/pokemons?page=1&limit=-1")
    
    assert resposta.status_code == 400
    assert resposta.json()["detail"] == "Página ou Limite estão inválidos!"

def test_metodo_get_pokemons_paginacao_page_erro(client):
    resposta = client.get("/pokemons?page=0&limit=20")
    assert resposta.status_code == 400
    assert resposta.json()["detail"] == "Página ou Limite estão inválidos!"

def test_metodo_get_pokemons_paginacao_ok(client, pokemon_salvo):
    resposta = client.get("/pokemons?page=1&limit=10")

    assert resposta.status_code == 200
    assert resposta.json()["limit"] == 10
    assert resposta.json()["page"] == 1

def test_metodo_get_pokemons_paginacao_page_ok(client, pokemon_salvo):
    resposta = client.get("/pokemons?page=2&limit=10")

    assert resposta.status_code == 200
    assert resposta.json()["message"] == "Nenhum Pokemon registrado!"

def test_metodo_get_pokemon_por_id_retorna_ok(client,pokemon_salvo):
    resposta = client.get("/pokemon/1")

    assert resposta.status_code == 200
    assert resposta.json() == {"teste": {"id":1, "altura":40, "peso":20, "tipos":['Elétrico']}}

def test_metodo_get_pokemon_por_id_retorna_erro(client,pokemon_salvo):
    resposta = client.get("/pokemon/2")

    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "Pokemon desejado não encontrado!"

@pytest.mark.asyncio
async def test_metodo_get_pokemons_cache_hit(client,redis_mock):
    cache_key = "pokemons"
    dados_mock = {"id":10, "nome":"teste"}
    await redis_mock.set(cache_key, json.dumps(dados_mock))
    resposta = client.get("/pokemons")

    assert resposta.json() == dados_mock

@pytest.mark.asyncio
async def test_metodo_get_pokemons_cache_miss(client,pokemon_salvo, redis_mock):
    cache_key = "pokemons"
    cache_velho = await redis_mock.get(cache_key)
    assert cache_velho is None
    resposta = client.get("/pokemons")
    assert resposta.json()["Pokemons"] == [{"id": 1, "nome": "teste"}]
    cache_novo = await redis_mock.get(cache_key)
    assert cache_novo is not None

@pytest.mark.asyncio
async def test_metodo_get_pokemon_por_id_cache_hit(client,redis_mock):
    dados_mock = {"id":10, "nome":"teste"}
    await redis_mock.set("pokemon:10", json.dumps(dados_mock))
    resposta = client.get("/pokemon/10")

    assert resposta.json() == dados_mock

@pytest.mark.asyncio
async def test_metodo_get_pokemon_por_id_cache_miss(client,pokemon_salvo,redis_mock):
    cache_key = "pokemon:1"
    cache_velho = await redis_mock.get(cache_key)
    assert cache_velho is None
    resposta = client.get("/pokemon/1")
    assert resposta.json() == {"teste": {"id":1, "altura":40, "peso":20, "tipos":['Elétrico']}}
    cache_novo = await redis_mock.get(cache_key)
    assert cache_novo is not None