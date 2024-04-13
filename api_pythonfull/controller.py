from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Pessoa
from secrets import token_hex
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# cors fastapi (policy) → https://fastapi.tiangolo.com/tutorial/cors/
# origins = ['*'] # '*' → todos podem fazer requisição
origins = ['http://127.0.0.1:5002']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def conectaBanco():
  engine = create_engine('sqlite:///sqlite.db', echo=False)
  Session = sessionmaker(bind=engine)
  return Session()

@app.post('/cadastro')
def cadastro(usuario: str, email: str, senha: str):
  if len(senha) < 6:
    return {'msg': 1}
  
  session = conectaBanco()
  usuarioExiste = session.query(Pessoa).filter_by(email=email, senha=senha).all()

  if usuarioExiste:
    return {'msg': 2}

  try:
    novoUsuario = Pessoa(usuario=usuario,
                         email=email,
                         senha=senha)
    session.add(novoUsuario)
    session.commit()
    return {'msg': 0}
  except Exception as erro:
    return {'msg': 3, 'msg': erro}

if __name__ == '__main__':
  uvicorn.run('controller:app', port=5000, reload=True, access_log=False)