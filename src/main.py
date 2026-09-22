from fastapi import FastAPI, HTTPException, Depends
from src.db_conf import session_db, PokemonDB
from src.redis_conf import redis_client, salvar_no_cache, deletar_cache
from sqlalchemy.orm import Session
from pydantic import BaseModel
import json


app = FastAPI(
    title="API-Pokemon",
    description="API para catalogar informações sobre pokemons permitindo listar, buscar, adicionar, editar e excluir informações.",
    version="1.0.0",
    contact={
        "name":"Pedro Américo",
        "email":"pedrobravo1406@gmail.com"
    },
)

class Pokemon(BaseModel):
    _id: int
    nome: str
    altura: int
    peso: int
    tipos: list[str]

@app.get("/pokemons", tags=["Buscar e Listar"], description="Busca um lista de pokemons registrados no banco de dados, com parâmetros de 'page' para o número da página e 'limit' para a quantidade de pokemons exibidos por página")
async def get_lista_pokemons(page: int = 1, limit: int = 20, db: Session = Depends(session_db)):
    cache_key = "pokemons"
    cached = await redis_client.get(cache_key)
    if cached is not None:
        return json.loads(cached)
    if page <= 0 or limit < 1:
        raise HTTPException(status_code=400, detail="Página ou Limite estão inválidos!")
    pokemons = db.query(PokemonDB).offset((page - 1) * (limit)).limit(limit).all()
    if not pokemons:
        return {"message":"Nenhum Pokemon registrado!"}
    
    total_pokemons = db.query(PokemonDB).count()
    lista_pokemons = [{"id": pokemon._id, "nome": pokemon.nome} for pokemon in pokemons]
    resposta = {
        "page": page,
        "limit": limit,
        "Total": total_pokemons,
        "Pokemons": lista_pokemons
    }
    await salvar_no_cache(resposta, cache_key)
    return resposta

@app.get("/pokemon/{id}", tags=["Buscar e Listar"], description="Busca um pokemon específico registrado no banco de dados de acordo com seu id, basta passar o id como parâmetro.")
async def get_pokemon_por_id(id: int, db: Session = Depends(session_db)):
    cache_key = f"pokemon:{id}"
    cached = await redis_client.get(cache_key)
    if cached is not None:
        return json.loads(cached)
    pokemon = db.query(PokemonDB).filter(PokemonDB._id == id).first()
    if not pokemon:
        raise HTTPException(status_code=404,detail="Pokemon desejado não encontrado!")
    Resposta = {f"{pokemon.nome}": {"id":pokemon._id, "altura":pokemon.altura, "peso":pokemon.peso, "tipos":pokemon.tipos}}
    await salvar_no_cache(Resposta, cache_key)
    return Resposta
    
@app.post("/pokemon", status_code=201, tags=["Criar e Editar"], description="Adiciona um pokemon aos registros do banco de dados, basta passar as informações via Body da requisição sendo elas: nome, altura, peso, tipos(lista com os tipos)")
async def post_pokemon(pokemon: Pokemon, db: Session = Depends(session_db)):
    db_pokemon = db.query(PokemonDB).filter(PokemonDB.nome == pokemon.nome).first()
    if db_pokemon:
        raise HTTPException(status_code=400, detail="Esse Pokemon já existe nos registros!")
    new_pokemon = PokemonDB(nome = pokemon.nome, altura = pokemon.altura, peso = pokemon.peso, tipos=pokemon.tipos)
    db.add(new_pokemon)
    db.commit()
    db.refresh(new_pokemon)
    cache_key = "pokemons"
    await deletar_cache(cache_key)
    return {"message": f"{pokemon.nome} adicionado aos registros com sucesso!"}

@app.put("/pokemon/{id}", tags=["Criar e Editar"], description="Atualiza o registro de um pokemon ja existente no banco de dados atrazes do seu id, basta passar o id como parâmetro e as novas informações via Body da requisição.")
async def put_pokemon_por_id(pokemon: Pokemon, id: int, db: Session = Depends(session_db)):
    pokemon_db = db.query(PokemonDB).filter(PokemonDB._id == id).first()
    if not pokemon_db:
        raise HTTPException(status_code=404, detail="Pokemon desejado não encontrado!")
    pokemon_db.nome = pokemon.nome
    pokemon_db.altura = pokemon.altura
    pokemon_db.peso = pokemon.peso
    pokemon_db.tipos = pokemon.tipos
    db.commit()
    db.refresh(pokemon_db)
    await deletar_cache("pokemons")
    await deletar_cache(f"pokemon:{id}")
    return {"message":"As informações do Pokemon foram atualizadas!"}

@app.delete("/pokemon/{id}", tags=["Criar e Editar"], description="Deleta um pokemon dos registros do banco de dados, basta passar o id como parâmetro.")
async def delete_pokemon_por_id(id: int, db: Session = Depends(session_db)):
    pokemon_db = db.query(PokemonDB).filter(PokemonDB._id == id).first()
    if not pokemon_db:
        raise HTTPException(status_code=404, detail="Pokemon desejado não encontrado!")
    db.delete(pokemon_db)
    db.commit()
    await deletar_cache("pokemons")
    await deletar_cache(f"pokemon:{id}")
    return {"message":"Pokemon foi deletado com sucesso!"}

# ENDPOINT para desenvolvimento. Mostra os itens no cache atual do redis

# @app.get("/cache/debug", tags=["Debug"], description="Mostra os itens no cache atual do redis")
# async def ver_cache():
#    chaves = await redis_client.keys("pokemon:*")
#    Pokemons = []
#    for chave in chaves:
#        valor = await redis_client.get(chave)
#        ttl = await redis_client.ttl(chave)
#        Pokemons.append({"chave": chave, "valor": json.loads(valor), "ttl": ttl})
#    lista_pokemons = await redis_client.get("pokemons")
#    Lista = {
#        "valor": json.loads(lista_pokemons),
#        "ttl": await redis_client.ttl("pokemons"),
#    }
#    return [Lista, Pokemons]