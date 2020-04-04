SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;
DROP DATABASE IF EXISTS chat;

CREATE DATABASE chat;
USE chat;

DROP TABLE IF EXISTS history;
DROP TABLE IF EXISTS user;

CREATE TABLE history
(
    id INT NOT NULL AUTO_INCREMENT,
    username VARCHAR (20),
    message VARCHAR (200),
    time VARCHAR (20),
    PRIMARY KEY (id)
);

CREATE TABLE user
(
    id INT NOT NULL AUTO_INCREMENT,
     username VARCHAR (32),
     password VARCHAR (32),
     token VARCHAR (200),
     PRIMARY KEY (id)
);
