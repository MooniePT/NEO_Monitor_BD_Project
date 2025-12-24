------------------------------------------------------------
-- 04_seed_data.sql
-- Objetivo: Popular tabelas de apoio com valores do Manual
-- DB alvo: BD_PL2_09
------------------------------------------------------------
USE [BD_PL2_09];
GO
SET NOCOUNT ON;
GO

------------------------------------------------------------
-- PRIORIDADES (Manual: Alta / Média / Baixa)
------------------------------------------------------------
IF NOT EXISTS (SELECT 1 FROM dbo.Prioridade_Alerta)
BEGIN
    INSERT INTO dbo.Prioridade_Alerta (codigo, nome, descricao)
    VALUES
    ('ALTA',  N'Alta Prioridade',  N'Intervenção imediata / risco elevado'),
    ('MEDIA', N'Média Prioridade', N'Monitorização intensiva'),
    ('BAIXA', N'Baixa Prioridade', N'Análise contínua');
END
GO

------------------------------------------------------------
-- NÍVEIS (Torino Modificado - Manual)
-- Nota: os limiares exatos dependem também do "próximo evento" e do RMS.
-- Aqui guardamos limites gerais; a procedure de alertas aplica as regras temporais.
------------------------------------------------------------
IF NOT EXISTS (SELECT 1 FROM dbo.Nivel_Alerta)
BEGIN
    INSERT INTO dbo.Nivel_Alerta
        (codigo, cor, descricao, diametro_min_m, diametro_max_m, moid_min_ld, moid_max_ld, rms_max, janela_dias)
    VALUES
        ('N1', 'VERDE',   N'PHAs com diâmetro 50–500m e MOID_LD entre 20–100', 50, 500, 20, 100, NULL, NULL),
        ('N2', 'AMARELO', N'Diâmetro >100m e MOID_LD 5–20 nos próximos 180 dias', 100, NULL, 5, 20, NULL, 180),
        ('N3', 'LARANJA', N'Diâmetro >50m, MOID_LD <5 e RMS <0.3', 50, NULL, NULL, 5, 0.3, NULL),
        ('N4', 'VERMELHO',N'Diâmetro >30m, próxima passagem <1 LD nos próximos 30 dias', 30, NULL, NULL, 1, NULL, 30);
END
GO

------------------------------------------------------------
-- SOFTWARE (opcional / placeholders não inventados: apenas 2 comuns)
------------------------------------------------------------
IF NOT EXISTS (SELECT 1 FROM dbo.Software)
BEGIN
    INSERT INTO dbo.Software (nome, versao, fornecedor, tipo_licenca, website)
    VALUES
      (N'Astrometry.net', NULL, N'Community', N'Open Source', N'https://astrometry.net'),
      (N'Find_Orb', NULL, N'Project Pluto', N'Freeware', N'https://www.projectpluto.com/find_orb.htm');
END
GO
