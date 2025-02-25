CREATE DATABASE rp;

CREATE USER 'username'@'localhost' IDENTIFIED BY 'user_password';
GRANT ALL PRIVILEGES ON *.* TO 'username'@'localhost';

USE rp;
create table sd (request_id varchar(255), request_object varchar(1024));
create table sdo (id int NOT NULL AUTO_INCREMENT, request_id varchar(255), signed_data_object TEXT(153600), error varchar(255));