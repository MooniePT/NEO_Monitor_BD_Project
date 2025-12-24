------------------------------------------------------------
-- 99_verify_import.sql
-- Objetivo: Verificações finais (integridade + views + triggers)
------------------------------------------------------------
USE [BD_PL2_09];
GO
SET NOCOUNT ON;
GO

PRINT '--- CONTAGENS ---';
SELECT 'Asteroide' AS tabela, COUNT(*) AS n FROM dbo.Asteroide
UNION ALL SELECT 'Solucao_Orbital', COUNT(*) FROM dbo.Solucao_Orbital
UNION ALL SELECT 'Aproximacao_Proxima', COUNT(*) FROM dbo.Aproximacao_Proxima
UNION ALL SELECT 'Alerta', COUNT(*) FROM dbo.Alerta
UNION ALL SELECT 'ESA_RiskList', COUNT(*) FROM dbo.ESA_RiskList
UNION ALL SELECT 'Centro_Observacao', COUNT(*) FROM dbo.Centro_Observacao
UNION ALL SELECT 'Equipamento', COUNT(*) FROM dbo.Equipamento;
GO

PRINT '--- ORFÃOS (deve dar 0) ---';
SELECT COUNT(*) AS orfaos_solucao FROM dbo.Solucao_Orbital so LEFT JOIN dbo.Asteroide a ON a.id_asteroide=so.id_asteroide WHERE a.id_asteroide IS NULL;
SELECT COUNT(*) AS orfaos_aprox  FROM dbo.Aproximacao_Proxima ap LEFT JOIN dbo.Asteroide a ON a.id_asteroide=ap.id_asteroide WHERE a.id_asteroide IS NULL;
SELECT COUNT(*) AS orfaos_alerta FROM dbo.Alerta al LEFT JOIN dbo.Asteroide a ON a.id_asteroide=al.id_asteroide WHERE a.id_asteroide IS NULL;
GO

PRINT '--- VIEWS (amostras) ---';
SELECT TOP (5) * FROM dbo.vw_Asteroide_ComDiametro ORDER BY id_asteroide DESC;
SELECT TOP (20) * FROM dbo.vw_Alertas_Ativos ORDER BY datahora_geracao DESC;
SELECT * FROM dbo.vw_Estatisticas_Alertas;
SELECT TOP (20) * FROM dbo.vw_Proximos_Eventos_Criticos ORDER BY datahora_aprox ASC;
SELECT TOP (20) * FROM dbo.vw_RMS_Medio_Mensal ORDER BY mes DESC;
GO

PRINT '--- TRIGGERS EXISTENTES ---';
SELECT
    t.name AS trigger_name,
    OBJECT_NAME(t.parent_id) AS tabela,
    t.is_disabled
FROM sys.triggers t
WHERE t.parent_id <> 0
ORDER BY tabela, trigger_name;
GO

PRINT '--- REAVALIAR ALERTAS (run manual) ---';
DECLARE @ids dbo.IntList; -- vazio => todos
EXEC dbo.sp_ReavaliarAlertas @Asteroides=@ids;
GO

SELECT TOP (50) * FROM dbo.vw_Alertas_Ativos ORDER BY datahora_geracao DESC;
GO
