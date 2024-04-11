from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Pessoa
from secrets import token_hex
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

def conectaBanco():
  engine = create_engine('sqlite:///sqlite.db', echo=False)
  Session = sessionmaker(bind=engine)
  session = Session()
  return session

@app.post('/cadastro')
def cadastro(usuario: str, email: str, senha: str):
  ...