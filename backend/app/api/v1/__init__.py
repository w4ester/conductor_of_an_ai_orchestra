from fastapi import APIRouter

api_router = APIRouter()

# Import and include all routers
from app.api.v1 import auth, users, prompts, tools, documents, vector_dbs, embeddings, rag_systems, models

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(prompts.router)
api_router.include_router(tools.router)
api_router.include_router(documents.router)
api_router.include_router(vector_dbs.router)
api_router.include_router(embeddings.router)
api_router.include_router(rag_systems.router)
api_router.include_router(models.router)
