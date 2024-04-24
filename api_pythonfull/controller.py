from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Pessoa, Tokens
from secrets import token_hex
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from hashlib import sha256
from datetime import datetime

app = FastAPI()

# cors fastapi (policy) → https://fastapi.tiangolo.com/tutorial/cors/
# origins = ['*'] # '*' → todos podem fazer requisição
origins = 'http://127.0.0.1:5001'

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
  token_existe = session.query(Tokens).filter_by(token=token_LS).all()
  if token_existe:
    expirou = datetime.now() - token_existe[0].data
    if expirou.days <= 3: # verifica se faz mais de 3 dias desde o último acesso
      token_existe[0].data = datetime.now()  # renova a validade do token
      session.commit()
      return {'msg': 0} # permite o acesso do usuário sem fazer login
  return {'msg': 1} # apaga o token do localStorage e o usuário precisa fazer um novo login

    
@app.post('/cadastro')
def cadastro(usuario: str, email: str, senha: str):
  if len(senha) < 6:
    return {'msg': 1}
  
  senha = sha256(senha.encode()).hexdigest()
  session = conectaBanco()
  usuario_existe = session.query(Pessoa).filter_by(email=email, senha=senha).all()

  if usuario_existe:
    return {'msg': 2}
  
  try:
    novo_usuario = Pessoa(usuario=usuario,
                          email=email,
                          senha=senha)
    session.add(novo_usuario)
    session.commit()
    return {'msg': 0}
  except Exception as erro:
    return {'msg': 3, 'erro': erro}
  

@app.post('/login')
def login(email: str, senha: str):
  senha = sha256(senha.encode()).hexdigest()
  session = conectaBanco()
  usuario_existe = session.query(Pessoa).filter_by(email=email, senha=senha).all()

  if usuario_existe:
    while True:
      token = token_hex(25)
      token_existe = session.query(Tokens).filter_by(token=token).all()
      if not token_existe:
        pessoa_existe = session.query(Tokens).filter_by(id_pessoa=usuario_existe[0].id).all()
        if not pessoa_existe:
          addToken = Tokens(id_pessoa=usuario_existe[0].id, token=token)
          session.add(addToken)
        else:
          pessoa_existe[0].token = token
        session.commit()
        break
    return {'msg': 0, 'nome': usuario_existe[0].usuario, 'token': token}
  
  else:
    return {'msg': 1}
    

if __name__ == '__main__':
  uvicorn.run('controller:app', port=5000, reload=True, access_log=False)