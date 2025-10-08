from flask_cors import CORS
from project import create_app
import threading
import time

app = create_app()
CORS(app)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)