FROM python:3.10

COPY . /scanner/

RUN apt-get update
RUN apt-get install -y aircrack-ng pciutils iproute2
RUN pip install -r /scanner/requirements.txt

CMD python /scanner/scan.py
