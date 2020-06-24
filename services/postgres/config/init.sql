DROP DATABASE IF EXISTS studentdb;
CREATE DATABASE studentdb;

CREATE USER student
WITH SUPERUSER PASSWORD 'student';

GRANT ALL PRIVILEGES ON DATABASE studentdb TO student;
