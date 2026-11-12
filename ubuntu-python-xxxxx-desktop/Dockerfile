ARG AI_TOOL=tensorflow
ARG BASE_VERSION="unknown"
ARG CUDA_VERSION

## Uncomment or include in "docker build --build-arg" for building with CUDA
#ARG CUDA_VERSION="cuda11"

## Uncomment or include in "docker build --build-arg" for building with pyTorch
#ARG AI_TOOL=pytorch
#ARG BASE_VERSION="unknown"

FROM harbor.chaimeleon-eu.i3m.upv.es/chaimeleon-library-batch/ubuntu-python-${AI_TOOL}:${BASE_VERSION}${CUDA_VERSION}
ARG AI_TOOL
ARG CUDA_VERSION
ARG TARGET_VERSION="unknown"
LABEL name="ubuntu-python-${AI_TOOL}-desktop"
LABEL version="${TARGET_VERSION}${CUDA_VERSION}"
LABEL description="Container with ubuntu 22.04, python 3.10.6, ${AI_TOOL}, ${CUDA_VERSION}, lxde desktop, vnc and ssh services."
LABEL maintainer="J. Damian Segrelles Quilis (dquilis@dsic.upv.es)"

############## Things done by the root user ##############
USER root
#RUN sed -i 's#http://archive.ubuntu.com/ubuntu/#mirror://mirrors.ubuntu.com/mirrors.txt#' /etc/apt/sources.list;

# libxkbcommon-x11-0, libxcb-icccm4, libxcb-image0, libxcb-keysyms1, libxcb-randr0, libxcb-render-util0 are required by itk-snap
# lxhotkey-plugin-openbox required to fix error opening the global hotkeys configuration window
ENV DEBIAN_FRONTEND noninteractive
RUN apt update && \
    apt install -y --no-install-recommends \
                software-properties-common curl apache2-utils && \
    apt install -y --no-install-recommends \
                supervisor sudo net-tools zenity xz-utils \
                dbus-x11 x11-utils alsa-utils mesa-utils libgl1-mesa-dri && \
    add-apt-repository ppa:mozillateam/ppa && \
    apt update && \
    apt install -y --no-install-recommends \
                xvfb x11vnc vim-tiny wget less firefox-esr ttf-wqy-zenhei \
                libxkbcommon-x11-0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 && \
    apt install -y --no-install-recommends \
                lxde gtk2-engines-murrine gnome-themes-standard gtk2-engines-pixbuf gtk2-engines-murrine arc-theme xterm lxhotkey-plugin-openbox && \
    rm -rf /var/lib/apt/lists/* && \
    ln -s /usr/bin/firefox-esr /usr/bin/firefox
    
# tini to fix subreap
ARG TINI_VERSION=v0.18.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /bin/tini
RUN chmod +x /bin/tini

COPY rootfs/etc /etc/
COPY rootfs/usr /usr/ 
COPY --chown=chaimeleon:chaimeleon rootfs/home/chaimeleon /home/chaimeleon/
RUN chmod +x /home/chaimeleon/.init/startup.sh && \
    chmod +x /home/chaimeleon/.local/bin/install-jobman && \
    chmod +x /usr/local/bin/xvfb.sh

RUN pip3 install --no-cache-dir guacli

EXPOSE 5900

########## SSH service installation
RUN apt update && \
    apt install -y --no-install-recommends openssh-server && \
    apt autoclean -y && \
    apt autoremove -y && \
    rm -rf /var/lib/apt/lists/*
        
COPY configure_sshd.sh /home/chaimeleon/.init/configure_sshd.sh
RUN chmod +x /home/chaimeleon/.init/configure_sshd.sh

EXPOSE 2222

########## jobman installation
# The nodesource's script adds the PPA and do apt update
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt install -y --no-install-recommends  nodejs git \
    && rm -rf /var/lib/apt/lists/*
## Currently only dependencies are installed here.
## The app now is installed by the init script in order to get the last version on container creation.
## This is temporal due to the current frequency of updates.
#   && cd /opt \
#   && git clone -b dev https://github.com/asalic/jobman.git \
#   && cd jobman \
#   && npm install \
#   && npx tsc \
#   && ln -s /opt/jobman/bin/jobman /usr/bin/
#   && cp src/settings.json /home/chaimeleon/.jobman/

########## itk-snap installation
RUN cd /tmp \
    && curl -L -o itk-snap.tgz 'https://download.sourceforge.net/project/itk-snap/itk-snap/4.4.0/itksnap-4.4.0-20250909-Linux-x86_64.tar.gz' \
    && tar xzf itk-snap.tgz \
    && cp -av ./itksnap-*/* /usr/local/ \
    && rm -rf ./itksnap-*/ itk-snap.tgz

