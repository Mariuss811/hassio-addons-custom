ARG BUILD_FROM
FROM ${BUILD_FROM}

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install microWakeWord from a specific branch
WORKDIR /usr/src

RUN \
    apt-get update \
    && apt-get install -y --no-install-recommends \
        git \
        netcat-traditional \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        build-essential \
    \
    && python3 -m venv .venv \
    && .venv/bin/pip3 install --no-cache-dir -U \
        setuptools \
        wheel \
    \
    # Install wyoming-microwakeword from the custom-model-support branch
    && .venv/bin/pip3 install --no-cache-dir \
        --extra-index-url https://www.piwheels.org/simple \
        "wyoming-microwakeword @ git+https://github.com/michelle-avery/wyoming-microwakeword.git@custom-model-support" \
    \
    && apt-get remove --yes build-essential git \
    && apt-get autoclean \
    && apt-get purge \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /
COPY rootfs /

HEALTHCHECK --start-period=10m \
    CMD echo '{ "type": "describe" }' \
        | nc -w 1 localhost 10400 \
        | grep -iq "microwakeword" \
        || exit 1
