from fastapi import FastAPI, HTTPException
from src.redis_conf import redis_client, salvar_no_cache
import httpx, json

App = FastAPI(
    title="API-Pokemon",
    description="API para buscar infomações de Pokemon",
    version="0.1.0",
    contact={
        "name":"Pedro Américo",
        "email":"pedrobravo1406@gmail.com"
    },
)

@App.get("/pokemons",
         description="Busca uma lista de pokemons em ordem de pokedex, com os parâmetros 'page' para o número da página e 'limit' para o limite de pokemons exibidos por página")
async def get_pokemons(page: int = 1, limit: int = 20):
    if page <= 0 or limit < 1:
        raise HTTPException(status_code=400, detail="Página ou Limite estão inválidos!")
    offset = page*limit-limit 
    async with httpx.AsyncClient() as client:
        resposta = await client.get(f'https://pokeapi.co/api/v2/pokemon?offset={offset}&limit={limit}')
        dados = resposta.json()
    lista = []
    for item in dados["results"]:
        lista.append(item["name"])
    return {"resultado": {
        "Total": dados["count"],
        "Page": page,
        "Limit": limit,
        "Pokemons": lista
    }}

@App.get("/pokemons/{id}",
         description="Busca um pokemon específico de acordo com o id/número da pokedex. Retorna informações sobre o tal pokemon pesquisado, como nome, altura, peso e tipos")
async def get_pokemon_id(id: int):
    cache_key = f"pokemon:{id}"
    cached = await redis_client.get(cache_key)
    if cached is not None:
        return json.loads(cached)
    
    async with httpx.AsyncClient() as client:
        resposta = await client.get(f"https://pokeapi.co/api/v2/pokemon/{id}")
        if resposta.status_code == 404:
            raise HTTPException(status_code=404, detail="Id inválido! Pokemon não encontrado.")
        dados = resposta.json()

    Pokemon = {
        "nome": dados["name"],
        "id": dados["id"],
        "altura": dados["height"],
        "peso": dados["weight"],
        "tipos": [type["type"]["name"] for type in dados["types"]],
        "sprites": {"Front":dados["sprites"]["front_default"],"Back":dados["sprites"]["back_default"]}
    }
    await salvar_no_cache(Pokemon, cache_key)
    return {"Pokemon": Pokemon}


# ENDPOINT para desenvilvimento. Mostra os itens no cache atual do redis

@App.get("/cache/debug")
async def ver_cache():
    chaves = await redis_client.keys("pokemon:*")
    Pokemons = []
    for chave in chaves:
        valor = await redis_client.get(chave)
        ttl = await redis_client.ttl(chave)
        Pokemons.append({"chave": chave, "valor": json.loads(valor), "ttl": ttl})
    return Pokemons