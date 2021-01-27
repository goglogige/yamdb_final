FROM python:3.8.5

WORKDIR /code
COPY . /code
RUN pip install -r requirements.txt
RUN python manage.py collectstatic --no-input 
CMD gunicorn api_yamdb.wsgi:application --bind 0.0.0.0:9000 && python manage.py migrate

