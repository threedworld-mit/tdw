from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


@app.route('/')
def index():
    return render_template("index.html")


@socketio.on('echo')
def my_event(message):
    print(message)
    emit('my response', {'data': 'got it!'})


if __name__ == '__main__':
    socketio.run(app)