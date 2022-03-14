FROM python:2

WORKDIR /app
ADD KOBServer.py /app
ADD pins.py /app

RUN mkdir www www/logs
ADD info.html /app/www/
RUN 

CMD ["python", "KOBServer.py", "./www"]