FROM python:3.7.3

MAINTAINER Abd. Jahiduddin <abd.jahiduddin@gmail.com>

WORKDIR /userdashboard

COPY requirements.txt /userdashboard
RUN pip install --no-cache-dir -r requirements.txt

COPY . /userdashboard

CMD [ "python3", "manage.py", "runserver", "0.0.0.0:8000" ]
