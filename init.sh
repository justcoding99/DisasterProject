docker-compose up --build &
python -m venv env
source env/bin/activate
pip install -r requirements.txt
cd disaster_project
touch .env
echo "DEVELOPMENT=True" > .env
python manage.py collectstatic
python manage.py migrate
python manage.py runserver


