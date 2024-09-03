FROM python:3.11

WORKDIR /src

COPY requirements.txt requirements.txt
COPY pytest.ini /pytest.ini
COPY .env.test /.env.test

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
