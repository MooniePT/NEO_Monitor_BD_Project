------------------------------------------------------------
-- File: sql/99_verify_import.sql
-- Descrição: Queries de verificação após importação
------------------------------------------------------------
USE BD_PL2_09;
GO

PRINT '=== VERIFICAÇÃO DA IMPORTAÇÃO DE DADOS ==='
GO

------------------------------------------------------------
-- 1. CONTAGENS GERAIS
------------------------------------------------------------
PRINT '1. Contagens Gerais:'
PRINT '===================='
GO

SELECT 'Asteroides' AS Tabela, COUNT(*) AS Total FROM dbo.Asteroide
UNION ALL
SELECT 'Soluções Orbitais', COUNT(*) FROM dbo.Solucao_Orbital
UNION ALL
SELECT 'Classes Orbitais', COUNT(*) FROM dbo.Classe_Orbital
UNION ALL
SELECT 'ESA Risk List', COUNT(*) FROM dbo.ESA_LISTA_RISCO_ATUAL
UNION ALL
SELECT 'ESA Special Risk', COUNT(*) FROM dbo.ESA_LISTA_RISCO_ESPECIAL
UNION ALL
SELECT 'ESA Past Impactors', COUNT(*) FROM dbo.ESA_IMPACTORES_PASSADOS
UNION ALL
SELECT 'ESA Removed', COUNT(*) FROM dbo.ESA_OBJETOS_REMOVIDOS_RISCO
UNION ALL
SELECT 'ESA Close Approaches', COUNT(*) FROM dbo.ESA_APROXIMACOES_PROXIMAS;
GO

------------------------------------------------------------
-- 2. ASTEROIDES NEO vs PHA
------------------------------------------------------------
PRINT ''
PRINT '2. Análise NEO/PHA:'
PRINT '==================='
GO

SELECT 
    COUNT(*) AS Total_Asteroides,
    SUM(CASE WHEN flag_neo = 1 THEN 1 ELSE 0 END) AS Total_NEOs,
    SUM(CASE WHEN flag_pha = 1 THEN 1 ELSE 0 END) AS Total_PHAs,
    CAST(SUM(CASE WHEN flag_neo = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS DECIMAL(5,2)) AS Percentagem_NEO,
    CAST(SUM(CASE WHEN flag_pha = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS DECIMAL(5,2)) AS Percentagem_PHA
FROM dbo.Asteroide;
GO

------------------------------------------------------------
-- 3. DISTRIBUIÇÃO POR CLASSE ORBITAL
------------------------------------------------------------
PRINT ''
PRINT '3. Distribuição por Classe Orbital:'
PRINT '===================================='
GO

SELECT 
    ISNULL(co.codigo, 'SEM CLASSE') AS Codigo,
    ISNULL(co.nome, 'Sem classificação') AS Nome_Classe,
    COUNT(a.id_asteroide) AS Num_Asteroides,
    CAST(COUNT(a.id_asteroide) * 100.0 / 
        (SELECT COUNT(*) FROM dbo.Asteroide) AS DECIMAL(5,2)) AS Percentagem
FROM dbo.Asteroide a
LEFT JOIN dbo.Classe_Orbital co ON a.id_classe_orbital = co.id_classe_orbital
GROUP BY co.codigo, co.nome
ORDER BY Num_Asteroides DESC;
GO

------------------------------------------------------------
-- 4. QUALIDADE DOS DADOS
------------------------------------------------------------
PRINT ''
PRINT '4. Qualidade dos Dados:'
PRINT '======================='
GO

SELECT 
    'Asteroides com nome completo' AS Metrica,
    COUNT(*) AS Quantidade,
    CAST(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM dbo.Asteroide) AS DECIMAL(5,2)) AS Percentagem
FROM dbo.Asteroide WHERE nome_completo IS NOT NULL AND nome_completo != ''
UNION ALL
SELECT 'Asteroides com H_mag', COUNT(*), 
    CAST(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM dbo.Asteroide) AS DECIMAL(5,2))
FROM dbo.Asteroide WHERE H_mag IS NOT NULL
UNION ALL
SELECT 'Asteroides com diâmetro', COUNT(*),
    CAST(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM dbo.Asteroide) AS DECIMAL(5,2))
FROM dbo.Asteroide WHERE diametro_km IS NOT NULL
UNION ALL
SELECT 'Asteroides com albedo', COUNT(*),
    CAST(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM dbo.Asteroide) AS DECIMAL(5,2))
