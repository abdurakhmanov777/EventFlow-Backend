from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.http.http_requests import router as http_requests

def init_routers() -> FastAPI:
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
    app.include_router(http_requests)
    return app
