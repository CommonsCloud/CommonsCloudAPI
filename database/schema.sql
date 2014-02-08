DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

CREATE TABLE attachment (
    id serial PRIMARY KEY,
    owner serial,
    created timestamp,
    status boolean,
    filename varchar(226) NOT NULL,
    filepath varchar(255) NOT NULL,
    filetype varchar(140) NOT NULL,
    filesize integer
);


CREATE TABLE field (
    id serial PRIMARY KEY,
    label varchar(255) NOT NULL,
    name varchar(255) NOT NULL,
    help_text varchar(255) NOT NULL,
    data_type varchar(255) NOT NULL,
    field_type varchar(255) NOT NULL,
    relationship varchar(255) NOT NULL,
    required boolean,
    weight integer,
    status boolean
);

CREATE TABLE template (
    id serial PRIMARY KEY,
    name varchar(255) NOT NULL,
    description varchar(255) NOT NULL,
    storage varchar(255) NOT NULL,
    owner serial,
    publicly_viewable boolean,
    crowd_sourcing boolean,
    moderate boolean,
    created timestamp,
    status boolean
);

CREATE TABLE template_fields (
    template serial,
    field serial
);

CREATE TABLE application (
  id serial PRIMARY KEY,
  name varchar(255) NOT NULL,
  description varchar(255) NOT NULL,
  owner serial,
  created timestamp,
  status boolean
);

CREATE TABLE application_templates (
    application serial,
    template serial
);

CREATE TABLE statistic (
    id serial PRIMARY KEY,
    template serial REFERENCES template (id),
    field serial REFERENCES field (id),
    name varchar(255) NOT NULL,
    units varchar(255) NOT NULL,
    math_type varchar(24) NOT NULL,
    owner serial,
    created timestamp,
    status boolean
);

CREATE TABLE permission (
    id serial PRIMARY KEY,
    type varchar(255) NOT NULL,
    type_id serial,
    can_view boolean,
    can_create boolean,
    can_edit_own boolean,
    can_edit_any boolean,
    can_delete_own boolean,
    can_delete_any boolean,
    is_admin boolean,
    is_moderator boolean
);

CREATE TABLE role (
    id serial PRIMARY KEY,
    name varchar(255) NOT NULL,
    description varchar(255) NOT NULL
);

CREATE TABLE "user" (
    id serial PRIMARY KEY,
    firstname varchar(255),
    lastname varchar(255),
    title varchar(255),
    bio varchar(255),
    email varchar(255) NOT NULL,
    password varchar(255) NOT NULL,
    active boolean,
    confirmed_at timestamp
);

    CREATE TABLE user_roles (
        "user" serial,
        role serial
    );

    CREATE TABLE user_permissions (
        "user" serial REFERENCES "user" (id),
        permission serial REFERENCES "permission" (id)
    );
