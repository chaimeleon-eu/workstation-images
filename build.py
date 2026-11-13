#! /usr/bin/env python3

import argparse
import enum
import os

REGISTRY_HOST = "harbor.chaimeleon-eu.i3m.upv.es"
REGISTRY_PATH_FOR_BATCH = "/chaimeleon-library-batch/"
REGISTRY_PATH_FOR_DESKTOP = "/chaimeleon-library/"

ubuntu_python_version = "3.10"

ubuntu_python_tensorflow_version = "3.11"
ubuntu_python_pytorch_version = "3.11"

ubuntu_python_tensorflow_desktop_version = "3.18"
ubuntu_python_pytorch_desktop_version = "3.17"

ubuntu_python_tensorflow_desktop_jupyter_version = "3.18"
ubuntu_python_pytorch_desktop_jupyter_version = "3.17"


def cmd(command, exit_on_error=True):
    print(command)
    ret = os.system(command)
    if exit_on_error and ret != 0: exit(1)
    return ret

login_done = False
uploaded_images = []

def upload_image(image: str, latest_tag=False):
    global login_done, uploaded_images
    if input("Do you want to upload the image? [Y/n] ").lower() == "n": return
    while True:
        ret = cmd("docker push "+image, exit_on_error=False)
        if ret == 0: 
            uploaded_images.append(image)
            break
        if input("Uploading error. Do you want to login? [Y/n] ").lower() != "n":
            cmd("docker login "+REGISTRY_HOST)
            login_done = True
        else:
            if input("Abort upload? [y/N] ").lower() == "y": return
            
    if latest_tag:
        latest_tag = image[0:image.find(':')] + ":latest"
        if image.find("cuda") > 0: latest_tag += "-cuda"
        if input("Do you want to tag as "+latest_tag+"? [Y/n] ").lower() == "n": return
        cmd("docker tag "+image+ " " +latest_tag, exit_on_error=False)
        while True:
            ret = cmd("docker push " +latest_tag, exit_on_error=False)
            if ret == 0: 
                uploaded_images.append(latest_tag)
                break
            if input("Uploading error. Do you want to retry? [Y/n] ").lower() == "n": return

    
def logout():
    if input("Do you want to logout? [y/N] ").lower() == "y": 
        cmd("docker logout "+REGISTRY_HOST)

def remove_local_image(image):
    if input("Do you want to remove the local image '"+image+"'? [y/N] ").lower() == "y": 
        cmd("docker rmi "+image)
    


def build_ubuntu_python(gpu=None):
    if gpu==None: gpu = input("Do you want to build with CUDA? [y/N] ").lower() == "y"

    TARGET_VERSION = ubuntu_python_version
    IMAGE_BASE = "nvidia/cuda:11.8.0-runtime-ubuntu22.04" if gpu else "ubuntu:22.04"
    CUDA_VERSION = "cuda11" if gpu else ""
    
    target_image = REGISTRY_HOST+REGISTRY_PATH_FOR_BATCH+"ubuntu-python:"+TARGET_VERSION+CUDA_VERSION
    cmd("docker build -t "+target_image
       +" --build-arg IMAGE_NAME="+IMAGE_BASE+" --build-arg CUDA_VERSION="+CUDA_VERSION
       +" --build-arg TARGET_VERSION="+TARGET_VERSION
       +" ubuntu-python")
    
    if input("Do you want to run the container for testing? [y/N] ").lower() == "y":
        print("OK, when you end the testing write 'exit' to stop and remove the container.")
        cmd("docker run -it --rm --name testing01 "+target_image+" bash")

    upload_image(target_image, latest_tag=True)

class AI_TOOL(enum.Enum):
   tensorflow = 1
   pytorch = 2

