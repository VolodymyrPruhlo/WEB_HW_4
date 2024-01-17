FROM python:3.12

ENV APP_HOME /app

WORKDIR $APP_HOME

COPY . /app

VOLUME /storage/data.json

EXPOSE 80

CMD python3 main.py
