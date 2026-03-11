FROM python:3.13.0-slim

WORKDIR /app

COPY . ./

RUN pip install -e .
RUN playwright install
RUN newspaper4k install

CMD ["python", "-m", "news_room_bot"]
