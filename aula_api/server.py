def app(amb, start_response):
  arq = open('index.html', 'rb')
  data = arq.read()
  status = '200 ok'
  response_headers = [('Content-type', 'text/html')]
  start_response(status, response_headers)
  return [data]