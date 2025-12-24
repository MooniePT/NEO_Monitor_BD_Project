------------------------------------------------------------
-- File: sql/01_create_tables.sql
-- Descrição: Criação de tabelas NEO + ESA
------------------------------------------------------------
USE BD_PL2_09;
GO

------------------------------------------------------------
-- TABELAS DE APOIO
------------------------------------------------------------

CREATE TABLE dbo.Classe_Orbital (
    id_classe_orbital   INT IDENTITY(1,1) PRIMARY KEY,
    codigo              VARCHAR(20)  NOT NULL,
    nome                VARCHAR(100) NOT NULL,
    descricao           VARCHAR(255) NULL
);
GO

CREATE TABLE dbo.Nivel_Alerta (
    id_nivel_alerta INT IDENTITY(1,1) PRIMARY KEY,
    codigo          VARCHAR(20)  NOT NULL,  -- ex: 'VERDE','AMARELO','LARANJA','VERMELHO'
    cor             VARCHAR(20)  NOT NULL,  -- ex: 'verde','amarelo',...
    descricao       VARCHAR(255) NULL
);
GO

CREATE TABLE dbo.Prioridade_Alerta (
    id_prioridade_alerta INT IDENTITY(1,1) PRIMARY KEY,
    codigo               VARCHAR(20)  NOT NULL,  -- ex: 'BAIXA','MEDIA','ALTA'
    nome                 VARCHAR(100) NOT NULL,
    ordem                INT          NOT NULL   -- 1=mais baixa, maior=mais alta
);
GO

------------------------------------------------------------
-- TABELA ASTEROIDE E NÚCLEO ORBITAL / APROXIMAÇÕES
------------------------------------------------------------

CREATE TABLE dbo.Asteroide (
    id_asteroide      INT IDENTITY(1,1) PRIMARY KEY,
    id_csv_original   VARCHAR(50)  NULL,       -- Adicionado para rastreabilidade
    spkid             BIGINT       NULL,       -- Adicionado do CSV
    pdes              VARCHAR(20)  NOT NULL,   -- designação abreviada
    nome_completo     VARCHAR(255) NOT NULL,
    flag_neo          BIT          NOT NULL,
    flag_pha          BIT          NOT NULL,
    H_mag             FLOAT        NULL,
    diametro_km       FLOAT        NULL,
    albedo            FLOAT        NULL,       -- Adicionado do CSV
    moid_ua           FLOAT        NULL,
    moid_ld           FLOAT        NULL,
    id_classe_orbital INT          NULL
        CONSTRAINT FK_Asteroide_ClasseOrbital
            REFERENCES dbo.Classe_Orbital(id_classe_orbital)
);
GO

CREATE TABLE dbo.Solucao_Orbital (
    id_solucao_orbital   INT IDENTITY(1,1) PRIMARY KEY,
    id_asteroide         INT          NOT NULL,
    epoca_jd             FLOAT        NULL,
    excentricidade       FLOAT        NULL,
    semi_eixo_maior_ua   FLOAT        NULL,
    inclinacao_graus     FLOAT        NULL,
    nodo_asc_graus       FLOAT        NULL,
    arg_perihelio_graus  FLOAT        NULL,
    anomalia_media_graus FLOAT        NULL,
    moid_ua              FLOAT        NULL,
    moid_ld              FLOAT        NULL,
    rms                  FLOAT        NULL,
    solucao_atual        BIT          NOT NULL DEFAULT 0,
    origem               VARCHAR(50)  NULL,
    data_epoca           DATE         NULL,
    CONSTRAINT FK_SolucaoOrbital_Asteroide
        FOREIGN KEY (id_asteroide)
        REFERENCES dbo.Asteroide(id_asteroide)
);
GO

CREATE TABLE dbo.Aproximacao_Proxima (
    id_aproximacao_proxima INT IDENTITY(1,1) PRIMARY KEY,
    id_asteroide           INT          NOT NULL,
    id_solucao_orbital     INT          NULL,
    datahora_aproximacao   DATETIME2(0) NOT NULL,
    distancia_ua           FLOAT        NULL,
    distancia_ld           FLOAT        NULL,
    velocidade_rel_kms     FLOAT        NULL,
    flag_critica           BIT          NOT NULL DEFAULT 0,
    origem                 VARCHAR(50)  NULL,
    CONSTRAINT FK_AproxProx_Asteroide
        FOREIGN KEY (id_asteroide)
        REFERENCES dbo.Asteroide(id_asteroide),
    CONSTRAINT FK_AproxProx_SolucaoOrbital
        FOREIGN KEY (id_solucao_orbital)
        REFERENCES dbo.Solucao_Orbital(id_solucao_orbital)
);
GO

------------------------------------------------------------
-- ALERTAS
------------------------------------------------------------

