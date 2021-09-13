FROM tensorflow/tensorflow:1.15.5
# https://hub.docker.com/r/tensorflow/tensorflow
# https://stackoverflow.com/questions/55313610/importerror-libgl-so-1-cannot-open-shared-object-file-no-such-file-or-directo

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y \
    && apt-get install -y cmake libopenmpi-dev zlib1g-dev \
    && apt-get install -y ffmpeg libsm6 libxext6

RUN pip3 install scipy sklearn pandas matplotlib pickle5 ipython gym stable-baselines[mpi] python-dotenv PyMySQL SQLAlchemy PyPika

WORKDIR /ewiis3
COPY . /ewiis3