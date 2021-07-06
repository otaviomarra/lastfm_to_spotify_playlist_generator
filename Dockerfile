FROM python:3

RUN apt-get update && apt-get install -yq \ 
    firefox-esr \
    unzip

RUN wget -q "https://github.com/mozilla/geckodriver/releases/download/v0.19.1/geckodriver-v0.19.1-linux64.tar.gz" -O /tmp/geckodriver.tgz \
    && tar zxf /tmp/geckodriver.tgz -C /usr/bin/ \
    && rm /tmp/geckodriver.tgz

##Adding the api keys
#ENV LASTFM_USERNAME="ommarra"
#ENV LASTFM_APIKEY="cf786f78db52a45f40f6e7b573b7d211"
#ENV SPOTIFY_APP_ID="6cb782c1b0404843b3e5a06e8361cb6e"
#ENV SPOTIFY_SECRET="a32c28deab714fa89091395089cbca90"

#Defining our stored cache and saved data relative path
#   Cache will make the api requests to run faster
#   Data will be usefull when updating playlists from already stored data, not running new api calls
ENV CACHEPATH=/cache
ENV DATAPATH=/data

WORKDIR /usr/src/app

COPY ${CACHEPATH} ${WORKDIR}
COPY ${DATAPATH} ${WORKDIR}
COPY /utils ${WORKDIR}
COPY /scripts ${WORKDIR}

RUN echo Installing dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Build Selenium Standalone
FROM selenium/node-firefox:4.0.0-rc-1-prerelease-20210618
LABEL authors=SeleniumHQ

COPY selenium/start-selenium-standalone.sh /opt/bin/start-selenium-standalone.sh
COPY selenium/selenium.conf /etc/supervisor/conf.d/
COPY selenium/generate_config /opt/bin/generate_config

ENV SE_RELAX_CHECKS true

EXPOSE 4444

#Execute
RUN ls -a
ENTRYPOINT "./selenium_open.py"