FROM dbo.Asteroide WHERE albedo IS NOT NULL
UNION ALL
SELECT 'Asteroides com MOID', COUNT(*),
    CAST(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM dbo.Asteroide) AS DECIMAL(5,2))
FROM dbo.Asteroide WHERE moid_ua IS NOT NULL
UNION ALL
SELECT 'Asteroides com spkid', COUNT(*),
    CAST(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM dbo.Asteroide) AS DECIMAL(5,2))
FROM dbo.Asteroide WHERE spkid IS NOT NULL
UNION ALL
SELECT 'Asteroides com classificação', COUNT(*),
    CAST(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM dbo.Asteroide) AS DECIMAL(5,2))
FROM dbo.Asteroide WHERE id_classe_orbital IS NOT NULL;
GO

------------------------------------------------------------
-- 5. ESTATÍSTICAS DOS DADOS ORBITAIS
------------------------------------------------------------
PRINT ''
PRINT '5. Estatísticas Dados Orbitais:'
PRINT '================================'
GO

SELECT 
    COUNT(*) AS Total_Solucoes,
    COUNT(DISTINCT id_asteroide) AS Asteroides_Com_Orbital,
    AVG(excentricidade) AS Media_Excentricidade,
    MIN(excentricidade) AS Min_Excentricidade,
    MAX(excentricidade) AS Max_Excentricidade,
    AVG(semi_eixo_maior_ua) AS Media_Semi_Eixo_UA,
    AVG(inclinacao_graus) AS Media_Inclinacao_Graus
FROM dbo.Solucao_Orbital;
GO

------------------------------------------------------------
-- 6. PRIMEIROS 5 ASTEROIDES (AMOSTRA)
------------------------------------------------------------
PRINT ''
PRINT '6. Amostra dos Primeiros 5 Asteroides:'
PRINT '======================================='
GO

SELECT TOP 5
    a.id_asteroide,
    a.pdes,
    a.nome_completo,
    a.flag_neo,
    a.flag_pha,
    a.H_mag,
    a.diametro_km,
    a.albedo,
    co.codigo AS classe,
    CASE WHEN so.id_solucao_orbital IS NOT NULL THEN 'Sim' ELSE 'Não' END AS Tem_Orbital
FROM dbo.Asteroide a
LEFT JOIN dbo.Classe_Orbital co ON a.id_classe_orbital = co.id_classe_orbital
LEFT JOIN dbo.Solucao_Orbital so ON so.id_asteroide = a.id_asteroide AND so.solucao_atual = 1
ORDER BY a.id_asteroide;
GO

------------------------------------------------------------
-- 7. VERIFICAR INTEGRIDADE REFERENCIAL
------------------------------------------------------------
PRINT ''
PRINT '7. Integridade Referencial:'
PRINT '==========================='
GO

-- Asteroides órfãos nas tabelas ESA (não deveriam existir)
SELECT 'ESA Risk (órfãos)' AS Tabela, COUNT(*) AS Total
FROM dbo.ESA_LISTA_RISCO_ATUAL
WHERE id_asteroide IS NOT NULL 
  AND id_asteroide NOT IN (SELECT id_asteroide FROM dbo.Asteroide)
UNION ALL
SELECT 'ESA Aproximações (órfãos)', COUNT(*)
FROM dbo.ESA_APROXIMACOES_PROXIMAS
WHERE id_asteroide IS NOT NULL 
  AND id_asteroide NOT IN (SELECT id_asteroide FROM dbo.Asteroide);
GO

------------------------------------------------------------
-- 8. TOP 10 ASTEROIDES MAIS PERIGOSOS (PHAs)
------------------------------------------------------------
PRINT ''
PRINT '8. Top 10 PHAs (menor MOID):'
PRINT '============================='
GO

SELECT TOP 10
    a.pdes,
    a.nome_completo,
    a.H_mag,
    a.diametro_km,
    a.moid_ua,
    a.moid_ld,
    co.codigo AS classe
FROM dbo.Asteroide a
LEFT JOIN dbo.Classe_Orbital co ON a.id_classe_orbital = co.id_classe_orbital
WHERE a.flag_pha = 1 AND a.moid_ua IS NOT NULL
ORDER BY a.moid_ua ASC;
GO

PRINT ''
PRINT '=== VERIFICAÇÃO CONCLUÍDA ==='
GO
