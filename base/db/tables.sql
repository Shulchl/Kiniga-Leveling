CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS public.setup (
    id integer PRIMARY KEY, 
    guild text COLLATE pg_catalog."default" NOT NULL UNIQUE,
    message_id text COLLATE pg_catalog."default" NOT NULL,
    role_id text COLLATE pg_catalog."default" NOT NULL,
    owner_id integer NOT NULL
);

CREATE TABLE IF NOT EXISTS public.users (
    id text COLLATE pg_catalog."default" NOT NULL,
    rank integer NOT NULL,
    xp integer NOT NULL,
    xptotal integer NOT NULL,
    info text COLLATE pg_catalog."default",
    spark integer DEFAULT 0,
    iventory_id uuid DEFAULT uuid_generate_v4(),
    birth text DEFAULT '???',
    ori integer DEFAULT 0,
    rank_id bigint,
    user_name text NOT NULL,
    email VARCHAR, 
    PRIMARY KEY (iventory_id)
);

CREATE TABLE IF NOT EXISTS public.iventory (
    iventory_id uuid REFERENCES public.users (iventory_id) ON DELETE CASCADE ON UPDATE CASCADE,
    itens text,
    car uuid,
    title uuid,
    mold uuid,
    banner uuid,
    badge text
);

CREATE TABLE IF NOT EXISTS public.ranks (
    id uuid DEFAULT uuid_generate_v4() UNIQUE,
    name text UNIQUE,
    lvmin integer,
    r integer,
    g integer,
    b integer,
    badges text,
    roleid text,
    imgxp text,
    rankid UUID DEFAULT uuid_generate_v4(),
    PRIMARY KEY (rankid)
);

CREATE TABLE IF NOT EXISTS public.molds (
    id uuid DEFAULT uuid_generate_v4(),
    name text COLLATE pg_catalog."default" NOT NULL UNIQUE,
    img text COLLATE pg_catalog."default" NOT NULL,
    imgxp text,
    img_bdg text NOT NULL,
    type_ text DEFAULT 'Moldura',
    img_profile text NOT NULL,
    value integer DEFAULT 0,
    canbuy boolean DEFAULT True,
    img_mold_title text,
    lvmin int DEFAULT 0,
    group_ text DEFAULT 'rank',
    category text DEFAULT 'Comum',
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.badges (
    name text COLLATE pg_catalog."default" NOT NULL UNIQUE,
    img text COLLATE pg_catalog."default" NOT NULL,
    canbuy boolean DEFAULT true,
    value integer DEFAULT 0,
    type_ text DEFAULT 'Badge',
    lvmin integer DEFAULT 0,
    group_ text DEFAULT 'rank',
    category text DEFAULT 'Comum',
    id uuid DEFAULT uuid_generate_v4(),
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.banners (
    name text COLLATE pg_catalog."default" NOT NULL UNIQUE,
    img_loja text COLLATE pg_catalog."default" NOT NULL,
    img_perfil text COLLATE pg_catalog."default" NOT NULL,
    canbuy boolean DEFAULT true,
    value integer DEFAULT 0,
    type_ text DEFAULT 'Banner',
    id uuid DEFAULT uuid_generate_v4(),
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.cars (
    name text COLLATE pg_catalog."default" NOT NULL UNIQUE,
    localimg text COLLATE pg_catalog."default" NOT NULL,
    canbuy boolean DEFAULT true,
    value integer DEFAULT 0,
    type_ text DEFAULT 'Carro',
    id uuid DEFAULT uuid_generate_v4(),
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.utilizaveis (
    id uuid DEFAULT uuid_generate_v4(),
    name text NOT NULL,
    canbuy boolean DEFAULT true,
    value integer DEFAULT 0,
    type_ text DEFAULT 'Utilizavel',
    img text NOT NULL,
    category text DEFAULT 'Comum',
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.itens (
    id SERIAL PRIMARY KEY,
    name text COLLATE pg_catalog."default" NOT NULL,
    type_ text COLLATE pg_catalog."default" NOT NULL,
    value integer,
    img text COLLATE pg_catalog."default" NOT NULL,
    imgd text COLLATE pg_catalog."default",
    img_profile text COLLATE pg_catalog."default",
    lvmin integer,
    canbuy boolean,
    dest boolean,
    limitedtime timestamp without time zone,
    details CHAR,
    item_type_id uuid DEFAULT uuid_generate_v4() UNIQUE,
    group_ text DEFAULT 'rank',
    category text DEFAULT 'Comum'
);

CREATE TABLE IF NOT EXISTS public.shop (
    id INTEGER REFERENCES public.itens (id) ON DELETE CASCADE ON UPDATE CASCADE,
    item_type_id UUID REFERENCES public.itens (item_type_id) ON DELETE CASCADE ON UPDATE CASCADE UNIQUE,
    name text COLLATE pg_catalog."default" NOT NULL,
    value integer,
    lvmin integer,
    dest boolean,
    limitedtime timestamp without time zone,
    img text COLLATE pg_catalog."default",
    details text COLLATE pg_catalog."default",
    type_ text,
    category text DEFAULT 'Comum'
);
