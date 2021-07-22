FROM python:3

RUN apt-get update && apt-get install -y \
    firefox-esr \
    python3 python3-pip \
    curl unzip wget \
    xvfb

# Installing Geckodriver and Firefox
RUN GECKODRIVER_VERSION=`curl https://github.com/mozilla/geckodriver/releases/latest | grep -Po 'v[0-9]+.[0-9]+.[0-9]+'` && \
    wget https://github.com/mozilla/geckodriver/releases/download/$GECKODRIVER_VERSION/geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz && \
    tar -zxf geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz -C /usr/local/bin && \ 
    chmod +x /usr/local/bin/geckodriver && \
    rm geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz

WORKDIR /usr/src/app

COPY . .
RUN pip install --no-cache-dir -r requirements.txt && \
    rm requirements.txt