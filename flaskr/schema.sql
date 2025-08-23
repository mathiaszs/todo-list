-- sqlite3 flaskr/flaskr.sqlite
-- sqlite3 instance/flaskr.sqlite
-- flask --app flaskr init-db

DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE tasks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  title TEXT NOT NULL,
  description TEXT NOT NULL, 
  term DATE,
  FOREIGN KEY (author_id) REFERENCES user (id)
);