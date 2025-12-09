--------------------------------------------------------------------
-- Usar sempre a base de dados do projeto
--------------------------------------------------------------------
USE BD_PL2_09;
GO

--------------------------------------------------------------------
-- 1) Lista de risco atual (riskList.csv)
--------------------------------------------------------------------
IF OBJECT_ID('dbo.ESA_LISTA_RISCO_ATUAL','U') IS NULL
BEGIN
    CREATE TABLE dbo.ESA_LISTA_RISCO_ATUAL (
        id_risco_atual       INT IDENTITY(1,1) PRIMARY KEY,

        -- FK opcional para ASTEROIDE (a preencher no futuro, se quiseres)
        id_asteroide         INT NULL
            CONSTRAINT FK_ESA_RISCO_ATUAL__ASTEROIDE
            REFERENCES dbo.ASTEROIDE(id_asteroide),

        num_lista            INT NULL,              -- "No."
        designacao_objeto    VARCHAR(50) NOT NULL,  -- "Object designation"
        diametro_m_texto     VARCHAR(50) NULL,      -- "Diameter in m"
        datahora_impacto_utc DATETIME NULL,         -- "Impact date/time in UTC"
        ip_max_texto         VARCHAR(20) NULL,      -- "IP max" (ex: '1/425')
        ps_max               FLOAT NULL,            -- "PS max"
        ts                   TINYINT NULL,          -- "TS"
        anos_intervalo       VARCHAR(20) NULL,      -- "Years"
        ip_cum_texto         VARCHAR(20) NULL,      -- "IP cum"
        ps_cum               FLOAT NULL,            -- "PS cum"
        velocidade_kms       FLOAT NULL,            -- "Vel. in km/s"
        dias_na_lista        INT NULL               -- "In list since in d"
    );
END;
GO

--------------------------------------------------------------------
-- 2) Lista de risco especial (specialRiskList.csv)
--------------------------------------------------------------------
IF OBJECT_ID('dbo.ESA_LISTA_RISCO_ESPECIAL','U') IS NULL
BEGIN
    CREATE TABLE dbo.ESA_LISTA_RISCO_ESPECIAL (
        id_risco_especial    INT IDENTITY(1,1) PRIMARY KEY,

        id_asteroide         INT NULL
            CONSTRAINT FK_ESA_RISCO_ESP__ASTEROIDE
            REFERENCES dbo.ASTEROIDE(id_asteroide),

        num_lista            INT NULL,              -- "No."
        designacao_objeto    VARCHAR(50) NOT NULL,  -- "Object designation"
        diametro_m_texto     VARCHAR(50) NULL,      -- "Diameter in m"
        datahora_impacto_utc DATETIME NULL,         -- "Impact date/time in UTC"
        ip_max_texto         VARCHAR(20) NULL,      -- "IP max"
        ps_max               FLOAT NULL,            -- "PS max"
        velocidade_kms       FLOAT NULL,            -- "Vel. in km/s"
        dias_na_lista        INT NULL,              -- "In list since in d"
        comentario           VARCHAR(255) NULL      -- "Comment"
    );
END;
GO

--------------------------------------------------------------------
-- 3) Impactores passados (pastImpactorsList.csv)
--------------------------------------------------------------------
IF OBJECT_ID('dbo.ESA_IMPACTORES_PASSADOS','U') IS NULL
BEGIN
    CREATE TABLE dbo.ESA_IMPACTORES_PASSADOS (
        id_impactor          INT IDENTITY(1,1) PRIMARY KEY,

        id_asteroide         INT NULL
            CONSTRAINT FK_ESA_IMPACTORES__ASTEROIDE
            REFERENCES dbo.ASTEROIDE(id_asteroide),

        num_lista            INT NULL,              -- "No."
        designacao_objeto    VARCHAR(50) NOT NULL,  -- "Object designation"
        diametro_m_texto     VARCHAR(50) NULL,      -- "Diameter in m"
        datahora_impacto_utc DATETIME NULL,         -- "Impact date/time in UTC"
        velocidade_impacto_kms FLOAT NULL,          -- "Impact velocity in km/s"
        fpa_graus            FLOAT NULL,            -- "Impact FPA in deg"
        azimute_graus        FLOAT NULL,            -- "Impact azimuth in deg"
        energia_kt           FLOAT NULL,            -- "Estimated energy in kt"
        energia_kt_outras    FLOAT NULL             -- "Estimated energy from other sources in kt"
    );
END;
GO

--------------------------------------------------------------------
-- 4) Objetos removidos da lista de risco (removedObjectsFromRiskList.csv)
--------------------------------------------------------------------
IF OBJECT_ID('dbo.ESA_OBJETOS_REMOVIDOS_RISCO','U') IS NULL
BEGIN
    CREATE TABLE dbo.ESA_OBJETOS_REMOVIDOS_RISCO (
        id_remocao           INT IDENTITY(1,1) PRIMARY KEY,

        id_asteroide         INT NULL
            CONSTRAINT FK_ESA_REMOVIDOS__ASTEROIDE
            REFERENCES dbo.ASTEROIDE(id_asteroide),

        designacao_objeto    VARCHAR(50) NOT NULL,  -- "Object designation"
        data_remocao_utc     DATETIME NULL,         -- "Removal date in UTC"
        data_vi_utc          DATETIME NULL,         -- "VI date in UTC"
        ultimo_ip            FLOAT NULL,            -- "Last IP"
        ultimo_ps            FLOAT NULL             -- "Last PS"
    );
END;
GO

--------------------------------------------------------------------
-- 5) Próximas aproximações (upcomingClApp.csv)
--------------------------------------------------------------------
IF OBJECT_ID('dbo.ESA_APROXIMACOES_PROXIMAS','U') IS NULL
BEGIN
    CREATE TABLE dbo.ESA_APROXIMACOES_PROXIMAS (
        id_aproximacao_esa   INT IDENTITY(1,1) PRIMARY KEY,

        id_asteroide         INT NULL
            CONSTRAINT FK_ESA_APROX__ASTEROIDE
            REFERENCES dbo.ASTEROIDE(id_asteroide),

        designacao_objeto        VARCHAR(50) NOT NULL,  -- "Object designation"
        datahora_aproximacao_utc DATETIME NULL,         -- "Close approach date in UTC"
        miss_dist_km             FLOAT NULL,            -- "Miss distance in km"
        miss_dist_au             FLOAT NULL,            -- "Miss distance in au"
        miss_dist_ld             FLOAT NULL,            -- "Miss distance in LD"
        diametro_m_texto         VARCHAR(50) NULL,      -- "Diameter in m"
        H_mag                    FLOAT NULL,            -- "H in mag"
        brilho_max_mag           FLOAT NULL,            -- "Maximum brightness in mag"
        vel_rel_kms              FLOAT NULL,            -- "Relative velocity in km/s"
        cai_index                FLOAT NULL             -- "CAI Index"
    );
END;
GO

--------------------------------------------------------------------
-- 6) Resultados de pesquisa (searchResult.csv)
--------------------------------------------------------------------
IF OBJECT_ID('dbo.ESA_RESULTADOS_PESQUISA','U') IS NULL
BEGIN
    CREATE TABLE dbo.ESA_RESULTADOS_PESQUISA (
        id_pesquisa          INT IDENTITY(1,1) PRIMARY KEY,
        designacao_objeto    VARCHAR(50) NOT NULL  -- "Object designation"
    );
END;
GO
