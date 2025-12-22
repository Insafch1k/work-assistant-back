from flask_cors import CORS
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
from loguru import logger

from extensions import socketio
from project import create_app

app = create_app()
CORS(app)
#docker run --name podrab-pg -p 5432:5432 -e POSTGRES_PASSWORD=zilant116 -e POSTGRES_DB=podrabotai -d postgres:17
# if __name__ == '__main__':
#     # context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
#     # context.load_cert_chain('cert.pem', 'key.pem')
#     logger.info('Сервер успешно запущен')
#     #socketio.run(app,host="localhost", port=5000)
#     server = pywsgi.WSGIServer(('0.0.0.0', 5000), app, handler_class=WebSocketHandler)
#     server.serve_forever()