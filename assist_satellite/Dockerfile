FROM ghcr.io/home-assistant/base-debian:bookworm

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

WORKDIR /usr/src
ARG LINUX_VOICE_ASSISTANT_VERSION=1.1.15
ENV PIP_BREAK_SYSTEM_PACKAGES=1

# Install system dependencies
RUN \
    apt-get update && \
        apt-get install --yes --no-install-recommends \
        python3 \
        python3-pip \
        avahi-utils \
        pulseaudio-utils \
        alsa-utils \
        pipewire-bin \
        pipewire-alsa \
        pipewire-pulse \
        build-essential \
        libmpv-dev \
        libasound2-plugins \
        ca-certificates \
        iproute2 \
        vim \
        procps \
    \
    && pip3 install --no-cache-dir -U \
        setuptools \
        wheel \
    && pip3 install --no-cache-dir \
        "linux-voice-assistant @ https://github.com/OHF-Voice/linux-voice-assistant/archive/refs/tags/v${LINUX_VOICE_ASSISTANT_VERSION}.tar.gz" \
    \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy default sounds
COPY sounds/ ./sounds/

# Copy wake word models
COPY wakewords/ ./wakewords/

WORKDIR /
COPY rootfs /

# Ensure all s6 service scripts and trainer hook wrapper are executable.
RUN chmod a+x \
    /usr/src/run_with_trainer_hook.py \
    /etc/s6-overlay/s6-rc.d/assist_satellite/run \
    /etc/s6-overlay/s6-rc.d/assist_satellite/finish \
    /etc/s6-overlay/s6-rc.d/discovery/run

HEALTHCHECK --start-period=10m \
    CMD pgrep -f "run_with_trainer_hook|linux_voice_assistant" || exit 1
