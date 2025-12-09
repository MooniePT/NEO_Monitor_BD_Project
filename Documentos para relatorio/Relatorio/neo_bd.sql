------------------------------------------------------
-- ASTEROIDE
------------------------------------------------------
CREATE TABLE Asteroide (
    id_asteroide           INT IDENTITY(1,1) PRIMARY KEY,
    id_csv                 INT NULL,
    id_spk                 INT NULL,
    nome_completo          VARCHAR(255) NULL,
    pdes                   VARCHAR(20) NULL,
    nome_asteroide         VARCHAR(100) NULL,
    prefixo                VARCHAR(20) NULL,
    flag_neo               BIT NULL,
    flag_pha               BIT NULL,
    H_mag                  DECIMAL(5,2) NULL,
    diametro_km            DECIMAL(10,4) NULL,
    diametro_sigma_km      DECIMAL(10,4) NULL,
    albedo                 DECIMAL(6,4) NULL,
    data_descoberta        DATE NULL
);

------------------------------------------------------
-- CLASSE_ORBITAL
------------------------------------------------------
CREATE TABLE Classe_Orbital (
    codigo_classe          VARCHAR(20) NOT NULL PRIMARY KEY,
    descricao              VARCHAR(255) NULL
);

------------------------------------------------------
-- SOLUCAO_ORBITAL
------------------------------------------------------
CREATE TABLE Solucao_Orbital (
    id_solucao_orbital     INT IDENTITY(1,1) PRIMARY KEY,
    id_asteroide           INT NOT NULL,
    codigo_classe          VARCHAR(20) NOT NULL,
    id_orbita_externa      VARCHAR(50) NULL,

    epoca_jd               DECIMAL(15,5) NULL,
    epoca_mjd              DECIMAL(15,5) NULL,
    epoca_cal              VARCHAR(25) NULL,
    equinocio              VARCHAR(10) NULL,

    excentricidade         DECIMAL(12,10) NULL,
    semi_eixo_maior_ua     DECIMAL(13,10) NULL,
    perielio_ua            DECIMAL(13,10) NULL,
    inclinacao_graus       DECIMAL(10,6) NULL,
    long_no_asc_graus      DECIMAL(10,6) NULL,
    arg_perielio_graus     DECIMAL(10,6) NULL,
    anomalia_media_graus   DECIMAL(10,6) NULL,
    afelio_ua              DECIMAL(13,10) NULL,
    movimento_medio_graus_dia DECIMAL(12,8) NULL,
    tempo_perielio_jd      DECIMAL(15,5) NULL,
    tempo_perielio_cal     VARCHAR(25) NULL,
    periodo_dias           DECIMAL(12,5) NULL,
    periodo_anos           DECIMAL(12,5) NULL,
    moid_ua                DECIMAL(13,10) NULL,
    moid_ld                DECIMAL(13,10) NULL,

    sigma_e                DECIMAL(12,10) NULL,
    sigma_a_ua             DECIMAL(13,10) NULL,
    sigma_q_ua             DECIMAL(13,10) NULL,
    sigma_i_graus          DECIMAL(10,6) NULL,
    sigma_om_graus         DECIMAL(10,6) NULL,
    sigma_w_graus          DECIMAL(10,6) NULL,
    sigma_ma_graus         DECIMAL(10,6) NULL,
    sigma_ad_ua            DECIMAL(13,10) NULL,
    sigma_n_graus_dia      DECIMAL(12,8) NULL,
    sigma_tp_jd            DECIMAL(15,5) NULL,
    sigma_periodo_dias     DECIMAL(12,5) NULL,

    incerteza_orbita       VARCHAR(10) NULL,
    codigo_condicao        VARCHAR(10) NULL,
    rms                    DECIMAL(10,6) NULL,
    referencia_mpc         VARCHAR(50) NULL,
    num_observacoes        INT NULL,
    num_oposicoes          INT NULL,
    arco_anos              DECIMAL(6,2) NULL,
    perturbacoes           VARCHAR(100) NULL,
    computador_orbita      VARCHAR(100) NULL,
    data_ultima_atualizacao DATETIME NULL,

    valido_de              DATETIME NULL,
    valido_ate             DATETIME NULL,
    solucao_atual          BIT NULL,

    CONSTRAINT FK_SolucaoOrbital_Asteroide
        FOREIGN KEY (id_asteroide) REFERENCES Asteroide(id_asteroide),

    CONSTRAINT FK_SolucaoOrbital_ClasseOrbital
        FOREIGN KEY (codigo_classe) REFERENCES Classe_Orbital(codigo_classe)
);

