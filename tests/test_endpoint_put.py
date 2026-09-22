def test_metodo_put_pokemon_retorna_ok(client,pokemon_salvo):
    data = {
    "nome": "teste",
    "altura": 40,
    "peso": 23,
    "tipos":["Elétrico","Sombrio"]
    }
    resposta = client.put('/pokemon/1', json=data)

    assert resposta.status_code == 200
    assert resposta.json()["message"] == "As informações do Pokemon foram atualizadas!"

def test_metodo_put_pokemon_retorna_erro(client,pokemon_salvo):
    data = {
    "nome": "teste",
    "altura": 40,
    "peso": 23,
    "tipos":["Elétrico","Sombrio"]
    }
    resposta = client.put('/pokemon/2', json=data)

    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "Pokemon desejado não encontrado!"

def test_metodo_put_pokemon_retorna_erro_tipo(client, pokemon_salvo):
    data = {
        "nome": 444,
        "altura": "40",
        "peso": 23,
        "tipos":["Elétrico","Sombrio"]
    }
    resposta = client.put('/pokemon/1', json=data)

    assert resposta.status_code == 422