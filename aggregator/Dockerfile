FROM python:3.10

COPY . /aggregator/

RUN apt-get update && apt-get install libpq-dev
RUN pip install -r /aggregator/requirements.txt

CMD python /aggregator/src/aggregator.py
