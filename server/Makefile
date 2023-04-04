run:
	python3 ./server.py

docker_build:
	sudo docker build -t whiteboard-server .

docker_run:
	sudo docker run -ti --rm \
	--network=host \
	whiteboard-server
