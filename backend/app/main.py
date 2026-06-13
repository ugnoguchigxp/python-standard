import time

import asgi  # type: ignore
from fastapi import FastAPI, Request
from workers import WorkerEntrypoint  # type: ignore

app = FastAPI(title="FastAPI Cloudflare Worker")


@app.get("/api/health/liveness")
async def liveness():
    return {"status": "ok", "timestamp": time.time()}


@app.get("/api/items")
async def list_items(request: Request):
    # Access D1 binding from request environment context
    env = request.scope.get("env")
    if not env or not hasattr(env, "DB"):
        return [{"id": 1, "title": "Local Mock Item", "description": "No D1 DB bound"}]

    db = env.DB
    result = await db.prepare("SELECT * FROM items").all()
    return result.results


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        return await asgi.fetch(app, request, self.env)
