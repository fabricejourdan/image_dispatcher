FROM python:3.9.9

LABEL maintainer="datalab-mi"

RUN mkdir /workspace && chown -R 42420:42420 /workspace

WORKDIR /workspace

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python" , "app.py" ,"--config", "/home/fabrice/fabrice.yaml"]
