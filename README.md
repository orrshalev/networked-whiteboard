# Multiplayer Whiteboard

Remote change here

![networking whiteboard demo](https://user-images.githubusercontent.com/78034726/236699634-b8005eef-5ea6-492e-894b-224bd583aa5b.gif)

## Overview

A server-client application written in Python which utilizes socket programming, virtual networking with Docker, and GUI programming with the PyQT framework. 

This is a collaborative project as part of the University of Georgia's Master's level networking course. collaborators include:

| Name              |
| ----------------- |
| Orr Shalev        |
| Devan Allen       |
| Mitchel Castleton |

## Dependencies

- Docker must be installed and the docker daemon must be running
- You may need to pull the ubuntu and python images (`docker pull python` and `docker pull ubuntu`)
- This app is intended to run on a Linux environment with DISPLAY environment variable set; you may need to set a DISPLAY environment and enable X11 forwarding if you are not on Linux (WSL is recommended for Windows).

## Server

Make sure that your working directory is `server`

**Docker commands:**

To build:

`sudo docker build . -t whiteboard-server`

To run: 

`sudo docker run -ti --rm
	--network whiteboard-network
	--publish 1500:1500
	whiteboard-server`

Make sure that your working directory is `client`

**Docker commands:**

To build:

`sudo docker build . -t whiteboard-client`

To run:

`sudo docker run --rm -it
-v /tmp/.X11-unix:/tmp/.X11-unix
-e DISPLAY=$DISPLAY
-u qtuser
--network whiteboard-network
--publish PORT:1000
whiteboard-client python3 ./main.py 172.18.0.2`

Where PORT is the port number you would like your local system to use. Keep in mind that you should not be using overlapping PORTs for the client
