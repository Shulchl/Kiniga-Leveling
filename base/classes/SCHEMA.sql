CREATE TABLE IF NOT EXISTS users (
    ID BIGINT PRIMARY KEY,
    user_name VARCHAR(60) NOT NULL,
    email VARCHAR(89),
    info VARCHAR(255),
    rank integer NOT NULL,
    xp integer NOT NULL,
    xptotal integer NOT NULL,
    spark integer DEFAULT 0,
    ori integer DEFAULT 0,
    birth VARCHAR(5) DEFAULT '???',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS inventory (
    ID BIGINT PRIMARY KEY,
    itens JSON DEFAULT '{"Badge":{"rank":{"ids":[]},"equipe":{"ids":[]},"moldura":{"ids":[]},"apoiador":{"ids":[]}},"Carro":{"ids":[]},"Banner":{"ids":[]},"Moldura":{"rank":{"ids":[]},"equipe":{"ids":[]},"moldura":{"ids":[]},"apoiador":{"ids":[]}},"Utilizavel":{"ids":{}}}',
    car INT,
    title INT,
    moldura INT,
    banner INT,
    badge JSON DEFAULT '{}',
    FOREIGN KEY (ID) REFERENCES users(ID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS banners (
    ID VARCHAR(36) PRIMARY KEY DEFAULT UUID(),
    name VARCHAR(60) NOT NULL,
    img_loja VARCHAR(255),
    img_profile VARCHAR(255),
    value INT DEFAULT 0,
    value_ori INT DEFAULT 0,
    canbuy BOOLEAN DEFAULT true,
    category VARCHAR(20) DEFAULT 'Comum',
    type_ text DEFAULT 'Banner',
    lvmin INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS badges (
    ID VARCHAR(36) PRIMARY KEY DEFAULT UUID(),
    name VARCHAR(60) NOT NULL,
    img VARCHAR(255),
    type_ VARCHAR(20) DEFAULT 'Badge',
    value INT DEFAULT 0,
    value_ori INT DEFAULT 0,
    canbuy BOOLEAN DEFAULT true,
    lvmin INT DEFAULT 0,
    group_ VARCHAR(10) DEFAULT 'rank',
    category VARCHAR(20) DEFAULT 'Comum'
);

CREATE TABLE IF NOT EXISTS molds (
    ID VARCHAR(36) PRIMARY KEY DEFAULT UUID(),
    name VARCHAR(60) NOT NULL,
    img VARCHAR(255),
    imgxp VARCHAR(255),
    img_bdg VARCHAR(255),
    img_profile VARCHAR(255),
    img_mold_title VARCHAR(255),
    type_ VARCHAR(20) DEFAULT 'Moldura',
    value INT DEFAULT 0,
    value_ori INT DEFAULT 0,
    canbuy BOOLEAN DEFAULT true,
    lvmin INT DEFAULT 0,
    group_ VARCHAR(10) DEFAULT 'rank',
    category VARCHAR(20) DEFAULT 'Comum',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS consumables (
    ID VARCHAR(36) PRIMARY KEY DEFAULT UUID(),
    name VARCHAR(60) NOT NULL,
    type_ VARCHAR(20) DEFAULT 'Consumable',
    value INT DEFAULT 0,
    value_ori INT DEFAULT 0,
    canbuy BOOLEAN DEFAULT true,
    lvmin INT DEFAULT 0,
    category VARCHAR(20) DEFAULT 'Comum',
    img_loja VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS cars (
    ID VARCHAR(36) PRIMARY KEY DEFAULT UUID(),
    name VARCHAR(60) NOT NULL,
    value INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS items (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    ID_ITEM VARCHAR(36),
    UNIQUE KEY(ID_ITEM),
    type_ VARCHAR(20) NOT NULL,
    group_ VARCHAR(10),
    category VARCHAR(20) NOT NULL,
    limitedtime timestamp,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS shop (
    ID INT PRIMARY KEY,
    limitedtime timestamp,
    FOREIGN KEY (ID) REFERENCES items(ID) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS ranks (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(60) UNIQUE,
    lvmin INT,
    r INT,
    g INT,
    b INT,
    roleid VARCHAR(20),
    badges VARCHAR(255),
    imgxp VARCHAR(255)
);