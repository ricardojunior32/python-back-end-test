from fastapi import FastAPI
from app.core.database import Base, engine
from app.series.routes import router as series_router

app = FastAPI()

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

app.include_router(series_router)

@app.get("/")
def root():
    return {"message": "API funcionando!"}