# Ptoject name: Todolist 
## The "Calendar" provides opportunities to work with meetings, which will allow you to work with goals and track progress on them.
******
## Stack:
- python3.10
- Django
- Postgres

## Project launch
1. Create virtual environment
2. Install dependencies from requirements.txt:
- pip install -r requirements.txt
3. install dependencies from .env file:
- install your variables or can copy the default variables from todolist/.env.example
4. Launch docker for database:
- docker run --name todolist -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres
5. roll up migrations:
- python ./manage.py makemigraitons
- python ./manage.py migrate
5. Launch project
- python ./manage.py runserver