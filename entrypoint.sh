#!/bin/sh
until pg_isready -h db -p 5432 -U ${DATABASE_USER} -d ${DATABASE_NAME}; do
  echo "Waiting for database to be ready..."
  sleep 2
done

python ./manage.py migrate
python ./manage.py runserver 0.0.0.0:8000