from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import health, process_image, root

app = FastAPI(title="All Things Ones API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(process_image.router, tags=["processing"])
app.include_router(root.router, tags=["root"])
