FROM python:3.10-slim
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*
COPY ./requirements.txt requirements.txt
RUN pip install -r ./requirements.txt
COPY ./app.py app.py
ENTRYPOINT [ "python" ]
CMD [ "app.py" ]
EXPOSE 5000
