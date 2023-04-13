docker_build:
	sudo docker build . -t whiteboard-client

docker_run:
	sudo docker run --rm -it \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -e DISPLAY=$DISPLAY \
    -u qtuser \
    --network whiteboard-network \
		--publish 1100:1100 \
    whiteboard-client python3 ./main.py $(SERVER_HOST)