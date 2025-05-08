FROM python:3.13

WORKDIR /usr/src/app

RUN pip install pip -U

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY birdbot birdbot/

CMD [ "python3", "-m", "birdbot" ]