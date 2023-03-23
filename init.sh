docker-compose up --build &
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
cd disaster_project
touch .env
echo "DEVELOPMENT=True" > .env
python3 manage.py collectstatic --noinput
python3 manage.py migrate
python3 manage.py runserver


