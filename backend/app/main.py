from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import auth, clients, keywords, mentions, dashboard, alerts

# Creates tables on startup if they don't exist yet (fine for a small pilot;
# use a real migration tool like Alembic once this grows past a few clients).
Base.metadata.create_all(bind=engine)

app = FastAPI(title="PR Media Monitoring Tool", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this to your frontend's exact URL once deployed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(clients.router)
app.include_router(keywords.router)
app.include_router(mentions.router)
app.include_router(dashboard.router)
app.include_router(alerts.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