def build_ubuntu_python_aitool(aitool:AI_TOOL, gpu=None):
    if gpu==None: gpu = input("Do you want to build with CUDA? [y/N] ").lower() == "y"

    if aitool == AI_TOOL.tensorflow:
        TARGET_VERSION = ubuntu_python_tensorflow_version
        BASE_VERSION = ubuntu_python_version
    else:  # aitool == AI_TOOL.pytorch
        TARGET_VERSION = ubuntu_python_pytorch_version
        BASE_VERSION = ubuntu_python_version
    
    CUDA_VERSION="cuda11" if gpu else ""

    target_image = REGISTRY_HOST+REGISTRY_PATH_FOR_BATCH+"ubuntu-python-"+aitool.name+":"+TARGET_VERSION+CUDA_VERSION
    cmd("docker build -t "+target_image
       +" --build-arg BASE_VERSION="+BASE_VERSION+" --build-arg CUDA_VERSION="+CUDA_VERSION
       +" --build-arg TARGET_VERSION="+TARGET_VERSION
       +" ubuntu-python-"+aitool.name)

    if input("Do you want to run the container for testing? [y/N] ").lower() == "y":
        print("OK, when you end the testing write 'exit' to stop and remove the container.")
        cmd("docker run -it --rm --name testing01 "+target_image+" bash")

    upload_image(target_image, latest_tag=True)

def build_ubuntu_python_aitool_desktop(aitool:AI_TOOL, gpu=None):
    if gpu==None: gpu = input("Do you want to build with CUDA? [y/N] ").lower() == "y"

    if aitool == AI_TOOL.tensorflow:
        TARGET_VERSION = ubuntu_python_tensorflow_desktop_version
        BASE_VERSION = ubuntu_python_tensorflow_version
    else:  # aitool == AI_TOOL.pytorch
        TARGET_VERSION = ubuntu_python_pytorch_desktop_version
        BASE_VERSION = ubuntu_python_pytorch_version

    CUDA_VERSION="cuda11" if gpu else ""

    target_image = REGISTRY_HOST+REGISTRY_PATH_FOR_DESKTOP+"ubuntu-python-"+aitool.name+"-desktop:"+TARGET_VERSION+CUDA_VERSION
    cmd("docker build -t "+target_image
       +" --build-arg AI_TOOL="+aitool.name+" --build-arg BASE_VERSION="+BASE_VERSION+" --build-arg CUDA_VERSION="+CUDA_VERSION
       +" --build-arg TARGET_VERSION="+TARGET_VERSION
       +" ubuntu-python-xxxxx-desktop")

    if input("Do you want to run the container for testing? [y/N] ").lower() == "y":
        print("OK, when you end the testing write 'exit' to stop and remove the container.")
        cmd('docker run -d --rm -p 15900:5900 -p 3322:22'
           +' -e VNC_PASSWORD="chaimeleon" '
           +' -e PASSWORD="chaimeleon" '
           +' -e GUACAMOLE_URL=https://chaimeleon-eu.i3m.upv.es/guacamole/ '
           +' -e GUACAMOLE_USER="guacamoleuser" '
           +' -e GUACAMOLE_PASSWORD="XXXXXXXXXXXX" '
           +' -e GUACD_HOST="10.98.114.250" '
           +' -e SSH_ENABLE_PASSWORD_AUTH=true '
           +' -e GUACAMOLE_CONNECTION_NAME=testing-ubuntu-python-'+aitool.name+'-desktop '
           +' -e GATEWAY_PORTS=true '
           +' -e TCP_FORWARDING=true '
           +' --name testing01 '
           +target_image)
        if input("Do you want see the log? [Y/n] ").lower() != "n":
            cmd("docker logs testing01")
        print("Test VNC service: run a VNC client (tightVNC or tigerVNC) and connect to localhost:15900.")
        print("Test file transfer: run SSH client and connect to localhost:3322")
        
        input("Type enter to continue stopping the container")
        cmd("docker stop testing01")

    upload_image(target_image)

