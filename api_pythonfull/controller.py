from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Pessoa, Tokens
from secrets import token_hex
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from hashlib import sha256
from datetime import datetime, timedelta

app = FastAPI()

# cors fastapi (policy) → https://fastapi.tiangolo.com/tutorial/cors/
# origins = ['*'] # '*' → todos podem fazer requisição
origins = ['http://127.0.0.1:5001', 'http://127.0.0.1:5002', 'http://127.0.0.1:5003']

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


@app.post('/token')
def token(token_LS: str):
  session = conectaBanco()
  tokenExiste = session.query(Tokens).filter_by(token=token_LS).all()
  if tokenExiste:
    expirou = datetime.now() - tokenExiste[0].data
    if expirou.days <= 3: # verifica se faz mais de 3 dias desde o último acesso
      tokenExiste[0].data = datetime.now()  # renova a validade do token
      session.commit()
      return {'msg': 0} # permite o acesso do usuário sem fazer login
  return {'msg': 1} # apaga o token do localStorage e o usuário precisa fazer um novo login

    
@app.post('/cadastro')
def cadastro(usuario: str, email: str, senha: str):
  if len(senha) < 6:
    return {'msg': 1}
  
  senha = sha256(senha.encode()).hexdigest()
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
    return {'msg': 3, 'erro': erro}
  

@app.post('/login')
def login(email: str, senha: str):

  senha = sha256(senha.encode()).hexdigest()
  session = conectaBanco()
  usuarioExiste = session.query(Pessoa).filter_by(email=email, senha=senha).all()

  if usuarioExiste:
    while True:
      token = token_hex(25)
      tokenExiste = session.query(Tokens).filter_by(token=token).all()
      if not tokenExiste:
        pessoaExiste = session.query(Tokens).filter_by(id_pessoa=usuarioExiste[0].id).all()
        if not pessoaExiste:
          addToken = Tokens(id_pessoa=usuarioExiste[0].id, token=token)
          session.add(addToken)
          session.commit()
        else:
            pessoaExiste[0].token = token
            session.commit()
        break
    return {'msg': 0, 'nome': usuarioExiste[0].usuario, 'token': pessoaExiste[0].token}
  
  else:
    return {'msg': 1}
    

if __name__ == '__main__':
  uvicorn.run('controller:app', port=5000, reload=True, access_log=False)