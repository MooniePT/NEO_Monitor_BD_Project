------------------------------------------------------------
-- 01_create_tables.sql
-- Objetivo: Criar o modelo NORMALIZADO (3FN) conforme Manual + DER
-- DB alvo: BD_PL2_09
------------------------------------------------------------
USE [BD_PL2_09];
GO
SET NOCOUNT ON;
SET XACT_ABORT ON;
GO

------------------------------------------------------------
-- SCHEMA DE STAGING
------------------------------------------------------------
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name='stg')
    EXEC('CREATE SCHEMA stg AUTHORIZATION dbo;');
GO

------------------------------------------------------------
-- TABELA DE LOG DE IMPORTAÇÕES
------------------------------------------------------------
CREATE TABLE dbo.Import_Log (
    id_import      INT IDENTITY(1,1) PRIMARY KEY,
    fonte          VARCHAR(50) NOT NULL,
    descricao      NVARCHAR(400) NULL,
    datahora       DATETIME2(0) NOT NULL CONSTRAINT DF_ImportLog_DataHora DEFAULT SYSUTCDATETIME(),
    linhas_afetadas BIGINT NULL
);
GO

------------------------------------------------------------
-- TABELAS DE ALERTA (DIMENSÕES)
------------------------------------------------------------
CREATE TABLE dbo.Prioridade_Alerta (
    id_prio_alerta INT IDENTITY(1,1) PRIMARY KEY,
    codigo         VARCHAR(20)  NOT NULL,
    nome           VARCHAR(60)  NOT NULL,
    descricao      NVARCHAR(255) NULL,
    CONSTRAINT UQ_Prioridade_Codigo UNIQUE (codigo)
);
GO

CREATE TABLE dbo.Nivel_Alerta (
    id_nivel_alerta   INT IDENTITY(1,1) PRIMARY KEY,
    codigo            VARCHAR(20) NOT NULL,
    cor               VARCHAR(20) NOT NULL CHECK (cor IN ('VERDE','AMARELO','LARANJA','VERMELHO')),
    descricao         NVARCHAR(255) NULL,

    -- Limiares (Torino modificado - Manual)
    diametro_min_m    FLOAT NULL,
    diametro_max_m    FLOAT NULL,
    moid_min_ld       FLOAT NULL,
    moid_max_ld       FLOAT NULL,
    rms_max           FLOAT NULL,
    janela_dias       INT   NULL,

    CONSTRAINT UQ_Nivel_Codigo UNIQUE (codigo)
);
GO

------------------------------------------------------------
-- CLASSES ORBITAIS (MBA, APO, AMO, ...)
------------------------------------------------------------
CREATE TABLE dbo.Classe_Orbital (
    id_classe_orbital INT IDENTITY(1,1) PRIMARY KEY,
    codigo            VARCHAR(20)  NOT NULL,
    descricao         NVARCHAR(255) NULL,
    CONSTRAINT UQ_ClasseOrbital_Codigo UNIQUE (codigo)
);
GO

