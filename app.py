# from gevent import monkey
# from gevent.pywsgi import WSGIServer
# monkey.patch_all()
from subwayappointment import app

if __name__ == '__main__':
    # http_server = WSGIServer(('0.0.0.0', int(5000)), app)
    # http_server.serve_forever()
    app.run(host='0.0.0.0', port=5000)