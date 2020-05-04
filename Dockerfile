FROM python:3.7-slim

RUN adduser bestmadrid

WORKDIR /home/bestmadrid
COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install --upgrade pip
RUN venv/bin/pip install wheel
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn pymysql

COPY app app
COPY migrations migrations
COPY BOSS.py config.py boot.sh ./
RUN chmod a+x boot.sh

ENV FLASK_APP BOSS.py

RUN chown -R bestmadrid:bestmadrid ./
USER bestmadrid

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
