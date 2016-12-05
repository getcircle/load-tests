FROM ubuntu:14.04

RUN apt-get update -y && apt-get install -y \
    python-setuptools \
    python-dev \
    git && \
    easy_install pip==7.1.2

ADD . /src
WORKDIR /src
RUN pip install -U --no-deps -r requirements.txt

EXPOSE 8089

CMD ["bin/start-locust"]
