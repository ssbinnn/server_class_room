from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('message') # 클라이언트로부터 'message' 이벤트를 받을 때 실행되는 함수
def handle_message(data):
    print('received message: ' + data)
    emit('response', 'This is a response')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
