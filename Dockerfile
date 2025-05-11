FROM python:3-slim
WORKDIR /programas/ingesta
RUN pip3 install boto3 psycopg2-binary 
COPY . .
CMD [ "python3", "./ingesta-gest.py" ]