CREATE TABLE dbo.Alerta (
    id_alerta             INT IDENTITY(1,1) PRIMARY KEY,
    datahora_geracao      DATETIME2(0) NOT NULL DEFAULT SYSDATETIME(),
    codigo_regra          VARCHAR(50)  NOT NULL,
    titulo                VARCHAR(255) NOT NULL,
    descricao             NVARCHAR(MAX) NULL,
    id_asteroide          INT          NOT NULL,
    id_solucao_orbital    INT          NULL,
    id_aproximacao_proxima INT         NULL,
    id_prioridade_alerta  INT          NOT NULL,
    id_nivel_alerta       INT          NULL,
    ativo                 BIT          NOT NULL DEFAULT 1,
    CONSTRAINT FK_Alerta_Asteroide
        FOREIGN KEY (id_asteroide)
        REFERENCES dbo.Asteroide(id_asteroide),
    CONSTRAINT FK_Alerta_SolucaoOrbital
        FOREIGN KEY (id_solucao_orbital)
        REFERENCES dbo.Solucao_Orbital(id_solucao_orbital),
    CONSTRAINT FK_Alerta_AproxProx
        FOREIGN KEY (id_aproximacao_proxima)
        REFERENCES dbo.Aproximacao_Proxima(id_aproximacao_proxima),
    CONSTRAINT FK_Alerta_Prioridade
        FOREIGN KEY (id_prioridade_alerta)
        REFERENCES dbo.Prioridade_Alerta(id_prioridade_alerta),
    CONSTRAINT FK_Alerta_Nivel
        FOREIGN KEY (id_nivel_alerta)
        REFERENCES dbo.Nivel_Alerta(id_nivel_alerta)
);
GO

------------------------------------------------------------
-- CONTEXTO OBSERVACIONAL
------------------------------------------------------------

CREATE TABLE dbo.Centro_Observacao (
    id_centro INT IDENTITY(1,1) PRIMARY KEY,
    codigo    VARCHAR(20)  NOT NULL,
    nome      VARCHAR(150) NOT NULL,
    pais      VARCHAR(100) NULL,
    cidade    VARCHAR(100) NULL,
    latitude  FLOAT        NULL,
    longitude FLOAT        NULL,
    altitude_m INT         NULL
);
GO

CREATE TABLE dbo.Equipamento (
    id_equipamento    INT IDENTITY(1,1) PRIMARY KEY,
    id_centro         INT          NOT NULL,
    nome              VARCHAR(150) NOT NULL,
    tipo              VARCHAR(100) NULL,
    modelo            VARCHAR(100) NULL,
    diametro_mm       FLOAT        NULL,
    distancia_focal_mm FLOAT       NULL,
    CONSTRAINT FK_Equipamento_Centro
        FOREIGN KEY (id_centro)
        REFERENCES dbo.Centro_Observacao(id_centro)
);
GO

CREATE TABLE dbo.Astronomo (
    id_astronomo   INT IDENTITY(1,1) PRIMARY KEY,
    nome_completo  VARCHAR(150) NOT NULL,
    email          VARCHAR(150) NULL,
    afiliacao      VARCHAR(150) NULL
);
GO

CREATE TABLE dbo.Software (
    id_software INT IDENTITY(1,1) PRIMARY KEY,
    nome        VARCHAR(100) NOT NULL,
    versao      VARCHAR(50)  NULL,
    fornecedor  VARCHAR(100) NULL
);
GO

CREATE TABLE dbo.Observacao (
    id_observacao        INT IDENTITY(1,1) PRIMARY KEY,
    id_asteroide         INT          NOT NULL,
    id_astronomo         INT          NOT NULL,
    id_equipamento       INT          NOT NULL,
    id_software          INT          NOT NULL,
    datahora_observacao  DATETIME2(0) NOT NULL,
    duracao_min          INT          NULL,
    modo                 VARCHAR(50)  NULL,
    seeing_arcseg        FLOAT        NULL,
    filtro               VARCHAR(50)  NULL,
    magnitude            FLOAT        NULL,
    notas                NVARCHAR(MAX) NULL,
    CONSTRAINT FK_Obs_Asteroide
        FOREIGN KEY (id_asteroide)
        REFERENCES dbo.Asteroide(id_asteroide),
    CONSTRAINT FK_Obs_Astronomo
        FOREIGN KEY (id_astronomo)
        REFERENCES dbo.Astronomo(id_astronomo),
    CONSTRAINT FK_Obs_Equipamento
        FOREIGN KEY (id_equipamento)
        REFERENCES dbo.Equipamento(id_equipamento),
    CONSTRAINT FK_Obs_Software
        FOREIGN KEY (id_software)
        REFERENCES dbo.Software(id_software)
);
GO

CREATE TABLE dbo.Imagem (
    id_imagem     INT IDENTITY(1,1) PRIMARY KEY,
    id_observacao INT          NOT NULL,
    caminho_arquivo VARCHAR(255) NOT NULL,
    formato       VARCHAR(10)  NULL,
    largura_px    INT          NULL,
    altura_px     INT          NULL,
    tamanho_kb    INT          NULL,
    CONSTRAINT FK_Imagem_Observacao
        FOREIGN KEY (id_observacao)
        REFERENCES dbo.Observacao(id_observacao)
);
GO

