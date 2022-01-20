FROM python:3.8-slim-buster

RUN apt-get update && apt-get install -y curl wget gcc build-essential

ARG JFROG_ARTIFACTORY_READ_USER
ARG JFROG_ARTIFACTORY_READ_TOKEN
RUN curl -u${JFROG_ARTIFACTORY_READ_USER}:${JFROG_ARTIFACTORY_READ_TOKEN} https://unity3d.jfrog.io/artifactory/api/npm/auth > ~/.npmrc

WORKDIR /app

RUN /usr/local/bin/python -m pip install --upgrade pip

USER $USER
# install miniconda
# ENV MINICONDA_VERSION 4.8.2
# ENV CONDA_DIR $HOME/miniconda3
# RUN wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh

# install in batch (silent) mode, does not edit PATH or .bashrc or .bash_profile
# -p path
# -f force
# RUN bash Miniconda3-latest-Linux-x86_64.sh -b
# install conda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-4.5.12-Linux-x86_64.sh -O ~/miniconda.sh && \
     /bin/bash ~/miniconda.sh -b -p /opt/conda

# ENV PATH=/root/miniconda3/bin:${PATH} 

# create env with python 3.5
RUN /opt/conda/bin/conda create -y -n dv_env python=3.8

# Copy requirements
COPY unity_cv_datasetvisualizer/requirements.txt requirements.txt

# add source code into the image
COPY . .

# pip install this package
RUN pip3 install -e unity_cv_datasetvisualizer/.
RUN pip3 install -r requirements.txt --index-url=https://artifactory.prd.it.unity3d.com/artifactory/api/pypi/pypi/simple

# install cv2 dependencies
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y

RUN datasetvisualizer
CMD [ "datasetvisualizer"]

