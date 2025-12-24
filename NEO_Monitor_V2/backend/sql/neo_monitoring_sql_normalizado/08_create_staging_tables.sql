------------------------------------------------------------
-- 08_create_staging_tables.sql
-- Objetivo: Criar tabelas de STAGING para importação via SSMS "Import Data"
-- DB alvo: BD_PL2_09
-- Nota: Estas tabelas são para receber CSVs (neo.csv, MPCORB.csv, ESA*.csv, centros/equipamento).
------------------------------------------------------------
USE [BD_PL2_09];
GO
SET NOCOUNT ON;
GO

------------------------------------------------------------
-- STAGING NEO (neo.csv ; separado por ';')
-- Estratégia robusta: tudo como texto (NVARCHAR) e converter com TRY_CONVERT no wizard/import.
------------------------------------------------------------
IF OBJECT_ID('stg.neo_wizard','U') IS NOT NULL DROP TABLE stg.neo_wizard;
GO
CREATE TABLE stg.neo_wizard (
    id                 NVARCHAR(50)  NULL,
    spkid              NVARCHAR(50)  NULL,
    full_name          NVARCHAR(255) NULL,
    pdes               NVARCHAR(50)  NULL,
    name               NVARCHAR(120) NULL,
    prefix             NVARCHAR(40)  NULL,
    neo                NVARCHAR(10)  NULL,
    pha                NVARCHAR(10)  NULL,
    h                  NVARCHAR(50)  NULL,
    diameter           NVARCHAR(50)  NULL,
    albedo             NVARCHAR(50)  NULL,
    diameter_sigma     NVARCHAR(50)  NULL,
    orbit_id           NVARCHAR(50)  NULL,
    epoch              NVARCHAR(50)  NULL,
    epoch_mjd          NVARCHAR(50)  NULL,
    epoch_cal          NVARCHAR(50)  NULL,
    equinox            NVARCHAR(50)  NULL,
    e                  NVARCHAR(50)  NULL,
    a                  NVARCHAR(50)  NULL,
    q                  NVARCHAR(50)  NULL,
    i                  NVARCHAR(50)  NULL,
    om                 NVARCHAR(50)  NULL,
    w                  NVARCHAR(50)  NULL,
    ma                 NVARCHAR(50)  NULL,
    ad                 NVARCHAR(50)  NULL,
    n                  NVARCHAR(50)  NULL,
    tp                 NVARCHAR(50)  NULL,
    tp_cal             NVARCHAR(50)  NULL,
    per                NVARCHAR(50)  NULL,
    per_y              NVARCHAR(50)  NULL,
    moid               NVARCHAR(50)  NULL,
    moid_ld            NVARCHAR(50)  NULL,
    sigma_e            NVARCHAR(50)  NULL,
    sigma_a            NVARCHAR(50)  NULL,
    sigma_q            NVARCHAR(50)  NULL,
    sigma_i            NVARCHAR(50)  NULL,
    sigma_om           NVARCHAR(50)  NULL,
    sigma_w            NVARCHAR(50)  NULL,
    sigma_ma           NVARCHAR(50)  NULL,
    sigma_ad           NVARCHAR(50)  NULL,
    sigma_n            NVARCHAR(50)  NULL,
    sigma_tp           NVARCHAR(50)  NULL,
    sigma_per          NVARCHAR(50)  NULL,
    class              NVARCHAR(50)  NULL,
    rms                NVARCHAR(50)  NULL,
    class_description  NVARCHAR(255) NULL
);
GO

------------------------------------------------------------
-- STAGING MPCORB (colunas mínimas usadas pelo teu wizard)
------------------------------------------------------------
IF OBJECT_ID('stg.mpcorb_wizard','U') IS NOT NULL DROP TABLE stg.mpcorb_wizard;
GO
CREATE TABLE stg.mpcorb_wizard (
    designation         NVARCHAR(60)  NULL,
    designation_full    NVARCHAR(255) NULL,
    epoch               NVARCHAR(20)  NULL,   -- packed epoch (ex: K24A1)
    abs_mag             NVARCHAR(50)  NULL,
    eccentricity        NVARCHAR(50)  NULL,
    semi_major_axis     NVARCHAR(50)  NULL,
    inclination         NVARCHAR(50)  NULL,
    long_asc_node       NVARCHAR(50)  NULL,
    arg_perihelion      NVARCHAR(50)  NULL,
    mean_anomaly        NVARCHAR(50)  NULL,
    rms_residual        NVARCHAR(50)  NULL,
    is_neo              NVARCHAR(10)  NULL
);
GO

