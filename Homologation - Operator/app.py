from app import app, socketio

if __name__ == '__main__':
    socketio.thread = None
    socketio.run(app, port=5001, debug=True)