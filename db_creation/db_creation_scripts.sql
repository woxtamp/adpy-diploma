create table if not exists vk_user_token (
	id serial primary key,
	vk_id integer not null unique,
	vk_user_token varchar(1000) not null,
    vk_token_lifetime integer not null
);

create table if not exists vk_user (
	id serial primary key,
	vk_id integer not null unique references vk_user_token(vk_id),
	age integer not null,
	sex integer not null,
	city_name varchar(250) not null,
	city_id integer
);

create table if not exists vk_search_params (
	id serial primary key,
	vk_id integer not null unique references vk_user(vk_id),
	age_from integer not null,
	age_to integer not null,
	sex integer not null,
	city_name varchar(250) not null,
	city_id integer
);

create table if not exists vk_find_user (
	id serial primary key,
	vk_id integer not null references vk_search_params(vk_id),
	vk_search_id integer not null,
	constraint vk_id_vk_search_id_vk_find_user unique (vk_id, vk_search_id)
);
