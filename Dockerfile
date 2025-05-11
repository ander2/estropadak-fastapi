FROM python:3.13.1-slim
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./app /code/app
COPY ./log_conf.yaml /code/
CMD ["uvicorn", "app.main:api", "--host", "0.0.0.0", "--workers", "4", "--proxy-headers", "--port", "80", "--log-config", "log_conf.yaml"]