------------------------------------------------------------
-- ENTIDADE NÚCLEO: ASTEROIDE (sem redundâncias orbitais)
------------------------------------------------------------
CREATE TABLE dbo.Asteroide (
    id_asteroide        INT IDENTITY(1,1) PRIMARY KEY,

    -- Identificadores principais (NASA / internos)
    nasa_id             INT NULL,            -- neo.csv: id
    spkid               BIGINT NULL,         -- neo.csv: spkid
    pdes                VARCHAR(30) NOT NULL, -- identificação forte (neo + mpcorb)
    
    -- Nome/designação
    nome_asteroide      NVARCHAR(120) NULL,  -- neo.csv: name
    prefixo             NVARCHAR(40)  NULL,  -- neo.csv: prefix
    nome_completo       NVARCHAR(255) NULL,  -- neo.csv: full_name

    -- Flags
    flag_neo            BIT NOT NULL CONSTRAINT DF_Asteroide_flag_neo DEFAULT 0,
    flag_pha            BIT NOT NULL CONSTRAINT DF_Asteroide_flag_pha DEFAULT 0,

    -- Parâmetros físicos
    h_mag               FLOAT NULL,          -- neo.csv: h / mpcorb: abs_mag
    diametro_km         FLOAT NULL,          -- neo.csv: diameter (km)
    diametro_sigma_km   FLOAT NULL,          -- neo.csv: diameter_sigma (km)
    albedo              FLOAT NULL,          -- 0..1

    data_descoberta     DATE NULL,           -- se existir (NEO/MPCORB podem não ter)

    -- Chave normalizada para matching entre fontes (resolve também o "ast_key" em código Python)
    ast_key AS (
        REPLACE(
            REPLACE(
                REPLACE(
                    REPLACE(
                        UPPER(COALESCE(nome_completo, nome_asteroide, pdes)),
                    '(', ''),
                ')', ''),
            ' ', ''),
        '-', '')
    ) PERSISTED,

    CONSTRAINT UQ_Asteroide_PDES UNIQUE (pdes),
    CONSTRAINT CK_Asteroide_Albedo CHECK (albedo IS NULL OR (albedo BETWEEN 0 AND 1)),
    CONSTRAINT CK_Asteroide_Diametro CHECK (diametro_km IS NULL OR diametro_km > 0)
);
GO

CREATE UNIQUE INDEX UX_Asteroide_NASAID ON dbo.Asteroide(nasa_id) WHERE nasa_id IS NOT NULL;
CREATE UNIQUE INDEX UX_Asteroide_SPKID  ON dbo.Asteroide(spkid)  WHERE spkid IS NOT NULL;
CREATE INDEX IX_Asteroide_AstKey ON dbo.Asteroide(ast_key);
GO

------------------------------------------------------------
-- SOLUÇÃO ORBITAL (1:N por asteroide) - aqui ficam MOID, RMS e elementos orbitais
------------------------------------------------------------
CREATE TABLE dbo.Solucao_Orbital (
    id_solucao_orbital INT IDENTITY(1,1) PRIMARY KEY,
    id_asteroide       INT NOT NULL,
    fonte              VARCHAR(20) NOT NULL,        -- 'NEO' ou 'MPCORB'
    orbit_id           BIGINT NULL,                 -- neo.csv: orbit_id (quando aplicável)

    epoch_jd           FLOAT NULL,
    epoch_mjd          FLOAT NULL,
    epoch_cal          DATE  NULL,

    -- Elementos principais (neo.csv)
    e                 FLOAT NULL,
    a_au              FLOAT NULL,
    q_au              FLOAT NULL,
    i_deg             FLOAT NULL,
    om_deg            FLOAT NULL,
    w_deg             FLOAT NULL,
    ma_deg            FLOAT NULL,
    ad_au             FLOAT NULL,
    n_deg_d           FLOAT NULL,

    tp_jd             FLOAT NULL,
    tp_cal            DATE  NULL,
    per_d             FLOAT NULL,
    per_y             FLOAT NULL,

    -- Métricas de risco/qualidade
    moid_ua           FLOAT NULL,
    moid_ld           FLOAT NULL,
    rms               FLOAT NULL,

    -- Incertezas (neo.csv)
    sigma_e           FLOAT NULL,
    sigma_a           FLOAT NULL,
    sigma_q           FLOAT NULL,
    sigma_i           FLOAT NULL,
    sigma_om          FLOAT NULL,
    sigma_w           FLOAT NULL,
    sigma_ma          FLOAT NULL,
    sigma_ad          FLOAT NULL,
    sigma_n           FLOAT NULL,
    sigma_tp          FLOAT NULL,
    sigma_per         FLOAT NULL,

    id_classe_orbital INT NULL,

    solucao_atual     BIT NOT NULL CONSTRAINT DF_Solucao_solucao_atual DEFAULT 0,
    dt_import         DATETIME2(0) NOT NULL CONSTRAINT DF_Solucao_dt_import DEFAULT SYSUTCDATETIME(),

    CONSTRAINT FK_Solucao_Asteroide FOREIGN KEY (id_asteroide) REFERENCES dbo.Asteroide(id_asteroide),
    CONSTRAINT FK_Solucao_ClasseOrbital FOREIGN KEY (id_classe_orbital) REFERENCES dbo.Classe_Orbital(id_classe_orbital)
);
GO

