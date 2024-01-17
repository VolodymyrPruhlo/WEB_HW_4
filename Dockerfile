FROM python:3.12

ENV APP_HOME /app

WORKDIR $APP_HOME

COPY . $APP_HOME

VOLUME /storage/data.json

EXPOSE 3000

ENTRYPOINT ["python", "main.py"]
