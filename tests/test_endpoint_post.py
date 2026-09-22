def test_metodo_post_pokemon_retorna_ok(client):
    data = {
    "nome": "teste",
    "altura": 40,
    "peso": 23,
    "tipos":["Eletrico","Sombrio"]
    }
    resposta = client.post('/pokemon', json=data)

    assert resposta.status_code == 201
    assert resposta.json()["message"] == "teste adicionado aos registros com sucesso!"

def test_metodo_post_pokemon_retorna_erro(client,pokemon_salvo):
    data = {
    "nome": "teste",
    "altura": 40,
    "peso": 23,
    "tipos":["Eletrico","Sombrio"]
    }
    resposta = client.post('/pokemon', json=data)

    assert resposta.status_code == 400
    assert resposta.json()["detail"] == "Esse Pokemon já existe nos registros!"

def test_metodo_post_pokemon_retorna_erro_tipo(client):
    data = {
        "nome": 444,
        "altura": "40",
        "peso": 23,
        "tipos":["Eletrico","Sombrio"]
    }
    resposta = client.post('/pokemon', json=data)

    assert resposta.status_code == 422