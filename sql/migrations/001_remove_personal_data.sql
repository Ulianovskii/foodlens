-- Удаляем поля first_name, last_name из таблицы users
ALTER TABLE users DROP COLUMN IF EXISTS first_name;
ALTER TABLE users DROP COLUMN IF EXISTS last_name;