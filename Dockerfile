FROM python:3.10-slim

WORKDIR /code
COPY . .
#COPY poetry.lock .
#COPY pyproject.toml .
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8000

CMD python ./manage.py runserver 0.0.0.0:8000