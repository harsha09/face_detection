PG="psql --username ${POSTGRES_USER}"

echo "Creating role facerecog............"
$PG <<DOITALL
CREATE ROLE facerecog WITH LOGIN PASSWORD 'ideeo@519';
\q
DOITALL

echo "Creating database ${POSTGRES_DB}.............."
$PG <<DOITALL
CREATE DATABASE ${POSTGRES_DB} OWNER =  facerecog;
DOITALL

PG="psql --username ${POSTGRES_USER} --dbname facerecogdb"

echo "Creating the required tables ....................."

$PG <<DOITALL
create extension cube;
create extension pgcrypto;

CREATE TABLE ${POSTGRES_DB}.public.app (
	appid varchar(50) NOT NULL,
	appname varchar(80) NOT NULL,
	appkey varchar(48) NOT NULL
);

ALTER TABLE ${POSTGRES_DB}.public.app OWNER TO facerecog;
GRANT ALL ON TABLE ${POSTGRES_DB}.public.app TO facerecog;


CREATE TABLE ${POSTGRES_DB}.public.im_data (
	id varchar(200) NULL,
	"data" cube NULL,
	appid varchar(50) NOT NULL 
);

ALTER TABLE ${POSTGRES_DB}.public.im_data OWNER TO facerecog;


CREATE TABLE ${POSTGRES_DB}.public."user" (
	userid serial NOT NULL,
	username varchar(50) NOT NULL,
	"password" varchar(96) NOT NULL,
	"role" varchar NULL,
	CONSTRAINT user_pk PRIMARY KEY (username, userid)
);

ALTER TABLE ${POSTGRES_DB}.public."user" OWNER TO facerecog;
GRANT ALL ON TABLE ${POSTGRES_DB}.public."user" TO facerecog;
DOITALL
