drop table if exists images;
create table images (
  id integer primary key autoincrement,
  f integer not null,
  n interger not null,
  file text not null
);

drop table if exists drawings;
create table drawings ( 
    id integer primary key autoincrement,
    file text not null,
    ts_created integer not null,
    ts_moderated integer, 
    is_approved integer default 0,
    creator_mail text,
    image integer,
    FOREIGN KEY(image) REFERENCES images(id)
);


drop table if exists users;
create table users (
    shortname text primary key,
    name text not null,
    password text not null
);
