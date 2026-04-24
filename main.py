from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import redis.asyncio as aioredis
import json, time, logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Redis client (lazy init)
redis_client = None
@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client
    redis_client = aioredis.from_url("redis://localhost:6379", decode_responses=True)
    logger.info("Redis connection established")
    yield
    await redis_client.close()
app = FastAPI(
    title="FastAPI Async Microservice",
    description="High-performance async microservice by Sahil Apsunde",
    version="1.0.0",
    lifespan=lifespan
)
security = HTTPBearer()
# 
 In-memory store (replace with PostgreSQL in production) 
items_db = {}
item_counter = 1
# 
 Cache-aside helper 
async def get_cached(key: str):
    if redis_client:
        cached = await redis_client.get(key)
        if cached:
            logger.info(f"Cache HIT for key: {key}")
            return json.loads(cached)
    return None
async def set_cache(key: str, value: dict, ttl: int = 300):
    if redis_client:
        await redis_client.setex(key, ttl, json.dumps(value))
async def invalidate_cache(key: str):
    if redis_client:
        await redis_client.delete(key)
# 
 Routes 
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time(), "service": "fastapi-async-microservice"}
@app.get("/api/v1/items")
async def list_items():
    cache_key = "items:all"
    cached = await get_cached(cache_key)
    if cached:
        return {"data": cached, "source": "cache"}
    data = list(items_db.values())
    await set_cache(cache_key, data)
    return {"data": data, "source": "database"}
@app.post("/api/v1/items", status_code=201)
async def create_item(item: dict):
    global item_counter
    item["id"] = item_counter
    item["created_at"] = time.time()
    items_db[item_counter] = item
    item_counter += 1
    await invalidate_cache("items:all")
    logger.info(f"Created item {item['id']}")
    return item
@app.get("/api/v1/items/{item_id}")
async def get_item(item_id: int):
    cache_key = f"item:{item_id}"
    cached = await get_cached(cache_key)
    if cached:
        return {"data": cached, "source": "cache"}
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    await set_cache(cache_key, items_db[item_id])
    return {"data": items_db[item_id], "source": "database"}
@app.delete("/api/v1/items/{item_id}", status_code=204)
async def delete_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    del items_db[item_id]
    await invalidate_cache(f"item:{item_id}")
    await invalidate_cache("items:all")
    return None
