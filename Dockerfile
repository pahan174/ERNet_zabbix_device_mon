FROM python:slim

RUN pip install --upgrade pip

COPY . /app

WORKDIR  /app

RUN pip install -r requirements.txt

CMD ["python", "start.py"]