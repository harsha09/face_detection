docker build -f ./docker/app/Dockerfile -t facerecog_app .
docker build -f ./docker/db/Dockerfile -t facerecog_db .

docker-compose up

docker-compose exec db bash

execute
    chmod 755 /var/local/db/create_database_tables.sh
    /var/local/db/create_database_tables.sh     <!-- Creates database and corresponding tables -->

<!-- gunicorn -w 4 -b localhost:5000 facedetection:app
celery worker -A facedetection.celery --loglevel=info -->
i7h3ogbr57lu
