From python:3.9

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

CMD ["gunicorn", "--bind=0.0.0.0:5000", "--workers=2", "myapp:app"]