def build_ubuntu_python_aitool_desktop_jupyter(aitool:AI_TOOL, gpu=None):
    if gpu==None: gpu = input("Do you want to build with CUDA? [y/N] ").lower() == "y"

    if aitool == AI_TOOL.tensorflow:
        TARGET_VERSION = ubuntu_python_tensorflow_desktop_jupyter_version
        BASE_VERSION = ubuntu_python_tensorflow_desktop_version
    else:  # aitool == AI_TOOL.pytorch
        TARGET_VERSION = ubuntu_python_pytorch_desktop_jupyter_version
        BASE_VERSION = ubuntu_python_pytorch_desktop_version

    CUDA_VERSION="cuda11" if gpu else ""

    target_image = REGISTRY_HOST+REGISTRY_PATH_FOR_DESKTOP+"ubuntu-python-"+aitool.name+"-desktop-jupyter:"+TARGET_VERSION+CUDA_VERSION
    cmd("docker build -t "+target_image
       +" --build-arg AI_TOOL="+aitool.name+" --build-arg BASE_VERSION="+BASE_VERSION+" --build-arg CUDA_VERSION="+CUDA_VERSION
       +" --build-arg TARGET_VERSION="+TARGET_VERSION
       +" ubuntu-python-xxxxx-desktop-jupyter")

    if input("Do you want to run the container for testing? [y/N] ").lower() == "y":
        print("OK, when you end the testing write 'exit' to stop and remove the container.")
        cmd('docker run -d --rm -p 15900:5900 -p 3322:22'
           +' -e VNC_PASSWORD="chaimeleon" '
           +' -e PASSWORD="chaimeleon" '
           +' -e GUACAMOLE_URL=https://chaimeleon-eu.i3m.upv.es/guacamole/ '
           +' -e GUACAMOLE_USER="guacamoleuser" '
           +' -e GUACAMOLE_PASSWORD="XXXXXXXXXXXX" '
           +' -e GUACD_HOST="10.98.114.250" '
           +' -e SSH_ENABLE_PASSWORD_AUTH=true '
           +' -e GUACAMOLE_CONNECTION_NAME=testing-ubuntu-python-'+aitool.name+'-desktop '
           +' -e GATEWAY_PORTS=true '
           +' -e TCP_FORWARDING=true '
           +' --name testing01 '
           +target_image)
        if input("Do you want see the log? [Y/n] ").lower() != "n":
            cmd("docker logs testing01")
        print("Test VNC service: run a VNC client (tightVNC or tigerVNC) and connect to localhost:15900.")
        print("Test file transfer: run SSH client and connect to localhost:3322")
        
        input("Type enter to continue stopping the container")
        cmd("docker stop testing01")

    upload_image(target_image)


IMAGES = ["all", "ubuntu-python", 
          "ubuntu-python-tensorflow", "ubuntu-python-pytorch", 
          "ubuntu-python-tensorflow-desktop", "ubuntu-python-pytorch-desktop",
          "ubuntu-python-tensorflow-desktop-jupyter", "ubuntu-python-pytorch-desktop-jupyter"]


def build(image, gpu=None):
    if image == "ubuntu-python":
        build_ubuntu_python(gpu)
    elif image == "ubuntu-python-tensorflow":
        build_ubuntu_python_aitool(AI_TOOL.tensorflow, gpu)
    elif image == "ubuntu-python-pytorch":
        build_ubuntu_python_aitool(AI_TOOL.pytorch, gpu)
    elif image == "ubuntu-python-tensorflow-desktop":
        build_ubuntu_python_aitool_desktop(AI_TOOL.tensorflow, gpu)
    elif image == "ubuntu-python-pytorch-desktop":
        build_ubuntu_python_aitool_desktop(AI_TOOL.pytorch, gpu)
    elif image == "ubuntu-python-tensorflow-desktop-jupyter":
        build_ubuntu_python_aitool_desktop_jupyter(AI_TOOL.tensorflow, gpu)
    elif image == "ubuntu-python-pytorch-desktop-jupyter":
        build_ubuntu_python_aitool_desktop_jupyter(AI_TOOL.pytorch, gpu)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()    
    parser.add_argument("IMAGE", help="Which image to build", nargs="?", default="")
    args = parser.parse_args()

    image = str(args.IMAGE).lower()
    while image not in IMAGES:
        print("Unknown image, please select one option:")
        n = 0
        for img_name in IMAGES: 
            print("%d - %s" % (n, img_name))
            n += 1
        try:
            image = IMAGES[int(input(""))]
        except (ValueError, IndexError): image = ""
    print(image)

    if image == "all":
        for image in IMAGES[1:]: build(image, gpu=False)
        for image in IMAGES[1:]: 
            if not image.find("desktop") > 0:  # Skip build GPU images for desktops, currently not used because the GPU is only available for jobs
                build(image, gpu=True)
    else:
        build(image)

    if login_done: logout()

    for image in uploaded_images:
        remove_local_image(image)

    exit(0)
