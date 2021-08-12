FROM ubuntu:20.04

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND="noninteractive"

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y \
        python3-dev \
        cython3 \
		python3-pip \
        zlib1g-dev \
        libxml2-dev \
        libxslt-dev \
        lib32z1-dev \
        jq \
		firefox \
		firefox-geckodriver \
		cron \
		tzdata 

WORKDIR /tmp

RUN pip3 install -U pip \
    && pip3 install -U lxml openpyxl

ENV TZ="America/New_York"

COPY requirements.txt .
RUN pip3 install -r requirements.txt

WORKDIR /app
COPY app/ .
RUN chown -R root:root /app

COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

COPY crontab /etc/cron.d/crontab
RUN chmod 0644 /etc/cron.d/crontab
RUN /usr/bin/crontab /etc/cron.d/crontab

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["/docker-entrypoint.sh"]