------------------------------------------------------------
-- STAGING ESA (riskList, specialRiskList, removed..., past..., upcoming..., searchResult)
------------------------------------------------------------
IF OBJECT_ID('stg.esa_risklist','U') IS NOT NULL DROP TABLE stg.esa_risklist;
GO
CREATE TABLE stg.esa_risklist (
    no_                 NVARCHAR(20) NULL,
    object_designation  NVARCHAR(120) NULL,
    diameter_in_m       NVARCHAR(50) NULL,
    impact_datetime_utc NVARCHAR(60) NULL,
    ip_max              NVARCHAR(50) NULL,
    ps_max              NVARCHAR(50) NULL,
    ts                  NVARCHAR(50) NULL,
    years               NVARCHAR(50) NULL,
    ip_cum              NVARCHAR(50) NULL,
    ps_cum              NVARCHAR(50) NULL,
    vel_kms             NVARCHAR(50) NULL,
    in_list_since_days  NVARCHAR(50) NULL
);
GO

IF OBJECT_ID('stg.esa_specialrisklist','U') IS NOT NULL DROP TABLE stg.esa_specialrisklist;
GO
CREATE TABLE stg.esa_specialrisklist (
    no_                 NVARCHAR(20) NULL,
    object_designation  NVARCHAR(120) NULL,
    diameter_in_m       NVARCHAR(50) NULL,
    impact_datetime_utc NVARCHAR(60) NULL,
    ip_max              NVARCHAR(50) NULL,
    ps_max              NVARCHAR(50) NULL,
    vel_kms             NVARCHAR(50) NULL,
    in_list_since_days  NVARCHAR(50) NULL,
    comment             NVARCHAR(255) NULL
);
GO

IF OBJECT_ID('stg.esa_removedrisk','U') IS NOT NULL DROP TABLE stg.esa_removedrisk;
GO
CREATE TABLE stg.esa_removedrisk (
    object_designation  NVARCHAR(120) NULL,
    removal_date_utc    NVARCHAR(60) NULL,
    vi_date_utc         NVARCHAR(60) NULL,
    last_ip             NVARCHAR(50) NULL,
    last_ps             NVARCHAR(50) NULL
);
GO

IF OBJECT_ID('stg.esa_pastimpactors','U') IS NOT NULL DROP TABLE stg.esa_pastimpactors;
GO
CREATE TABLE stg.esa_pastimpactors (
    no_                     NVARCHAR(20) NULL,
    object_designation      NVARCHAR(120) NULL,
    diameter_in_m           NVARCHAR(50) NULL,
    impact_datetime_utc     NVARCHAR(60) NULL,
    impact_velocity_kms     NVARCHAR(50) NULL,
    impact_fpa_deg          NVARCHAR(50) NULL,
    impact_azimuth_deg      NVARCHAR(50) NULL,
    estimated_energy_kt     NVARCHAR(50) NULL,
    estimated_energy_other_kt NVARCHAR(50) NULL
);
GO

IF OBJECT_ID('stg.esa_upcomingclapp','U') IS NOT NULL DROP TABLE stg.esa_upcomingclapp;
GO
CREATE TABLE stg.esa_upcomingclapp (
    object_designation        NVARCHAR(120) NULL,
    close_approach_date_utc   NVARCHAR(60) NULL,
    miss_distance_km          NVARCHAR(60) NULL,
    miss_distance_au          NVARCHAR(60) NULL,
    miss_distance_ld          NVARCHAR(60) NULL,
    diameter_in_m             NVARCHAR(60) NULL,
    h_mag                     NVARCHAR(60) NULL,
    max_brightness_mag        NVARCHAR(60) NULL,
    relative_velocity_kms     NVARCHAR(60) NULL,
    cai_index                 NVARCHAR(60) NULL
);
GO

IF OBJECT_ID('stg.esa_searchresult','U') IS NOT NULL DROP TABLE stg.esa_searchresult;
GO
CREATE TABLE stg.esa_searchresult (
    object_designation NVARCHAR(120) NULL
);
GO

------------------------------------------------------------
-- STAGING CENTROS / EQUIPAMENTO (CSV fornecidos no projeto)
------------------------------------------------------------
IF OBJECT_ID('stg.centro_observacoes','U') IS NOT NULL DROP TABLE stg.centro_observacoes;
GO
CREATE TABLE stg.centro_observacoes (
    id_centro      NVARCHAR(50) NULL,
    codigo         NVARCHAR(20) NULL,
    nome           NVARCHAR(200) NULL,
    pais           NVARCHAR(120) NULL,
    cidade         NVARCHAR(120) NULL,
    latitude       NVARCHAR(60) NULL,
    longitude      NVARCHAR(60) NULL,
    altitude_m     NVARCHAR(60) NULL
);
GO

IF OBJECT_ID('stg.equipamento','U') IS NOT NULL DROP TABLE stg.equipamento;
GO
CREATE TABLE stg.equipamento (
    id_equipamento      NVARCHAR(50) NULL,
    id_centro           NVARCHAR(50) NULL,
    nome                NVARCHAR(200) NULL,
    tipo                NVARCHAR(60) NULL,
    modelo              NVARCHAR(200) NULL,
    abertura_m          NVARCHAR(60) NULL,
    distancia_focal_m   NVARCHAR(60) NULL,
    notas               NVARCHAR(600) NULL
);
GO
