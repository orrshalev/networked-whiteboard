FROM ubuntu:22.10

WORKDIR /home

COPY ./ ./

RUN useradd -ms /bin/bash whiteboard-server
RUN chown -R whiteboard-server:whiteboard-server /home
RUN chmod 755 -R /home  

RUN apt update
RUN apt install -y net-tools
RUN apt install -y python3
RUN apt install -y python3-pip

COPY ./requirements.txt ./
RUN pip install -r requirements.txt


USER whiteboard-server

CMD ["bash"]