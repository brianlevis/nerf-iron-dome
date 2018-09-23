# Nerf Iron Dome
![Turret](https://github.com/brianlevis/nerf-iron-dome/raw/master/turret.jpg)
## Contributors
[Brian Levis](https://github.com/brianlevis) • [Luciano Vinas](https://github.com/lucianovinas) • [Andrew Chan](https://github.com/theandrewchan)
## Summary
The aim of this project is to build a nerf turret that can do cool stuff. Cool stuff might include:
* Targeting a moving object (tennis ball?)
* Recognizing faces
* Being remote controlled
* Guarding an object
* Reenacting [this scene](https://www.youtube.com/watch?v=mrXfh4hENKs) from RoboCop

## Quick Start
### Running the Web Server
There is a python server that provides a live stream of the camera located at `server.py`. To run, do
1. Activate the virtual environment with `source env/bin/activate`.
2. `FLASK_APP=server.py flask run --host=0.0.0.0` from the project directory.

## Contributing
### Status
The turret has been constructed, and may be controlled via a USB Xbox 360 Controller. It's electronics are ~~spaghetti~~ no longer spaghetti.

The turret can track and attack faces, or an object of a certain color and size. Tracking is currently just done by moving the turret towards the target with movement and flywheel revving speed proportional to target distance.

If not running tracking code, the turret may be operated manually via Xbox controller, or keyboard input to a camera livestream webpage.
### TODO
Software:
* Improve object tracking techniques
* Add facial recognition
## Credits
Turret base inspired by Britt Michelsen's [Nerf Vulcan Sentry Gun](http://www.instructables.com/id/Nerf-Vulcan-Sentry-Gun/), Nerf RapidStrike [teardown guide](http://torukmakto4.blogspot.com/2013/10/standard-rapidstrike-illustrated-guide.html),
[xboxdrv python wrapper class](https://github.com/FRC4564/Xbox)

## Tech Documentation

### Hardware
Nerf RapidStrike with pusher and flywheel motors hooked up to 7.5V 100W power supply and 5V relay module. Super high torque HS-805BB servos hooked up to 6V 18W power supply. Arduino controls all actuators, and communicates over serial with Raspberry Pi. Raspberry Pi Camera v2 mounted on top of gun. Possibly will be mounted on drum tripod.

### Software
[Python Connector Design](https://docs.google.com/document/d/1Gke5QFeYasZ8_wYOghZAU99f_aja3h15VcXeIRREn2o/pub)

#### `nerf_turret`
All turret actuation is abstracted through the `nerf_turret` interface, which is importable as a python module. Do not use `v1_stable_controller_operation`, which is deprecated. The current interface contains the following functions:

##### `set_velocity(pan_velocity, tilt_velocity)`
**Parameters**
* `pan_velocity` - Integer in [-127, +127] indicating the horizontal angular velocity of the turret.
* `tilt_velocity` - Integer in [-127, +127] indicating the vertical angular velocity of the turret.
Note that if the arguments are not within the specified range, they will be truncated using a bitmask, so they should be clamped before calling if needed.

##### `move(pan_location, tilt_location)`
**Parameters**
* `pan_location` - Angle in [-700, +700] to set the turret horizontal rotation.
* `tilt_location` - Angle in [-300, +500] to set the turret vertical rotation.

##### `pan(position)`
**Parameters**
* `position` - Angle in [-700, +700] to set the turret horizontal rotation.

##### `tilt(position)`
**Parameters**
* `position` - Angle in [-300, +500] to set the turret vertical rotation.

##### `rev(rev_speed)`
**Parameters**
* `rev_speed` - Speed in [0, 200] to set the firing motor at.

##### `fire(num_shots)`
**Parameters**
* `num_shots` - Integer number of shots to fire.
