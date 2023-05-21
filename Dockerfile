FROM python:3

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN ./manage.py migrate
EXPOSE 8000
ENTRYPOINT ["./manage.py", "runserver", "0.0.0.0:8000"]
