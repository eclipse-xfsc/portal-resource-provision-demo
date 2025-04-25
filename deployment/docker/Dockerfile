FROM python:3.11.1-bullseye

WORKDIR /app

COPY ./templates ./templates

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./main.py /app/
COPY ./kubernetes_services.py /app/
COPY ./models.py /app/
COPY ./security_utils.py /app/
COPY ./kong_services.py /app/
COPY ./templates_services.py /app/

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8800"]