def test_metodo_delete_pokemon_retorna_ok(client, pokemon_salvo):
    resposta = client.delete('/pokemon/1')

    assert resposta.status_code == 200
    assert resposta.json()["message"] == "Pokemon foi deletado com sucesso!"

def test_metodo_delete_pokemon_retorna_erro(client, pokemon_salvo):
    resposta = client.delete('/pokemon/2')

    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "Pokemon desejado não encontrado!"