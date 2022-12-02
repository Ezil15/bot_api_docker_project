FROM python:3.10.0-alpine

WORKDIR /usr/src/app

COPY ./requirements.txt .

RUN pip install -U pip && \
pip install --no-cache -r requirements.txt

COPY ./bot .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]