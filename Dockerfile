FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

RUN pip install jinja2

COPY ./app /app
