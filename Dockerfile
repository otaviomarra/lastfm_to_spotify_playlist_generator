FROM selenium/standalone-firefox

##Adding the api keys
#ENV LASTFM_USERNAME="ommarra"
#ENV LASTFM_APIKEY="cf786f78db52a45f40f6e7b573b7d211"
#ENV SPOTIFY_APP_ID="6cb782c1b0404843b3e5a06e8361cb6e"
#ENV SPOTIFY_SECRET="a32c28deab714fa89091395089cbca90"

USER root

RUN apt-get update && apt-get install -y python3-pip

WORKDIR /app/

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN rm requirements.txt
COPY selenium_open.py /scripts/

CMD ["python3", "scripts/selenium_open.py"]