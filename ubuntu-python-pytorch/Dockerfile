ARG CUDA_VERSION=""
ARG BASE_VERSION="unknown"

## Uncomment or include in "docker build --build-arg" for building with CUDA
#ARG CUDA_VERSION="cuda11"

FROM harbor.chaimeleon-eu.i3m.upv.es/chaimeleon-library-batch/ubuntu-python:${BASE_VERSION}${CUDA_VERSION}
# FROM pytorch/pytorch:1.9.1-cuda11.1-cudnn8-runtime        We can build from a container with pytorch already installed (untested alternative)
ARG CUDA_VERSION
ARG TARGET_VERSION="unknown"
LABEL name="ubuntu-python-pytorch"
LABEL version="${TARGET_VERSION}$CUDA_VERSION"
LABEL description="Container with ubuntu 22.04, python 3.10.6, ${CUDA_VERSION} and pyTorch."
LABEL maintainer="J. Damian Segrelles Quilis (dquilis@dsic.upv.es)"
LABEL authorization="This Dockerfile is intended to build a container image that will be publicly accessible in the CHAIMELEON images repository."

############## Things done by the root user ##############
USER root

RUN apt-get -y update && \
    apt-get -y install --no-install-recommends \
        libgl1-mesa-glx && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* 

# Upgrade pip and keyrings to avoid warnings and errors
RUN pip3 install --no-cache-dir --upgrade pip keyrings.alt

############### Now change to normal user ################
USER chaimeleon:chaimeleon
WORKDIR /home/chaimeleon

#RUN pip3 install --no-cache-dir torch==1.6.0+cu101 torchvision==0.7.0+cu101 -f https://download.pytorch.org/whl/torch_stable.html   # for CUDA 10.1, includes CUDNN 1.7
#RUN pip3 install --no-cache-dir torch==1.8.0 torchvision==0.9.0 torchaudio==0.8.0   # for CUDA 10.2, includes CUDNN 1.7
#RUN pip3 install --no-cache-dir torch==1.10.0 torchvision==0.11.1 torchaudio==0.10.0    # for CUDA 10.2, includes CUDNN 1.8
# for cpu and for cuda 11.8
RUN pip3 install --no-cache-dir typing-extensions && \
    if [ -z "$CUDA_VERSION" ] ; then pip3 install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu ; \
                                else pip3 install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 ; fi


# Verify pyTorch: https://pytorch.org/get-started/locally/#linux-verification
## import torch
## x = torch.rand(5, 3)
## print(x)
## torch.cuda.is_available()
