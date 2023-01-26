#!/bin/bash

export REGISTRY_HOST=harbor.chaimeleon-eu.i3m.upv.es
export REGISTRY_PATH=/chaimeleon-library/

export IMAGE_NAME="ubuntu:18.04"
export TARGET_VERSION=2.3

export CUDA_VERSION=
echo "Do you want to build with CUDA? (y/n)" && read RES
if [ "$RES" == "y" ]; then 
    export IMAGE_NAME="nvidia/cuda:10.2-runtime-ubuntu18.04"
    export CUDA_VERSION=cuda10
fi


# =========================================== Building all the images ===========================================
docker build -t ${REGISTRY_HOST}${REGISTRY_PATH}ubuntu_python:${TARGET_VERSION}${CUDA_VERSION} \
             --build-arg IMAGE_NAME=${IMAGE_NAME} --build-arg CUDA_VERSION=${CUDA_VERSION} \
             --build-arg TARGET_VERSION=${TARGET_VERSION} \
             ubuntu_python

# ======================================== Deploying a container to test ========================================
echo "Do you want to run the container for testing? (y/n)" && read RES
if [ "$RES" == "y" ]; then 
    docker run -d --rm --name testing01 \
               ${REGISTRY_HOST}${REGISTRY_PATH}ubuntu_python:${TARGET_VERSION}${CUDA_VERSION}

    echo "Continue showing the log? (y/n)" && read RES
    if [ "$RES" != "y" ]; then exit; fi
    docker logs testing01
    echo "Test VNC service: run a VNC client (tightVNC or tigerVNC) and connect to localhost:15900."
    echo "Test file transfer: run SSH client and connect to localhost:3322"
    
    echo "Continue stopping the container? (y/n)" && read RES
    if [ "$RES" != "y" ]; then exit; fi
    docker stop testing01
fi

# ====================================== Uploading the images to registry ======================================
echo "Do you want to upload the image? (y/n)" && read RES
if [ "$RES" == "y" ]; then 
    RET=999
    while [ $RET != 0 ]; do
        docker push ${REGISTRY_HOST}${REGISTRY_PATH}ubuntu_python:${TARGET_VERSION}${CUDA_VERSION}
        RET=$?
        if [ $RET != 0 ]; then
            echo "Uploading error. Do you want to login? (y/n)" && read RES
            if [ "$RES" == "y" ]; then 
                docker login $REGISTRY_HOST
            else
                echo "Abort upload? (y/n)" && read RES
                if [ "$RES" == "y" ]; then RET=0; fi
            fi
        fi
    done
    echo "Do you want to logout? (y/n)" && read RES
    if [ "$RES" == "y" ]; then 
        docker logout $REGISTRY_HOST
    fi

    # ====================================== Removing local images ======================================
    echo "Do you want to remove the local image? (y/n)" && read RES
    if [ "$RES" == "y" ]; then 
        docker rmi ${REGISTRY_HOST}${REGISTRY_PATH}ubuntu_python:${TARGET_VERSION}${CUDA_VERSION}
    fi
fi