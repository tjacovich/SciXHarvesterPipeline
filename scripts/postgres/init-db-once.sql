-- If this file is in /docker-entrypoint-initdb.d/, it will be loaded
-- only if /var/lib/postgresql/data does not exist (i.e., the first time the container is created with an empty volume)

-- *ALTER SYSTEM writes the given parameter setting to the postgresql.auto.conf file, which is read in addition to postgresql.conf
ALTER SYSTEM SET wal_level = logical; -- Required by Kafka Connect to replicate data
SELECT pg_reload_conf(); -- Causes all processes of the PostgreSQL server to reload their configuration files

-- -- Students data
-- CREATE TABLE IF NOT EXISTS admission (student_id INTEGER, gre INTEGER, toefl INTEGER, cpga DOUBLE PRECISION, admit_chance DOUBLE PRECISION, CONSTRAINT student_id_pk PRIMARY KEY (student_id));
-- CREATE TABLE IF NOT EXISTS research (student_id INTEGER, rating INTEGER, research INTEGER, PRIMARY KEY (student_id));
-- COPY admission FROM '/tmp/admit_1.csv' DELIMITER ',' CSV HEADER;
-- COPY research FROM '/tmp/research_1.csv' DELIMITER ',' CSV HEADER;

-- Shipment data
-- CREATE TABLE IF NOT EXISTS shipments
-- (
--     id bigint NOT NULL,
--     order_id bigint NOT NULL,
--     created character varying(255) COLLATE pg_catalog."default",
--     status character varying(25) COLLATE pg_catalog."default",
-- 	user_id integer NOT NULL,
--     CONSTRAINT shipments_pkey PRIMARY KEY (id)
-- );

-- INSERT INTO shipments values (30500,10500,'2021-01-21','COMPLETED',1);
-- INSERT INTO shipments values (31500,11500,'2021-04-21','COMPLETED',1);
-- INSERT INTO shipments values (32500,12500,'2021-05-31','PROCESSING',2);

-- CREATE TABLE IF NOT EXISTS roles (
--   id INT PRIMARY KEY     NOT NULL,
--   role_name VARCHAR(30) UNIQUE NOT NULL,
--   created_at timestamp with time zone default NOW()
-- );

-- INSERT INTO roles (id, role_name)values (1,'ADMIN');
-- INSERT INTO roles (id, role_name) values (2,'USER');

-- CREATE TABLE IF NOT EXISTS users
-- (
--     id integer NOT NULL,
--     role_id integer NOT NULL,
--     username character varying(15) COLLATE pg_catalog."default" NOT NULL,
--     created_at timestamp with time zone NOT NULL DEFAULT now(),
--     CONSTRAINT primary_key PRIMARY KEY (id),
--     CONSTRAINT role_fk FOREIGN KEY (role_id)
--         REFERENCES roles (id) MATCH SIMPLE
--         ON UPDATE NO ACTION
--         ON DELETE NO ACTION
-- );

-- INSERT INTO users (id, role_id, username)values (1,1,'albert');
-- INSERT INTO users (id, role_id, username)values (2,2,'sergi');
