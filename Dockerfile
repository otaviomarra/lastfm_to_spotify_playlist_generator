FROM python:3

RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    curl unzip wget \
    xvfb

# Installing Geckodriver and Firefox
RUN GECKODRIVER_VERSION=`curl https://github.com/mozilla/geckodriver/releases/latest | grep -Po 'v[0-9]+.[0-9]+.[0-9]+'` && \
    wget https://github.com/mozilla/geckodriver/releases/download/$GECKODRIVER_VERSION/geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz && \
    tar -zxf geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz -C /usr/local/bin && \
    chmod +x /usr/local/bin/geckodriver && \
    rm geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz

RUN FIREFOX_SETUP=firefox-setup.tar.bz2 && \
    apt-get purge firefox && \
    wget -O $FIREFOX_SETUP "https://download.mozilla.org/?product=firefox-latest&os=linux64" && \
    tar xjf $FIREFOX_SETUP -C /opt/ && \
    ln -s /opt/firefox/firefox /usr/bin/firefox && \
    rm $FIREFOX_SETUP

#COPY requirements.txt .
#RUN pip install --no-cache-dir -r requirements.txt
#RUN rm requirements.txt

#ENV LANG C.UTF-8
#ENV LC_ALL C.UTF-8
#ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app

COPY . .
RUN pip install --no-cache-dir -r requirements.txt && \
    rm requirements.txt

CMD ["python", "selenium_open.py"]