from flask_cors import CORS
from project import create_app

app = create_app()
CORS(app)
#docker run --name podrab-pg -p 5432:5432 -e POSTGRES_PASSWORD=zilant116 -e POSTGRES_DB=podrabotai -d postgres:17
if __name__ == '__main__':
    # context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    # context.load_cert_chain('cert.pem', 'key.pem')
    app.run(host="0.0.0.0", port=5000)
