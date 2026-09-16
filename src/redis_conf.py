import redis, json, os
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
if REDIS_HOST == "redis":
    redis_client = redis.asyncio.Redis(host=REDIS_HOST,port=6379, db=0, decode_responses=True)
else:
    redis_client = redis.asyncio.from_url(REDIS_HOST, decode_responses=True)

async def salvar_no_cache(pokemon: dict, cache_key: str):
    dados_json = json.dumps(pokemon)
    await redis_client.set(cache_key, dados_json, ex=300)