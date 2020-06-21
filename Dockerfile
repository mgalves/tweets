FROM python:3.7.2-alpine

RUN mkdir /opt/tweets
WORKDIR /opt/tweets

COPY ./requirements.txt /opt/tweets/requirements.txt
COPY src/ ./

RUN pip install -r requirements.txt
