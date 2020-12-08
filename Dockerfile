FROM ubuntu:18.04

COPY . ./twitter

WORKDIR '/twitter/'

RUN apt-get update \
&& apt-get install -y python3-pip python3-dev firefox\  
   xvfb wget curl\
&& cd /usr/local/bin \
&& ln -s /usr/bin/python3 python \
&& pip3 install --upgrade pip

#set docker tzdata
ENV TZ=Europe/Paris
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install tzdata

#install geckodriver
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.27.0/geckodriver-v0.27.0-linux64.tar.gz\
&& tar -xvzf geckodriver-v0.27.0-linux64.tar.gz \
&& chmod 777 geckodriver\
&& cp geckodriver $HOME

ENV LANG C.UTF-8
#pwd- twitter/
ENV PATH "$PATH:$PWD"
#home- root/
ENV PATH "$PATH:$HOME"
#python path
ENV PATH "$PATH:/root/.local/bin"

#install dependencies
RUN pip3 install --use-feature=2020-resolver --no-cache-dir -r driver_requirements.txt

#setup driver application
RUN  pip3 install --user .

CMD [ "python3","run_twitter.py" ]


