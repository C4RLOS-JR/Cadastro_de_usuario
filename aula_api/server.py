def app(amb, start_response):
  cadastro = open('cadastro.html', 'rb')
  login = open('login.html', 'rb')
  home = open('home.html', 'rb')
  if 'logar' in amb['PATH_INFO']:
    data = login.read()
  elif 'home' in amb['PATH_INFO']:
    data = home.read()
  else:
    data = cadastro.read()
  status = '200 ok'
  response_headers = [('Content-type', 'text/html')]
  start_response(status, response_headers)
    
  return [data]

# gunicorn server:app -b 127.0.0.1:5001