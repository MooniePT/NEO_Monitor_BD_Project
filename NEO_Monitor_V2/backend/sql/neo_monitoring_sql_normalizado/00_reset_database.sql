------------------------------------------------------------
-- 00_reset_database.sql
-- Objetivo: Remover (pela ordem correta) views, procedures, triggers e tabelas
-- DB alvo: BD_PL2_09
------------------------------------------------------------
USE [BD_PL2_09];
GO
SET NOCOUNT ON;
GO

------------------------------------------------------------
-- 1) DROP VIEWS
------------------------------------------------------------
DECLARE @sql NVARCHAR(MAX) = N'';

SELECT @sql = @sql + N'DROP VIEW ' + QUOTENAME(SCHEMA_NAME(v.schema_id)) + N'.' + QUOTENAME(v.name) + N';' + CHAR(10)
FROM sys.views v
WHERE v.name LIKE 'vw\_%' ESCAPE '\';

IF (@sql <> N'') EXEC sp_executesql @sql;
GO

------------------------------------------------------------
-- 2) DROP PROCEDURES (sp_...)
------------------------------------------------------------
DECLARE @sql2 NVARCHAR(MAX) = N'';

SELECT @sql2 = @sql2 + N'DROP PROCEDURE ' + QUOTENAME(SCHEMA_NAME(p.schema_id)) + N'.' + QUOTENAME(p.name) + N';' + CHAR(10)
FROM sys.procedures p
WHERE p.name LIKE 'sp\_%' ESCAPE '\';

IF (@sql2 <> N'') EXEC sp_executesql @sql2;
GO

------------------------------------------------------------
-- 3) DROP TRIGGERS (TRG_...)
------------------------------------------------------------
DECLARE @sql3 NVARCHAR(MAX) = N'';

SELECT @sql3 = @sql3 + N'DROP TRIGGER ' + QUOTENAME(SCHEMA_NAME(t.schema_id)) + N'.' + QUOTENAME(t.name) + N';' + CHAR(10)
FROM sys.triggers t
WHERE t.parent_id <> 0 AND t.name LIKE 'TRG\_%' ESCAPE '\';

IF (@sql3 <> N'') EXEC sp_executesql @sql3;
GO

------------------------------------------------------------
-- 4) DROP TABLES (staging + ESA + core) pela ordem (dependências)
------------------------------------------------------------
-- STAGING
IF OBJECT_ID('stg.neo_wizard','U') IS NOT NULL DROP TABLE stg.neo_wizard;
IF OBJECT_ID('stg.mpcorb_wizard','U') IS NOT NULL DROP TABLE stg.mpcorb_wizard;
IF OBJECT_ID('stg.esa_risklist','U') IS NOT NULL DROP TABLE stg.esa_risklist;
IF OBJECT_ID('stg.esa_specialrisklist','U') IS NOT NULL DROP TABLE stg.esa_specialrisklist;
IF OBJECT_ID('stg.esa_removedrisk','U') IS NOT NULL DROP TABLE stg.esa_removedrisk;
IF OBJECT_ID('stg.esa_pastimpactors','U') IS NOT NULL DROP TABLE stg.esa_pastimpactors;
IF OBJECT_ID('stg.esa_upcomingclapp','U') IS NOT NULL DROP TABLE stg.esa_upcomingclapp;
IF OBJECT_ID('stg.esa_searchresult','U') IS NOT NULL DROP TABLE stg.esa_searchresult;
IF OBJECT_ID('stg.centro_observacoes','U') IS NOT NULL DROP TABLE stg.centro_observacoes;
IF OBJECT_ID('stg.equipamento','U') IS NOT NULL DROP TABLE stg.equipamento;
GO

-- ESA (core)
IF OBJECT_ID('dbo.ESA_RiskList','U') IS NOT NULL DROP TABLE dbo.ESA_RiskList;
IF OBJECT_ID('dbo.ESA_SpecialRiskList','U') IS NOT NULL DROP TABLE dbo.ESA_SpecialRiskList;
IF OBJECT_ID('dbo.ESA_RemovedFromRiskList','U') IS NOT NULL DROP TABLE dbo.ESA_RemovedFromRiskList;
IF OBJECT_ID('dbo.ESA_PastImpactors','U') IS NOT NULL DROP TABLE dbo.ESA_PastImpactors;
IF OBJECT_ID('dbo.ESA_UpcomingCloseApproaches','U') IS NOT NULL DROP TABLE dbo.ESA_UpcomingCloseApproaches;
IF OBJECT_ID('dbo.ESA_SearchResult','U') IS NOT NULL DROP TABLE dbo.ESA_SearchResult;
GO

-- OBSERVACIONAL (junctions primeiro)
IF OBJECT_ID('dbo.Observacao_Software','U') IS NOT NULL DROP TABLE dbo.Observacao_Software;
IF OBJECT_ID('dbo.Observacao_Astronomo','U') IS NOT NULL DROP TABLE dbo.Observacao_Astronomo;
IF OBJECT_ID('dbo.Imagem','U') IS NOT NULL DROP TABLE dbo.Imagem;
IF OBJECT_ID('dbo.Observacao','U') IS NOT NULL DROP TABLE dbo.Observacao;
IF OBJECT_ID('dbo.Software','U') IS NOT NULL DROP TABLE dbo.Software;
IF OBJECT_ID('dbo.Astronomo','U') IS NOT NULL DROP TABLE dbo.Astronomo;
IF OBJECT_ID('dbo.Equipamento','U') IS NOT NULL DROP TABLE dbo.Equipamento;
IF OBJECT_ID('dbo.Centro_Observacao','U') IS NOT NULL DROP TABLE dbo.Centro_Observacao;
GO

-- ALERTAS / NEO
IF OBJECT_ID('dbo.Alerta','U') IS NOT NULL DROP TABLE dbo.Alerta;
IF OBJECT_ID('dbo.Aproximacao_Proxima','U') IS NOT NULL DROP TABLE dbo.Aproximacao_Proxima;
IF OBJECT_ID('dbo.Solucao_Orbital','U') IS NOT NULL DROP TABLE dbo.Solucao_Orbital;
IF OBJECT_ID('dbo.Asteroide','U') IS NOT NULL DROP TABLE dbo.Asteroide;
IF OBJECT_ID('dbo.Classe_Orbital','U') IS NOT NULL DROP TABLE dbo.Classe_Orbital;
IF OBJECT_ID('dbo.Nivel_Alerta','U') IS NOT NULL DROP TABLE dbo.Nivel_Alerta;
IF OBJECT_ID('dbo.Prioridade_Alerta','U') IS NOT NULL DROP TABLE dbo.Prioridade_Alerta;
IF OBJECT_ID('dbo.Import_Log','U') IS NOT NULL DROP TABLE dbo.Import_Log;
GO

------------------------------------------------------------
-- 5) DROP SCHEMA STG (se vazio)
------------------------------------------------------------
IF EXISTS (SELECT 1 FROM sys.schemas WHERE name='stg')
BEGIN
    IF NOT EXISTS (SELECT 1 FROM sys.objects o JOIN sys.schemas s ON s.schema_id=o.schema_id WHERE s.name='stg')
        EXEC('DROP SCHEMA stg;');
END
GO
