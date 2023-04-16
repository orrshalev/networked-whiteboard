# Multiplayer Whiteboard

## Dependencies

- Docker must be installed and the docker daemon must be running
- You may need to pull the ubuntu and python images (`docker pull python` and `docker pull ubuntu`)

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

## Client

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
--publish PORT:1100
whiteboard-client python3 ./main.py 172.18.0.2`

Where PORT is the port number you would like your local system to use. Keep in mind that you should not be using overlapping PORTs for the client
