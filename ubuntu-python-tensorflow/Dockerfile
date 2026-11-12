ARG CUDA_VERSION=""
ARG BASE_VERSION="unknown"

## Uncomment or include in "docker build --build-arg" for building with CUDA
#ARG CUDA_VERSION="cuda11"

FROM harbor.chaimeleon-eu.i3m.upv.es/chaimeleon-library-batch/ubuntu-python:${BASE_VERSION}${CUDA_VERSION}
ARG CUDA_VERSION
ARG TARGET_VERSION="unknown"
LABEL name="ubuntu-python-tensorflow"
LABEL version="${TARGET_VERSION}$CUDA_VERSION"
LABEL description="Container with ubuntu 22.04, python 3.10.6, ${CUDA_VERSION} and tensorflow."
LABEL maintainer="J. Damian Segrelles Quilis (dquilis@dsic.upv.es)"
LABEL authorization="This Dockerfile is intended to build a container image that will be publicly accessible in the CHAIMELEON images repository."

############## Things done by the root user ##############
USER root

RUN apt-get -y update && \
    apt-get -y install --no-install-recommends \
        libsm6 libxrender1 libxext6 libgl1-mesa-glx zlib1g  && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* 

# Installation of CUDNN extracted from nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04
#ENV NV_CUDNN_VERSION=8.7.0.84
#RUN apt-get update && \
#    apt-get install -y --no-install-recommends libcudnn8=8.7.0.84-1+cuda11.8  && \
#    apt-mark hold libcudnn8  && \
#    apt-get clean && \
#    rm -rf /var/lib/apt/lists/* 

# Upgrade pip and keyrings to avoid warnings and errors
RUN pip3 install --no-cache-dir --upgrade pip keyrings.alt

# fix error "Could not load library libcudnn_cnn_infer.so.8. Error: libnvrtc.so: cannot open shared object file: No such file or directory"
RUN if [ -n "$CUDA_VERSION" ] ; then cd /usr/local/cuda/targets/x86_64-linux/lib && ln -s libnvrtc.so.11.2 libnvrtc.so ; fi

############### Now change to normal user ################
USER chaimeleon:chaimeleon
WORKDIR /home/chaimeleon

# Installation of Tensorflow
# The extra "and-cuda" is included in the version ".post1" and installs cudnn, nvcc and other libraries 
# required by tensorflow in the "cuda" version of this image (GPU support).
RUN if [ -n "$CUDA_VERSION" ] ; then \
       pip3 install --no-cache-dir tensorflow[and-cuda]==2.15.0.post1 ; \
    else \
       pip3 install --no-cache-dir tensorflow==2.15.0 ; \
    fi

# Set some environment variables for the final container environment...
# It seems not needed in the new versions or installing with the "and-cuda" extra.
#ENV LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/home/chaimeleon/.local/lib/python3.10/site-packages/nvidia/cudnn/lib"
# Fix error "libdevice not found":
# libdevice is included in the pip package nvidia-cuda-nvcc-cu12==12.2.140 which is included in the "and-cuda" extra;
# once installed you can get the path for xla_gpu_cuda_data_dir with: 
#   dirname $(dirname $(dirname $(find / -name libdevice.10.bc 2>/dev/null)))
# in xla_gpu_cuda_data_dir should exist the path nvvm/libdevice/libdevice.10.bc
ENV XLA_FLAGS=--xla_gpu_cuda_data_dir=/home/chaimeleon/.local/lib/python3.10/site-packages/nvidia/cuda_nvcc

####################################
# Verify cudnn (required only for cuda version, for use GPU):
## ls /home/chaimeleon/.local/lib/python3.10/site-packages/nvidia/cudnn/lib/libcudnn.so.8

# Verify tensorflow: https://www.tensorflow.org/install/pip?hl=es-419#step-by-step_instructions
## import tensorflow as tf
## print(tf.reduce_sum(tf.random.normal([1000, 1000])))
## print(tf.config.list_physical_devices('GPU'))
####################################

