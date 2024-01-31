from app import app

if __name__ == '__main__':
    app.run(debug=True)


























    # rtsp_file_path = 'rtsp.json'
    # cap = None

    # server = pywsgi.WSGIServer(('127.0.0.1', 5000), app, handler_class=WebSocketHandler)
    # print("WebSocket server running on ws://127.0.0.1:5000")
    
    # try:
    #     server.serve_forever()
    # except KeyboardInterrupt:
    #     if cap:
    #         cap.release()