------------------------------------------------------
-- APROXIMACAO_PROXIMA
------------------------------------------------------
CREATE TABLE Aproximacao_Proxima (
    id_aproximacao_proxima INT IDENTITY(1,1) PRIMARY KEY,
    id_asteroide           INT NOT NULL,
    id_solucao_orbital     INT NULL,
    datahora_aproximacao   DATETIME NULL,
    distancia_ua           DECIMAL(13,10) NULL,
    distancia_ld           DECIMAL(13,10) NULL,
    velocidade_relativa_kms DECIMAL(10,4) NULL,
    critica                BIT NULL,
    datahora_registo       DATETIME NULL,

    CONSTRAINT FK_AproxProx_Asteroide
        FOREIGN KEY (id_asteroide) REFERENCES Asteroide(id_asteroide),

    CONSTRAINT FK_AproxProx_SolucaoOrbital
        FOREIGN KEY (id_solucao_orbital) REFERENCES Solucao_Orbital(id_solucao_orbital)
);

------------------------------------------------------
-- PRIORIDADE_ALERTA
------------------------------------------------------
CREATE TABLE Prioridade_Alerta (
    id_prioridade_alerta   INT IDENTITY(1,1) PRIMARY KEY,
    codigo                 VARCHAR(20) NULL,
    nome                   VARCHAR(50) NULL,
    descricao              VARCHAR(255) NULL
);

------------------------------------------------------
-- NIVEL_ALERTA
------------------------------------------------------
CREATE TABLE Nivel_Alerta (
    id_nivel_alerta        INT IDENTITY(1,1) PRIMARY KEY,
    codigo                 INT NULL,
    cor                    VARCHAR(20) NULL,
    descricao              VARCHAR(255) NULL,
    diametro_min_m         DECIMAL(10,2) NULL,
    diametro_max_m         DECIMAL(10,2) NULL,
    moid_min_ld            DECIMAL(10,4) NULL,
    moid_max_ld            DECIMAL(10,4) NULL,
    rms_maximo             DECIMAL(10,4) NULL,
    janela_dias            INT NULL
);

------------------------------------------------------
-- ALERTA
------------------------------------------------------
CREATE TABLE Alerta (
    id_alerta              INT IDENTITY(1,1) PRIMARY KEY,
    id_asteroide           INT NOT NULL,
    id_solucao_orbital     INT NULL,
    id_aproximacao_proxima INT NULL,
    id_prioridade_alerta   INT NOT NULL,
    id_nivel_alerta        INT NULL,

    codigo_regra           VARCHAR(50) NULL,
    datahora_geracao       DATETIME NULL,
    ativo                  BIT NULL,
    titulo                 VARCHAR(200) NULL,
    descricao              NVARCHAR(MAX) NULL,
    datahora_reconhecimento DATETIME NULL,
    datahora_encerramento  DATETIME NULL,

    CONSTRAINT FK_Alerta_Asteroide
        FOREIGN KEY (id_asteroide) REFERENCES Asteroide(id_asteroide),

    CONSTRAINT FK_Alerta_SolucaoOrbital
        FOREIGN KEY (id_solucao_orbital) REFERENCES Solucao_Orbital(id_solucao_orbital),

    CONSTRAINT FK_Alerta_AproxProx
        FOREIGN KEY (id_aproximacao_proxima) REFERENCES Aproximacao_Proxima(id_aproximacao_proxima),

    CONSTRAINT FK_Alerta_Prioridade
        FOREIGN KEY (id_prioridade_alerta) REFERENCES Prioridade_Alerta(id_prioridade_alerta),

    CONSTRAINT FK_Alerta_Nivel
        FOREIGN KEY (id_nivel_alerta) REFERENCES Nivel_Alerta(id_nivel_alerta)
);

