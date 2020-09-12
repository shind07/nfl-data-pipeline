FROM ubuntu:18.04

RUN apt-get update \
    && apt-get install -y  \
        python3 \ 
        python3-pip \
        git \
    && apt-get clean

COPY requirements.txt tmp/requirements.txt
RUN pip3 install -r tmp/requirements.txt

WORKDIR /opt/nfl 
COPY . .


ENTRYPOINT [ ]
CMD [ "echo", "testing..." ]