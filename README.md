# Nerf Iron Dome
![Turret](https://github.com/brianlevis/nerf-iron-dome/blob/master/turret.jpg)
## Contributors:
[Brian Levis](https://github.com/brianlevis) • [Luciano Vinas](https://github.com/lucianovinas) • [Andrew Chan](https://github.com/theandrewchan)
## Summary
The aim of this project is to build a nerf turret that can do cool stuff. Cool stuff might include:
* Targeting a moving object (tennis ball?)
* Recognizing faces
* Being remote controlled
* Guarding an object
* Reenacting [this scene](https://www.youtube.com/watch?v=mrXfh4hENKs) from RoboCop
## Status
The turret has been constructed, and may be controlled via a USB Xbox 360 Controller. It's electronics are spaghetti.
## TODO
Solder electronics, mount camera, do software. Also add pics/3D models to git.
## Credits
Turret base inspired by Britt Michelsen's [Nerf Vulcan Sentry Gun](http://www.instructables.com/id/Nerf-Vulcan-Sentry-Gun/), Nerf RapidStrike [teardown guide](http://www.instructables.com/id/Nerf-Vulcan-Sentry-Gun/),
[xboxdrv python wrapper class](https://github.com/FRC4564/Xbox)
## Tech
### Hardware
Nerf RapidStrike with pusher and flywheel motors hooked up to 7.5V@13.5A power supply and 5V relay module. Super high torque HS-805BB servos hooked up to 6V@3A power supply. Arduino controls all actuators, and communicates over serial with Raspberry Pi. Raspberry Pi Camera v2 mounted on top of gun. To be polished and elaborated. Possibly will be mounted on drum tripod.
### Software
TBD
