FROM python:3.8.12-slim-buster as base

WORKDIR /app

RUN apt-get update && apt-get install curl --no-install-recommends -y && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /app

RUN python3 -m pip install -r requirements.txt

CMD ["uvicorn", "app:app", "--host","0.0.0.0", "--port","5000"]