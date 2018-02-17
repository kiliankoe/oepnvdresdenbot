FROM python:3.6

WORKDIR /oepnvdd_bot

RUN pip install pipenv
COPY Pipfile .
COPY Pipfile.lock .
RUN pipenv install

COPY . .

ENTRYPOINT ["pipenv", "run"]
CMD ["python", "main.py"]
