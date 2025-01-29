FROM python:3.9-alpine

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

RUN python -m pip install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

EXPOSE 2034

ENTRYPOINT ["python3"]

CMD ["-m", "swagger_server", "--host", "0.0.0.0", "--port", "2034"]
