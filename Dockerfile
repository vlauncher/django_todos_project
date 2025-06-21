FROM python:3.13-alpine

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "django_todos_project.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
