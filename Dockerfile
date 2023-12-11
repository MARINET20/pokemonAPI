FROM python:3-alpine

ADD requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

ADD main.py /main.py

ENV FLASK_APP /main.py

CMD flask run --host=0.0.0.0