CREATE INDEX IX_Solucao_Asteroide ON dbo.Solucao_Orbital(id_asteroide);
CREATE INDEX IX_Solucao_Atual ON dbo.Solucao_Orbital(id_asteroide, solucao_atual) INCLUDE (moid_ld, rms, e, i_deg, dt_import);
CREATE INDEX IX_Solucao_OrbitId ON dbo.Solucao_Orbital(orbit_id) WHERE orbit_id IS NOT NULL;
GO

------------------------------------------------------------
-- APROXIMAÇÃO PRÓXIMA (eventos)
------------------------------------------------------------
CREATE TABLE dbo.Aproximacao_Proxima (
    id_aprox_prox       INT IDENTITY(1,1) PRIMARY KEY,
    id_asteroide        INT NOT NULL,
    datahora_aprox      DATETIME2(0) NOT NULL,
    distancia_ua        FLOAT NULL,
    distancia_ld        FLOAT NULL,
    veloc_relativa_kms  FLOAT NULL,
    critica             BIT NOT NULL CONSTRAINT DF_Aprox_Critica DEFAULT 0,
    origem              VARCHAR(30) NULL, -- 'ESA' / 'NASA' / etc
    datahora_registo    DATETIME2(0) NOT NULL CONSTRAINT DF_Aprox_Registo DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_Aprox_Asteroide FOREIGN KEY (id_asteroide) REFERENCES dbo.Asteroide(id_asteroide)
);
GO
CREATE INDEX IX_Aprox_Asteroide_Data ON dbo.Aproximacao_Proxima(id_asteroide, datahora_aprox);
GO

------------------------------------------------------------
-- ALERTA (fact)
------------------------------------------------------------
CREATE TABLE dbo.Alerta (
    id_alerta              INT IDENTITY(1,1) PRIMARY KEY,
    id_asteroide           INT NOT NULL,
    id_aprox_prox          INT NULL,
    id_solucao_orbital     INT NULL,
    id_prio_alerta         INT NOT NULL,
    id_nivel_alerta        INT NULL,

    codigo_regra           VARCHAR(50) NOT NULL,  -- ex: HIGH_CA_1LD_7D_10M
    titulo                 NVARCHAR(120) NOT NULL,
    descricao              NVARCHAR(600) NULL,

    datahora_geracao       DATETIME2(0) NOT NULL CONSTRAINT DF_Alerta_Geracao DEFAULT SYSUTCDATETIME(),
    ativo                  BIT NOT NULL CONSTRAINT DF_Alerta_Ativo DEFAULT 1,
    datahora_reconhecimento DATETIME2(0) NULL,
    datahora_encerramento  DATETIME2(0) NULL,

    CONSTRAINT FK_Alerta_Asteroide FOREIGN KEY (id_asteroide) REFERENCES dbo.Asteroide(id_asteroide),
    CONSTRAINT FK_Alerta_Aprox FOREIGN KEY (id_aprox_prox) REFERENCES dbo.Aproximacao_Proxima(id_aprox_prox),
    CONSTRAINT FK_Alerta_Solucao FOREIGN KEY (id_solucao_orbital) REFERENCES dbo.Solucao_Orbital(id_solucao_orbital),
    CONSTRAINT FK_Alerta_Prioridade FOREIGN KEY (id_prio_alerta) REFERENCES dbo.Prioridade_Alerta(id_prio_alerta),
    CONSTRAINT FK_Alerta_Nivel FOREIGN KEY (id_nivel_alerta) REFERENCES dbo.Nivel_Alerta(id_nivel_alerta)
);
GO
CREATE INDEX IX_Alerta_Ativo ON dbo.Alerta(ativo, id_prio_alerta, id_nivel_alerta);
CREATE INDEX IX_Alerta_Asteroide ON dbo.Alerta(id_asteroide, ativo);
GO

