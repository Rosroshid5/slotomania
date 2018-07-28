FROM python:3.7
ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code
COPY dev-requirements.txt .
RUN pip install -r dev-requirements.txt
ADD . /code

ENV PYTHONPATH .
