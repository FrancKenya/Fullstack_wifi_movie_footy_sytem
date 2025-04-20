 ### 1. Create PostgreSQL DB

sudo -u postgres psql


### 2. Create user & DB:

CREATE DATABASE wifi_db;
CREATE USER wifi_user WITH PASSWORD 'wifi_pass';
ALTER ROLE wifi_user SET client_encoding TO 'utf8';
ALTER ROLE wifi_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE wifi_user SET timezone TO 'EAT';
GRANT ALL PRIVILEGES ON DATABASE wifi_db TO wifi_user;
\q

### 3.  Run Migrations & Start Server
python manage.py makemigrations
python manage.py migrate
python manage.py runserver


### 4. Run Redis & Celery
redis-server
celery -A wifi_retail worker -l info