------------------------------------------------------------
-- CONTEXTO OBSERVACIONAL (NORMALIZADO)
------------------------------------------------------------
CREATE TABLE dbo.Centro_Observacao (
    id_centro       INT IDENTITY(1,1) PRIMARY KEY,
    codigo          VARCHAR(20)  NOT NULL,
    nome            NVARCHAR(150) NOT NULL,
    pais            NVARCHAR(100) NULL,
    cidade          NVARCHAR(100) NULL,
    latitude_graus  FLOAT NULL,
    longitude_graus FLOAT NULL,
    altitude_m      INT NULL,
    CONSTRAINT UQ_Centro_Codigo UNIQUE (codigo)
);
GO

CREATE TABLE dbo.Equipamento (
    id_equipamento       INT IDENTITY(1,1) PRIMARY KEY,
    id_centro            INT NOT NULL,
    nome                 NVARCHAR(120) NOT NULL,
    tipo                 NVARCHAR(60)  NULL,
    modelo               NVARCHAR(120) NULL,
    abertura_m           FLOAT NULL,
    distancia_focal_m    FLOAT NULL,
    notas                NVARCHAR(600) NULL,
    CONSTRAINT FK_Equip_Centro FOREIGN KEY (id_centro) REFERENCES dbo.Centro_Observacao(id_centro)
);
GO
CREATE INDEX IX_Equip_Centro ON dbo.Equipamento(id_centro);
GO

CREATE TABLE dbo.Astronomo (
    id_astronomo    INT IDENTITY(1,1) PRIMARY KEY,
    id_centro       INT NULL,
    nome_completo   NVARCHAR(150) NOT NULL,
    telefone        NVARCHAR(40)  NULL,
    email           NVARCHAR(150) NULL,
    funcao          NVARCHAR(80)  NULL,
    CONSTRAINT FK_Astro_Centro FOREIGN KEY (id_centro) REFERENCES dbo.Centro_Observacao(id_centro)
);
GO
CREATE UNIQUE INDEX UX_Astronomo_Email ON dbo.Astronomo(email) WHERE email IS NOT NULL;
GO

CREATE TABLE dbo.Software (
    id_software  INT IDENTITY(1,1) PRIMARY KEY,
    nome         NVARCHAR(120) NOT NULL,
    versao       NVARCHAR(40)  NULL,
    fornecedor   NVARCHAR(120) NULL,
    tipo_licenca NVARCHAR(60)  NULL,
    website      NVARCHAR(200) NULL
);
GO
CREATE INDEX IX_Software_Nome ON dbo.Software(nome);
GO

CREATE TABLE dbo.Observacao (
    id_observacao        INT IDENTITY(1,1) PRIMARY KEY,
    id_asteroide         INT NOT NULL,
    id_equipamento       INT NOT NULL,

    datahora_observacao  DATETIME2(0) NOT NULL,
    duracao_min          INT NULL,
    modo                 NVARCHAR(50) NULL,
    seeing_arcsec        FLOAT NULL,
    magnitude            FLOAT NULL,
    notas                NVARCHAR(MAX) NULL,

    CONSTRAINT FK_Obs_Asteroide FOREIGN KEY (id_asteroide) REFERENCES dbo.Asteroide(id_asteroide),
    CONSTRAINT FK_Obs_Equipamento FOREIGN KEY (id_equipamento) REFERENCES dbo.Equipamento(id_equipamento)
);
GO
CREATE INDEX IX_Obs_Asteroide_Data ON dbo.Observacao(id_asteroide, datahora_observacao);
GO

-- N:M Observação ↔ Astrónomo (normalizado)
CREATE TABLE dbo.Observacao_Astronomo (
    id_observacao INT NOT NULL,
    id_astronomo  INT NOT NULL,
    papel         NVARCHAR(60) NULL,
    CONSTRAINT PK_ObsAstro PRIMARY KEY (id_observacao, id_astronomo),
    CONSTRAINT FK_ObsAstro_Obs FOREIGN KEY (id_observacao) REFERENCES dbo.Observacao(id_observacao) ON DELETE CASCADE,
    CONSTRAINT FK_ObsAstro_Astro FOREIGN KEY (id_astronomo) REFERENCES dbo.Astronomo(id_astronomo)
);
GO