------------------------------------------------------
-- CENTRO_OBSERVACAO
------------------------------------------------------
CREATE TABLE Centro_Observacao (
    id_centro              INT IDENTITY(1,1) PRIMARY KEY,
    codigo                 VARCHAR(20) NULL,
    nome                   VARCHAR(100) NULL,
    pais                   VARCHAR(50) NULL,
    cidade                 VARCHAR(50) NULL,
    latitude_graus         DECIMAL(9,6) NULL,
    longitude_graus        DECIMAL(9,6) NULL,
    altitude_m             DECIMAL(8,2) NULL
);

------------------------------------------------------
-- EQUIPAMENTO
------------------------------------------------------
CREATE TABLE Equipamento (
    id_equipamento         INT IDENTITY(1,1) PRIMARY KEY,
    id_centro              INT NOT NULL,
    nome                   VARCHAR(100) NULL,
    tipo                   VARCHAR(50) NULL,
    modelo                 VARCHAR(100) NULL,
    abertura_m             DECIMAL(6,3) NULL,
    distancia_focal_m      DECIMAL(6,3) NULL,
    notas                  NVARCHAR(MAX) NULL,

    CONSTRAINT FK_Equipamento_Centro
        FOREIGN KEY (id_centro) REFERENCES Centro_Observacao(id_centro)
);

------------------------------------------------------
-- SOFTWARE
------------------------------------------------------
CREATE TABLE Software (
    id_software            INT IDENTITY(1,1) PRIMARY KEY,
    nome                   VARCHAR(100) NULL,
    versao                 VARCHAR(50) NULL,
    fornecedor             VARCHAR(100) NULL,
    tipo_licenca           VARCHAR(50) NULL,
    website                VARCHAR(200) NULL
);

------------------------------------------------------
-- ASTRONOMO
------------------------------------------------------
CREATE TABLE Astronomo (
    id_astronomo           INT IDENTITY(1,1) PRIMARY KEY,
    id_centro              INT NULL,
    nome_completo          VARCHAR(150) NULL,
    email                  VARCHAR(150) NULL,
    telefone               VARCHAR(30) NULL,
    funcao                 VARCHAR(50) NULL,

    CONSTRAINT FK_Astronomo_Centro
        FOREIGN KEY (id_centro) REFERENCES Centro_Observacao(id_centro)
);

------------------------------------------------------
-- OBSERVACAO
------------------------------------------------------
CREATE TABLE Observacao (
    id_observacao          INT IDENTITY(1,1) PRIMARY KEY,
    id_asteroide           INT NOT NULL,
    id_astronomo           INT NOT NULL,
    id_equipamento         INT NOT NULL,
    id_software            INT NOT NULL,

    datahora_observacao    DATETIME NULL,
    duracao_min            INT NULL,
    modo                   VARCHAR(50) NULL,
    seeing_arcseg          DECIMAL(5,2) NULL,
    filtro                 VARCHAR(20) NULL,
    magnitude              DECIMAL(6,3) NULL,
    notas                  NVARCHAR(MAX) NULL,

    CONSTRAINT FK_Obs_Asteroide
        FOREIGN KEY (id_asteroide) REFERENCES Asteroide(id_asteroide),

    CONSTRAINT FK_Obs_Astronomo
        FOREIGN KEY (id_astronomo) REFERENCES Astronomo(id_astronomo),

    CONSTRAINT FK_Obs_Equipamento
        FOREIGN KEY (id_equipamento) REFERENCES Equipamento(id_equipamento),

    CONSTRAINT FK_Obs_Software
        FOREIGN KEY (id_software) REFERENCES Software(id_software)
);

------------------------------------------------------
-- IMAGEM
------------------------------------------------------
CREATE TABLE Imagem (
    id_imagem              INT IDENTITY(1,1) PRIMARY KEY,
    id_asteroide           INT NOT NULL,
    id_observacao          INT NULL,

    nome_ficheiro          VARCHAR(255) NULL,
    caminho_url            VARCHAR(500) NULL,
    datahora_captura       DATETIME NULL,
    exposicao_s            DECIMAL(8,3) NULL,
    filtro                 VARCHAR(20) NULL,
    resolucao_x            INT NULL,
    resolucao_y            INT NULL,

    CONSTRAINT FK_Imagem_Asteroide
        FOREIGN KEY (id_asteroide) REFERENCES Asteroide(id_asteroide),

    CONSTRAINT FK_Imagem_Observacao
        FOREIGN KEY (id_observacao) REFERENCES Observacao(id_observacao)
);
