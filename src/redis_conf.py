import redis, json
redis_client = redis.asyncio.Redis(host="redis", port=6379, db=0, decode_responses=True)

async def salvar_no_cache(pokemon: dict, cache_key: str):
    dados_json = json.dumps(pokemon)
    await redis_client.set(cache_key, dados_json, ex=300)