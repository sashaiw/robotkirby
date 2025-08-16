FROM python:3.11

WORKDIR /usr/src/app

RUN pip install pip -U

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY robotkirby robotkirby/

CMD [ "python3", "-m", "robotkirby" ]