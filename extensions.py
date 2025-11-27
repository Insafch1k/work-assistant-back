from flask_socketio import SocketIO

# единый экземпляр SocketIO для всего проекта
socketio = SocketIO(cors_allowed_origins="*", async_mode="gevent")
