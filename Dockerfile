# Set base image
FROM python:3.9-slim-bullseye

# Set container label
LABEL org.opencontainers.image.title="Speedflux Docker Image" \
      org.opencontainers.image.description="Speedflux Docker Image" \
      org.opencontainers.image.documentation="https://github.com/dontobi/SpeedFlux.rpi#readme" \
      org.opencontainers.image.authors="Tobias S. <github@myhome.zone>" \
      org.opencontainers.image.url="https://github.com/dontobi/SpeedFlux.rpi" \
      org.opencontainers.image.source="https://github.com/dontobi/SpeedFlux.rpi" \
      org.opencontainers.image.base.name="docker.io/library/debian:bullseye-slim" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.created="${DATI}"

ENV DEBIAN_FRONTEND=noninteractive

# Installation process
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \

    # Install apt packages
    apt-utils apt-transport-https curl dirmngr gnupg1 \

    # Install python packages
    && pip3 install influxdb pythonping requests \

    # Install Speedtest
    && curl -L "https://packagecloud.io/ookla/speedtest-cli/gpgkey" 2> /dev/null | apt-key add - \
    && echo "deb https://packagecloud.io/ookla/speedtest-cli/debian/ bullseye main" | tee /etc/apt/sources.list.d/ookla_speedtest-cli.list \
    && apt-get update && apt-get -q -y install speedtest \

    # Clean up
    && apt-get -q -y autoremove && apt-get -q -y clean \
    && rm -rf /var/lib/apt/lists/*

# Copy and final setup
ADD . /app
WORKDIR /app

# Setting up ENVs
ENV NAMESPACE="None" \
    INFLUX_DB_ADDRESS="influxdb" \
    INFLUX_DB_PORT="8086" \
    INFLUX_DB_USER="_influx_user_" \
    INFLUX_DB_PASSWORD="_influx_pass_" \
    INFLUX_DB_DATABASE="speedflux" \
    SPEEDTEST_INTERVAL="5" \
    SPEEDTEST_FAIL_INTERVAL="5" \
    SPEEDTEST_SERVER_ID="6601" \
    LOG_TYPE="info"

# Excetution
CMD ["python", "main.py"]
