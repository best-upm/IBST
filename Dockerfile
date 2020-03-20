FROM python:3.7-alpine

RUN adduser -D BEST_Madrid

WORKDIR /home/ibst

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install --upgrade pip
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn pymysql

COPY app app
COPY migrations migrations
COPY BOSS.py config.py boot.sh ./
RUN chmod a+x boot.sh

ENV FLASK_APP BOSS.py

RUN chown -R BEST_Madrid:BEST_Madrid ./
USER BEST_Madrid

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
