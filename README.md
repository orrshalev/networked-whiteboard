## Whiteboard Server

Docker commands:

To build:

`sudo docker build . -t whiteboard-server`

To run: 

`sudo docker run -ti --rm \
    --network whiteboard-network \
    -p 1500:1500 \
    whiteboard-server`
