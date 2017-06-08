from flask import Flask, render_template
from flask.ext.socketio import SocketIO, emit
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
