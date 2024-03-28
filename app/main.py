from dotenv import load_dotenv
from fastapi import FastAPI

# from app.db.database import engine
from app.router import user, hotel, attraction
import uvicorn
from app.config import settings
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()
app = FastAPI()

origins = ["http://localhost:3000"]
app.include_router(user.router)
app.include_router(hotel.router)
app.include_router(attraction.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def start():
    uvicorn.run(
        "app.main:app",
        host="localhost",
        port=settings.port,
        reload=False,
    )


if __name__ == "__main__":
    start()
