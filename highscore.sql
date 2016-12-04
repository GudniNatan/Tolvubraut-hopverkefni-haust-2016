--create database if not exists 0403983099_highScores;

create table if not exists data(
	id int not null auto_increment,
	name varchar(255) not null,
	score int not null,
	primary key (id)
);

use database 0403983099_highScores;

insert into data(name, score)
values ('njalsson', 21);
