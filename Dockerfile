# Dockerfile for playing around with tensorflow, gym and stable_baselines on remote workstation
FROM tensorflow/tensorflow
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install cmake libopenmpi-dev python3-dev zlib1g-dev
RUN pip3 install --upgrade pip \
    && pip3 install scipy sklearn pandas matplotlib pickle5 ipython gym stable-baselines[mpi]

WORKDIR /ewiis3
COPY . /ewiis3