------------------------------------------------------------
-- TABELAS ESA
------------------------------------------------------------

CREATE TABLE dbo.ESA_LISTA_RISCO_ATUAL (
    id_risco_atual        INT IDENTITY(1,1) PRIMARY KEY,
    id_asteroide          INT          NULL,
    num_lista             INT          NULL,
    designacao_objeto     VARCHAR(100) NOT NULL,
    diametro_m_texto      VARCHAR(50)  NULL,
    datahora_impacto_utc  DATETIME2(0) NULL,
    ip_max_texto          VARCHAR(50)  NULL,
    ps_max                FLOAT        NULL,
    ts                    FLOAT        NULL,
    anos_intervalo        VARCHAR(50)  NULL,
    ip_cum_texto          VARCHAR(50)  NULL,
    ps_cum                FLOAT        NULL,
    velocidade_kms        FLOAT        NULL,
    dias_na_lista         INT          NULL,
    CONSTRAINT FK_ESA_RiscoAtual_Asteroide
        FOREIGN KEY (id_asteroide)
        REFERENCES dbo.Asteroide(id_asteroide)
);
GO

CREATE TABLE dbo.ESA_LISTA_RISCO_ESPECIAL (
    id_risco_especial      INT IDENTITY(1,1) PRIMARY KEY,
    id_asteroide           INT          NULL,
    num_lista              INT          NULL,
    designacao_objeto      VARCHAR(100) NOT NULL,
    diametro_m_texto       VARCHAR(50)  NULL,
    datahora_impacto_utc   DATETIME2(0) NULL,
    ip_max_texto           VARCHAR(50)  NULL,
    ps_max                 FLOAT        NULL,
    velocidade_kms         FLOAT        NULL,
    dias_na_lista          INT          NULL,
    comentario             NVARCHAR(255) NULL,
    CONSTRAINT FK_ESA_RiscoEspecial_Asteroide
        FOREIGN KEY (id_asteroide)
        REFERENCES dbo.Asteroide(id_asteroide)
);
GO

CREATE TABLE dbo.ESA_IMPACTORES_PASSADOS (
    id_impactor            INT IDENTITY(1,1) PRIMARY KEY,
    id_asteroide           INT          NULL,
    num_lista              INT          NULL,
    designacao_objeto      VARCHAR(100) NOT NULL,
    diametro_m_texto       VARCHAR(50)  NULL,
    datahora_impacto_utc   DATETIME2(0) NULL,
    velocidade_impacto_kms FLOAT        NULL,
    fpa_graus              FLOAT        NULL,
    azimute_graus          FLOAT        NULL,
    energia_kt             FLOAT        NULL,
    energia_kt_outras      VARCHAR(100) NULL,
    CONSTRAINT FK_ESA_Impactores_Asteroide
        FOREIGN KEY (id_asteroide)
        REFERENCES dbo.Asteroide(id_asteroide)
);
GO

CREATE TABLE dbo.ESA_OBJETOS_REMOVIDOS_RISCO (
    id_remocao        INT IDENTITY(1,1) PRIMARY KEY,
    id_asteroide      INT          NULL,
    designacao_objeto VARCHAR(100) NOT NULL,
    data_remocao_utc  DATETIME2(0) NULL,
    data_vi_utc       DATETIME2(0) NULL,
    ultimo_ip         VARCHAR(50)  NULL,
    ultimo_ps         VARCHAR(50)  NULL,
    CONSTRAINT FK_ESA_Removidos_Asteroide
        FOREIGN KEY (id_asteroide)
        REFERENCES dbo.Asteroide(id_asteroide)
);
GO

CREATE TABLE dbo.ESA_APROXIMACOES_PROXIMAS (
    id_aproximacao_esa       INT IDENTITY(1,1) PRIMARY KEY,
    id_asteroide             INT          NULL,
    designacao_objeto        VARCHAR(100) NOT NULL,
    datahora_aproximacao_utc DATETIME2(0) NULL,
    miss_dist_km             FLOAT        NULL,
    miss_dist_au             FLOAT        NULL,
    miss_dist_ld             FLOAT        NULL,
    diametro_m_texto         VARCHAR(50)  NULL,
    H_mag                    FLOAT        NULL,
    brilho_max_mag           FLOAT        NULL,
    vel_rel_kms              FLOAT        NULL,
    cai_index                VARCHAR(50)  NULL,
    CONSTRAINT FK_ESA_Aprox_Asteroide
        FOREIGN KEY (id_asteroide)
        REFERENCES dbo.Asteroide(id_asteroide)
);
GO

CREATE TABLE dbo.ESA_RESULTADOS_PESQUISA (
    id_pesquisa      INT IDENTITY(1,1) PRIMARY KEY,
    id_asteroide     INT          NULL,
    designacao_objeto VARCHAR(100) NOT NULL,
    CONSTRAINT FK_ESA_Pesquisa_Asteroide
        FOREIGN KEY (id_asteroide)
        REFERENCES dbo.Asteroide(id_asteroide)
);
GO
