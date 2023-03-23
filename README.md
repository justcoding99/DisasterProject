## Installation
You can either execute init.sh script or install step by step;


`./init.sh`

or

```
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
```


Then open `http://127.0.0.1:8000`

## Adding a new pip package

```
pip install add x
pip freeze > requirements.txt
```

