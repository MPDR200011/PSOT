FROM python:3.10

RUN apt-get update && apt-get install libpq-dev

COPY . /aggregator/

RUN pip install -r /aggregator/requirements.txt

CMD python -u /aggregator/src/aggregator.py
