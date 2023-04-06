run:
	python3 ./server.py

docker_build:
	sudo docker build -t whiteboard-server .

docker_run:
	sudo docker run -ti --rm \
	--network whiteboard-network \
	--publish 1500:1500 \
	whiteboard-server