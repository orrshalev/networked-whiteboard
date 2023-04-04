FROM ubuntu:22.10

EXPOSE 1100

ENV DEBIAN_FRONTEND=noninteractive

RUN adduser --quiet --disabled-password qtuser && usermod -a -G audio qtuser

ENV LIBGL_ALWAYS_INDIRECT=1

RUN apt-get update && apt-get install -y python3-pyqt5

COPY ./ ./
