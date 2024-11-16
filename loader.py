from db.mysql_db import Database
from data.config import HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI


db = Database(host=HOST, 
              user=MYSQL_USER, 
              password=MYSQL_PASSWORD, 
              database=MYSQL_DATABASE)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Bu yerda "*" o'rniga frontend domeningizni kiritsangiz xavfsizroq bo'ladi
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)