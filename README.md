# Nerf Iron Dome
![Turret](https://github.com/brianlevis/nerf-iron-dome/raw/master/turret.jpg)
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
API is being rewritten to be higher performing, and image processing work is in progress.
## TODO
Solder electronics, do software. Also add 3D models to git.
## Credits
Turret base inspired by Britt Michelsen's [Nerf Vulcan Sentry Gun](http://www.instructables.com/id/Nerf-Vulcan-Sentry-Gun/), Nerf RapidStrike [teardown guide](http://www.instructables.com/id/Nerf-Vulcan-Sentry-Gun/),
[xboxdrv python wrapper class](https://github.com/FRC4564/Xbox)
## Tech
### Hardware
Nerf RapidStrike with pusher and flywheel motors hooked up to 7.5V 100W power supply and 5V relay module. Super high torque HS-805BB servos hooked up to 6V 18W power supply. Arduino controls all actuators, and communicates over serial with Raspberry Pi. Raspberry Pi Camera v2 mounted on top of gun. Possibly will be mounted on drum tripod.
### Software
[Python Connector Design](https://docs.google.com/document/d/1Gke5QFeYasZ8_wYOghZAU99f_aja3h15VcXeIRREn2o/pub)
