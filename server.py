from flask import Flask, render_template, Response
from flask.ext.socketio import SocketIO, emit
from camera import Camera
app = Flask(__name__)

#
#
# See http://flask.pocoo.org/docs/0.12/quickstart/ for instructions on how to run this file.
# Quick run (in terminal): flask run --host=0.0.0.0
#
#

@app.route("/")
def serve():
    return render_template("index.html")

#-----------------------------------------------------------
# Video streaming functions
#-----------------------------------------------------------
# Create a generator for the images
def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
# Create the endpoint to return images
@app.route("/video_feed")
def video_feed():
    return Response(
        gen(Camera()),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )
#------------------------------------------------------------
#Websocket messages------------------------------------------
@socketio.on('connect')
def test_connect():
    print("CLIENT CONNECTED")

@socketio.on("action_code")
def print_client_version(message):
    print("received:" + message["code"]) #this is an example of a websocket message with a payload from client

# maybe define some handlers to write codes to serial on certain button presses?

@socketio.on('disconnect')
def test_disconnect():
    print('CLIENT DISCONNECTED')

#------------------------------------------------------------