-- N:M Observação ↔ Software (normalizado)
CREATE TABLE dbo.Observacao_Software (
    id_observacao INT NOT NULL,
    id_software   INT NOT NULL,
    finalidade    NVARCHAR(60) NULL,
    CONSTRAINT PK_ObsSoft PRIMARY KEY (id_observacao, id_software),
    CONSTRAINT FK_ObsSoft_Obs FOREIGN KEY (id_observacao) REFERENCES dbo.Observacao(id_observacao) ON DELETE CASCADE,
    CONSTRAINT FK_ObsSoft_Soft FOREIGN KEY (id_software) REFERENCES dbo.Software(id_software)
);
GO

CREATE TABLE dbo.Imagem (
    id_imagem        INT IDENTITY(1,1) PRIMARY KEY,
    id_observacao    INT NOT NULL,

    nome_ficheiro    NVARCHAR(255) NULL,
    caminho_url      NVARCHAR(500) NOT NULL,
    exposicao_s      FLOAT NULL,
    resolucao_x      INT NULL,
    resolucao_y      INT NULL,
    datahora_captura DATETIME2(0) NULL,
    filtro           NVARCHAR(50) NULL,

    formato          NVARCHAR(10) NULL,
    tamanho_kb       INT NULL,

    CONSTRAINT FK_Imagem_Obs FOREIGN KEY (id_observacao) REFERENCES dbo.Observacao(id_observacao) ON DELETE CASCADE
);
GO
CREATE INDEX IX_Imagem_Obs ON dbo.Imagem(id_observacao);
GO

------------------------------------------------------------
-- TABELAS ESA (normalizadas + chave de matching)
------------------------------------------------------------
CREATE TABLE dbo.ESA_RiskList (
    id_esa_risklist INT IDENTITY(1,1) PRIMARY KEY,
    id_asteroide    INT NULL,
    num_lista       INT NULL,
    object_designation NVARCHAR(100) NOT NULL,

    designation_key AS (
        REPLACE(REPLACE(REPLACE(REPLACE(UPPER(object_designation),'(',''),')',''),' ',''),'-','')
    ) PERSISTED,

    diameter_m      FLOAT NULL,
    impact_datetime_utc DATETIME2(0) NULL,
    ip_max          FLOAT NULL,
    ps_max          FLOAT NULL,
    ts              FLOAT NULL,
    years           FLOAT NULL,
    ip_cum          FLOAT NULL,
    ps_cum          FLOAT NULL,
    vel_kms         FLOAT NULL,
    in_list_since_days INT NULL,

    CONSTRAINT FK_ESA_Risk_Asteroide FOREIGN KEY (id_asteroide) REFERENCES dbo.Asteroide(id_asteroide)
);
GO
CREATE INDEX IX_ESA_Risk_DesignationKey ON dbo.ESA_RiskList(designation_key);
GO

CREATE TABLE dbo.ESA_SpecialRiskList (
    id_esa_special INT IDENTITY(1,1) PRIMARY KEY,
    id_asteroide   INT NULL,
    num_lista      INT NULL,
    object_designation NVARCHAR(100) NOT NULL,

    designation_key AS (
        REPLACE(REPLACE(REPLACE(REPLACE(UPPER(object_designation),'(',''),')',''),' ',''),'-','')
    ) PERSISTED,

    diameter_m      FLOAT NULL,
    impact_datetime_utc DATETIME2(0) NULL,
    ip_max          FLOAT NULL,
    ps_max          FLOAT NULL,
    vel_kms         FLOAT NULL,
    in_list_since_days INT NULL,
    comment         NVARCHAR(255) NULL,

    CONSTRAINT FK_ESA_Special_Asteroide FOREIGN KEY (id_asteroide) REFERENCES dbo.Asteroide(id_asteroide)
);
GO
CREATE INDEX IX_ESA_Special_DesignationKey ON dbo.ESA_SpecialRiskList(designation_key);
GO

