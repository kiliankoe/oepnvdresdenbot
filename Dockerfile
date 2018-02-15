FROM python:3.6-slim

WORKDIR /oepnvdd_bot

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
