FROM python:3.10

RUN apt-get update && apt-get install libpq-dev

COPY . /api/

RUN pip install -r /api/requirements.txt

CMD flask run --host=0.0.0.0
