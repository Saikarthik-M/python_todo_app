FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*
RUN pip install -r ./requirements.txt
ENTRYPOINT [ "python" ]
CMD [ "app.py" ]
EXPOSE 5000
