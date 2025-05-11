FROM python:3-slim
WORKDIR /programas/ingesta
RUN mkdir -p /home/ubuntu/.aws
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN chmod +x ./ingesta-gest.py
CMD [ "python3", "./ingesta-gest.py" ]
FROM python:3-slim
