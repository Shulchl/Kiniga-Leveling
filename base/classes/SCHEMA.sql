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
    itens JSON,
    car INT,
    title INT,
    moldura INT,
    banner INT,
    badge JSON DEFAULT '{}',
    FOREIGN KEY (ID) REFERENCES users(ID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS banners (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(60) NOT NULL,
    img_loja VARCHAR(255),
    img_profile VARCHAR(255),
    value INT DEFAULT 0,
    value_ori INT DEFAULT 0,
    canbuy BOOLEAN DEFAULT true,
    category VARCHAR(20) DEFAULT 'Comum',
    type_ text DEFAULT 'Banner',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS badges (
    ID INT PRIMARY KEY AUTO_INCREMENT,
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
    ID INT PRIMARY KEY AUTO_INCREMENT,
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
    ID INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(60) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS cars (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(60) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS items (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    ID_ITEM INT,
    name VARCHAR(60) NOT NULL,
    details VARCHAR(255),
    img VARCHAR(255),
    imgd VARCHAR(255),
    img_profile VARCHAR(255),

    type_ VARCHAR(20),
    value INT DEFAULT 0,
    value_ori INT DEFAULT 0,
    canbuy BOOLEAN DEFAULT true,
    lvmin INT,
    group_ VARCHAR(10),
    category VARCHAR(20) DEFAULT 'Comum',
    dest BOOLEAN DEFAULT false,
    limitedtime timestamp,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (ID_ITEM) REFERENCES banners(ID) ON DELETE CASCADE,
    FOREIGN KEY (ID_ITEM) REFERENCES badges(ID) ON DELETE CASCADE,
    FOREIGN KEY (ID_ITEM) REFERENCES molds(ID) ON DELETE CASCADE,
    FOREIGN KEY (ID_ITEM) REFERENCES consumables(ID) ON DELETE CASCADE,
    FOREIGN KEY (ID_ITEM) REFERENCES cars(ID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS shop (
    ID INT PRIMARY KEY,
    name VARCHAR(60) NOT NULL,
    details VARCHAR(255),
    img VARCHAR(255),
    value INT DEFAULT 0,
    value_ori INT DEFAULT 0,
    lvmin INT,
    dest BOOLEAN DEFAULT false,
    type_ VARCHAR(20),
    category VARCHAR(20) DEFAULT 'Comum',
    canbuy BOOLEAN DEFAULT true,
    group_ VARCHAR(10),
    limitedtime timestamp,
    FOREIGN KEY (ID) REFERENCES items(ID)
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