# Set base image
FROM python:slim-bullseye

# Set container label
LABEL org.opencontainers.image.title="Speedflux Docker Image" \
      org.opencontainers.image.description="Speedflux Docker Image" \
      org.opencontainers.image.documentation="https://github.com/dontobi/SpeedFlux.rpi#readme" \
      org.opencontainers.image.authors="Tobias Schug <github@myhome.zone>" \
      org.opencontainers.image.url="https://github.com/dontobi/SpeedFlux.rpi" \
      org.opencontainers.image.source="https://github.com/dontobi/SpeedFlux.rpi" \
      org.opencontainers.image.base.name="docker.io/library/python:slim-bullseye" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.created="${DATI}"

ENV DEBIAN_FRONTEND=noninteractive

# Installation process
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    apt-utils apt-transport-https curl dirmngr gnupg1 \
    && pip3 install influxdb pythonping requests \
    && curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | bash \
    && apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 8E61C2AB9A6D1557 \
    && apt-get update && apt-get -q -y install --no-install-recommends speedtest \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && apt-get autoclean -y && apt-get autoremove && apt-get clean \
    && rm -rf /tmp/* /var/tmp/* /root/.cache/* /var/lib/apt/lists/*

# Setting up ENVs
ENV NAMESPACE="None" \
    INFLUX_DB_ADDRESS="influxdb" \
    INFLUX_DB_PORT="8086" \
    INFLUX_DB_USER="_influx_user_" \
    INFLUX_DB_PASSWORD="_influx_pass_" \
    INFLUX_DB_DATABASE="speedflux" \
    INFLUX_DB_TAGS="None" \
    PING_INTERVAL="5" \
    PING_TARGETS="8.8.8.8" \
    SPEEDTEST_INTERVAL="5" \
    SPEEDTEST_FAIL_INTERVAL="5" \
    SPEEDTEST_SERVER_ID="6601" \
    LOG_TYPE="info"

# Final setup & execution
ADD main.py /app/main.py
WORKDIR /app
CMD ["python", "main.py"]
