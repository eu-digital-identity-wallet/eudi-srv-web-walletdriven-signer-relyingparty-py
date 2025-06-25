CREATE DATABASE db_name;

CREATE USER db_username@'localhost' IDENTIFIED BY db_user_password;
GRANT ALL PRIVILEGES ON db_name.* TO db_username@'localhost';

USE db_name;
create table sd (request_id varchar(255), request_object text);
create table sdo (id int NOT NULL AUTO_INCREMENT, request_id varchar(255), signed_data_object mediumtext, error varchar(255), PRIMARY KEY (id));