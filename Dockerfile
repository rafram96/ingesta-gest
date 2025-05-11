FROM python:3-slim
WORKDIR /programas/ingesta
RUN mkdir -p /home/ubuntu/.aws
RUN pip3 install boto3 psycopg2-binary python-dotenv
COPY . .
RUN chmod +x ./ingesta-gest.py
CMD [ "python3", "./ingesta-gest.py" ]
FROM python:3-slim