CREATE TABLE dbo.ESA_RemovedFromRiskList (
    id_esa_removed INT IDENTITY(1,1) PRIMARY KEY,
    id_asteroide   INT NULL,
    object_designation NVARCHAR(100) NOT NULL,

    designation_key AS (
        REPLACE(REPLACE(REPLACE(REPLACE(UPPER(object_designation),'(',''),')',''),' ',''),'-','')
    ) PERSISTED,

    removal_date_utc DATETIME2(0) NULL,
    vi_date_utc      DATETIME2(0) NULL,
    last_ip          FLOAT NULL,
    last_ps          FLOAT NULL,

    CONSTRAINT FK_ESA_Removed_Asteroide FOREIGN KEY (id_asteroide) REFERENCES dbo.Asteroide(id_asteroide)
);
GO
CREATE INDEX IX_ESA_Removed_DesignationKey ON dbo.ESA_RemovedFromRiskList(designation_key);
GO

CREATE TABLE dbo.ESA_PastImpactors (
    id_esa_past INT IDENTITY(1,1) PRIMARY KEY,
    id_asteroide INT NULL,
    num_lista    INT NULL,
    object_designation NVARCHAR(100) NOT NULL,

    designation_key AS (
        REPLACE(REPLACE(REPLACE(REPLACE(UPPER(object_designation),'(',''),')',''),' ',''),'-','')
    ) PERSISTED,

    diameter_m      FLOAT NULL,
    impact_datetime_utc DATETIME2(0) NULL,
    impact_velocity_kms FLOAT NULL,
    impact_fpa_deg  FLOAT NULL,
    impact_azimuth_deg FLOAT NULL,
    estimated_energy_kt FLOAT NULL,
    estimated_energy_other_kt FLOAT NULL,

    CONSTRAINT FK_ESA_Past_Asteroide FOREIGN KEY (id_asteroide) REFERENCES dbo.Asteroide(id_asteroide)
);
GO
CREATE INDEX IX_ESA_Past_DesignationKey ON dbo.ESA_PastImpactors(designation_key);
GO

CREATE TABLE dbo.ESA_UpcomingCloseApproaches (
    id_esa_upcoming INT IDENTITY(1,1) PRIMARY KEY,
    id_asteroide INT NULL,
    object_designation NVARCHAR(100) NOT NULL,

    designation_key AS (
        REPLACE(REPLACE(REPLACE(REPLACE(UPPER(object_designation),'(',''),')',''),' ',''),'-','')
    ) PERSISTED,

    close_approach_date_utc DATETIME2(0) NULL,
    miss_distance_km FLOAT NULL,
    miss_distance_au FLOAT NULL,
    miss_distance_ld FLOAT NULL,
    diameter_m       FLOAT NULL,
    h_mag            FLOAT NULL,
    max_brightness_mag FLOAT NULL,
    relative_velocity_kms FLOAT NULL,
    cai_index        FLOAT NULL,

    CONSTRAINT FK_ESA_Upcoming_Asteroide FOREIGN KEY (id_asteroide) REFERENCES dbo.Asteroide(id_asteroide)
);
GO
CREATE INDEX IX_ESA_Upcoming_DesignationKey ON dbo.ESA_UpcomingCloseApproaches(designation_key);
GO

CREATE TABLE dbo.ESA_SearchResult (
    id_esa_search INT IDENTITY(1,1) PRIMARY KEY,
    id_asteroide INT NULL,
    object_designation NVARCHAR(100) NOT NULL,

    designation_key AS (
        REPLACE(REPLACE(REPLACE(REPLACE(UPPER(object_designation),'(',''),')',''),' ',''),'-','')
    ) PERSISTED,

    CONSTRAINT FK_ESA_Search_Asteroide FOREIGN KEY (id_asteroide) REFERENCES dbo.Asteroide(id_asteroide)
);
GO
CREATE INDEX IX_ESA_Search_DesignationKey ON dbo.ESA_SearchResult(designation_key);
GO
