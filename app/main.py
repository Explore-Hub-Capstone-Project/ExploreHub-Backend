from dotenv import load_dotenv
from fastapi import FastAPI

# from app.db.database import engine
from app.router import user, hotel, attraction
import uvicorn
from app.config import settings
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()
app = FastAPI()

origins = [
    "0.0.0.0:3000",
    "http://localhost:3000",
    # "http://ec2-3-15-144-73.us-east-2.compute.amazonaws.com",
    # "https://ec2-3-15-144-73.us-east-2.compute.amazonaws.com",
    # "https://www.explorehub.lol",
]
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
        host="0.0.0.0",
        port=settings.PORT,
        reload=True,
    )


if __name__ == "__main__":
    start()