# http://www.nitrc.org/frs/downloadlink.php/13395
# https://sourceforge.net/projects/itk-snap/files/itk-snap/4.0.1/itksnap-4.0.1-20230320-Linux-gcc64.tar.gz/download
# https://netcologne.dl.sourceforge.net/project/itk-snap/itk-snap/4.0.1/itksnap-4.0.1-20230320-Linux-gcc64.tar.gz
# https://sourceforge.net/projects/itk-snap/files/latest/download
# https://download.sourceforge.net/project/itk-snap/itk-snap/4.0.2/itksnap-4.0.2-Linux-gcc64.tar.gz

########## itk-snap (old version) 3.6 installation
RUN cd /tmp \
    && curl -L -o itk-snap.tgz 'https://download.sourceforge.net/project/itk-snap/itk-snap/3.6.0/itksnap-3.6.0-20170401-Linux-x86_64.tar.gz' \
    && tar xzf itk-snap.tgz \
    && cp -av ./itksnap-*/lib/* /usr/local/lib/ \
    && cp -av ./itksnap-*/bin/itksnap /usr/local/bin/itksnap-3.6 \
    && rm -rf ./itksnap-*/ itk-snap.tgz
RUN apt update && \
    apt install -y --no-install-recommends libglu1-mesa && \
    rm -rf /var/lib/apt/lists/*


########## helm installation (required for the script delete-this-desktop)
RUN wget https://get.helm.sh/helm-v3.13.1-linux-amd64.tar.gz -O helm.tgz \
    && tar xzf helm.tgz \
    && mv linux-amd64/helm /home/chaimeleon/.local/bin/ \
    && rm -rf helm.tgz linux-amd64

########## install delete-this-desktop
RUN chmod +x /home/chaimeleon/.local/bin/delete-this-desktop /usr/bin/lxde-logout

########## apply the new mime types defined in /usr/share/mime/packages
RUN update-mime-database /usr/share/mime


############### Now change to normal user ################
USER chaimeleon:chaimeleon
WORKDIR /home/chaimeleon

ENV SUPERVISOR_CONF_FILE=/home/chaimeleon/.supervisor/conf.d/supervisord.conf
RUN mkdir -p /home/chaimeleon/.supervisor/conf.d/ && \
    cp /etc/supervisor/conf.d/supervisord.conf $SUPERVISOR_CONF_FILE

# default values to environment variables which can be configured
ENV VNC_HOST= \
    VNC_PASSWORD= \
    PASSWORD= \
    X11VNC_ARGS= \
    OPENBOX_ARGS= \
    RESOLUTION= \
    GUACAMOLE_URL= \
    GUACAMOLE_USER= \
    GUACAMOLE_PASSWORD= \
    GUACD_HOST= \
    GUACAMOLE_CONNECTION_NAME=

########## SSH service default values to environment variables which can be configured
ENV SSH_ENABLE_PASSWORD_AUTH= \
    TCP_FORWARDING= \
    GATEWAY_PORTS= \
    DISABLE_SFTP=
    
#HEALTHCHECK --interval=30s --timeout=5s CMD curl --fail http://127.0.0.1:6079/api/health
ENTRYPOINT ["/home/chaimeleon/.init/startup.sh"]

