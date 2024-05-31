FROM python:3.11-slim

WORKDIR /app

COPY ./source /app/

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-u", "paperless-search.py"]