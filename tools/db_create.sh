CREATE DATABASE db_name;

CREATE USER 'username'@'localhost' IDENTIFIED BY 'user_password';
GRANT ALL PRIVILEGES ON *.* TO 'username'@'localhost';

USE rp;
create table sd (request_id varchar(255), request_object text);
create table sdo (id int NOT NULL AUTO_INCREMENT, request_id varchar(255), signed_data_object mediumtext, error varchar(255), PRIMARY KEY (id));