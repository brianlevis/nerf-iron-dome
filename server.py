from flask import Flask, render_template, Response
from flask_socketio import SocketIO, emit
from camera_pi import Camera
import nerf_turret

app = Flask(__name__, static_folder='public')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


#
#
# See http://flask.pocoo.org/docs/0.12/quickstart/ for instructions on how to run this file.
# Quick run (in terminal): FLASK_APP=server.py flask run --host=0.0.0.0
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
    emit('my response', {'data': 'Connected'})

@socketio.on("action_code")
def print_client_version(message):
    print("received:{}".format(message["code"])) #this is an example of a websocket message with a payload from client

@socketio.on("fire")
def fire():
    nerf_turret.fire(1)

@socketio.on("controller_state")
def handle_controller_state(message):
    # recv 10 times per second
    velocity_x = int(message["move_x"] * -127)
    velocity_y = int(message["move_y"] * 127)
    nerf_turret.set_velocity(velocity_x, velocity_y)
    if bool(message["rev"]):
        nerf_turret.rev(100)
    else:
        nerf_turret.rev(0)

@socketio.on("orientation_state")
def handle_orientation_state(message):
    # recv 10 times per second
    pan = int(message["pan"] * -700)
    tilt = int(message["tilt"] * 700)
    # clamp pan and tilt values
    if pan < -700:
        pan = -700
    elif pan > 700:
        pan = 700

    if tilt < -300:
        tilt = -300
    elif tilt > 500:
        tilt = 500
    nerf_turret.move(pan, tilt)

@socketio.on('disconnect')
def test_disconnect():
    print('CLIENT DISCONNECTED')

#------------------------------------------------------------

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0")
