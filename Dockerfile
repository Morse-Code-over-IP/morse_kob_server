FROM python:3

WORKDIR /app
ADD KOBServer.py /app
ADD pins.py /app

RUN mkdir www www/logs
ADD info.html /app/www/

EXPOSE 7890/udp

CMD ["python", "KOBServer.py", "./www"]