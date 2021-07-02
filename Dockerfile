FROM python:3

ENV LASTFM_USERNAME="ommarra"
ENV LASTFM_APIKEY=
ENV SPOTIFY_APP_ID=
ENV SPOTIFY_SECRET=
ENV CACHEPATH=/cache
ENV DATAPATH=/data

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN "Installing dependencies"

RUN pip install --no-cache-dir -r requirements.txt

RUN echo "Setting up"

COPY ${CACHEPATH} .
COPY ${DATAPATH} .

CMD [ "python", "./your-daemon-or-script.py" ]