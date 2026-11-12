ARG AI_TOOL=tensorflow
ARG BASE_VERSION="unknown"
ARG CUDA_VERSION

## Uncomment or include in "docker build --build-arg" for building with CUDA
#ARG CUDA_VERSION="cuda11"

## Uncomment or include in "docker build --build-arg" for building with pyTorch
#ARG AI_TOOL=pytorch
#ARG BASE_VERSION="unknown"

FROM harbor.chaimeleon-eu.i3m.upv.es/chaimeleon-library/ubuntu-python-${AI_TOOL}-desktop:${BASE_VERSION}${CUDA_VERSION}
ARG AI_TOOL
ARG CUDA_VERSION
ARG TARGET_VERSION="unknown"
LABEL name="ubuntu-python-${AI_TOOL}-desktop-jupyter"
LABEL version="${TARGET_VERSION}${CUDA_VERSION}"
LABEL description="Container with ubuntu 22.04, python 3.10.6, ${AI_TOOL}, ${CUDA_VERSION}, lxde desktop, vnc and ssh services, and jupyter notebooks web service."
LABEL maintainer="J. Damian Segrelles Quilis (dquilis@dsic.upv.es)"

############## Things done by the root user ##############
USER root
    
RUN pip install --no-cache-dir jupyter
#RUN pip install --no-cache-dir jupyterlab    it seems now already included in jupyter package (from v7 jupyterNotebook is based on jupyterLab)

COPY --chown=chaimeleon:chaimeleon rootfs/home/chaimeleon /home/chaimeleon/

# - Delete the "Run Jupyter" start menu entries
# - Add execution permission to the start jupyter script
# - Autostart firefox with the web page of the jupyter service which is already running (initiated by startup_jupyter.sh)
RUN rm -f /usr/local/share/applications/jupyterlab.desktop /usr/local/share/applications/jupyter-notebook.desktop \
 && chmod +x /home/chaimeleon/.init/startup_jupyter.sh \
 && echo '@firefox http://localhost:8888' >> /etc/xdg/lxsession/LXDE/autostart

#EXPOSE 8888

############### Now change to normal user ################
USER chaimeleon:chaimeleon
WORKDIR /home/chaimeleon
    

ENTRYPOINT ["/home/chaimeleon/.init/startup_jupyter.sh"]
