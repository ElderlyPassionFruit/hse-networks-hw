FROM ubuntu:22.04

WORKDIR /igor

RUN apt update && apt install -y python3.10 && apt install -y iputils-ping

COPY . .