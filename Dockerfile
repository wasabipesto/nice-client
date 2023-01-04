FROM python:3.10-bullseye

ENV PYTHONUNBUFFERED=1

ENV NICE_VERSION=1.0.0

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "./main.py"]