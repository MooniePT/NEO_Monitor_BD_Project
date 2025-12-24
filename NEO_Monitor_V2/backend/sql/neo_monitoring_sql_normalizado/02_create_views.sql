------------------------------------------------------------
-- 02_create_views.sql
-- Objetivo: Views de apoio (dashboard / aplicação Python)
-- DB alvo: BD_PL2_09
------------------------------------------------------------
USE [BD_PL2_09];
GO
SET NOCOUNT ON;
GO

------------------------------------------------------------
-- 1) Asteroide com diâmetro estimado (quando diametro_km é NULL)
-- Fórmula: D(km) = 1329 / sqrt(albedo) * 10^(-H/5)
-- Se albedo NULL → 0.14 (média típica)
------------------------------------------------------------
IF OBJECT_ID('dbo.vw_Asteroide_ComDiametro','V') IS NOT NULL DROP VIEW dbo.vw_Asteroide_ComDiametro;
GO
CREATE VIEW dbo.vw_Asteroide_ComDiametro
AS
SELECT
    a.*,
    COALESCE(
        a.diametro_km,
        1329.0 * POWER(10.0, -a.h_mag/5.0) / SQRT(COALESCE(a.albedo, 0.14))
    ) AS diametro_estimado_km,
    COALESCE(
        a.diametro_km,
        1329.0 * POWER(10.0, -a.h_mag/5.0) / SQRT(COALESCE(a.albedo, 0.14))
    ) * 1000.0 AS diametro_estimado_m
FROM dbo.Asteroide a;
GO

------------------------------------------------------------
-- 2) Solução orbital atual por asteroide
------------------------------------------------------------
IF OBJECT_ID('dbo.vw_SolucaoOrbital_Atual','V') IS NOT NULL DROP VIEW dbo.vw_SolucaoOrbital_Atual;
GO
CREATE VIEW dbo.vw_SolucaoOrbital_Atual
AS
SELECT so.*
FROM dbo.Solucao_Orbital so
WHERE so.solucao_atual = 1;
GO

------------------------------------------------------------
-- 3) Próxima aproximação futura por asteroide (evento mais próximo)
------------------------------------------------------------
IF OBJECT_ID('dbo.vw_ProximaAproximacao','V') IS NOT NULL DROP VIEW dbo.vw_ProximaAproximacao;
GO
CREATE VIEW dbo.vw_ProximaAproximacao
AS
WITH x AS (
    SELECT
        ap.*,
        ROW_NUMBER() OVER (PARTITION BY ap.id_asteroide ORDER BY ap.datahora_aprox ASC) rn
    FROM dbo.Aproximacao_Proxima ap
    WHERE ap.datahora_aprox >= SYSUTCDATETIME()
)
SELECT * FROM x WHERE rn=1;
GO

------------------------------------------------------------
-- 4) Alertas ativos (detalhe)
------------------------------------------------------------
IF OBJECT_ID('dbo.vw_Alertas_Ativos','V') IS NOT NULL DROP VIEW dbo.vw_Alertas_Ativos;
GO
CREATE VIEW dbo.vw_Alertas_Ativos
AS
SELECT
    al.id_alerta,
    al.datahora_geracao,
    al.codigo_regra,
    al.titulo,
    al.descricao,
    pa.codigo AS prioridade_codigo,
    pa.nome   AS prioridade_nome,
    na.codigo AS nivel_codigo,
    na.cor    AS nivel_cor,
    a.id_asteroide,
    a.pdes,
    a.nome_completo,
    a.flag_neo,
    a.flag_pha,
    sod.moid_ld,
    sod.rms,
    ap.datahora_aprox AS prox_evento_data,
    ap.distancia_ld   AS prox_evento_ld
FROM dbo.Alerta al
JOIN dbo.Asteroide a ON a.id_asteroide = al.id_asteroide
JOIN dbo.Prioridade_Alerta pa ON pa.id_prio_alerta = al.id_prio_alerta
LEFT JOIN dbo.Nivel_Alerta na ON na.id_nivel_alerta = al.id_nivel_alerta
LEFT JOIN dbo.vw_SolucaoOrbital_Atual sod ON sod.id_asteroide = a.id_asteroide
LEFT JOIN dbo.vw_ProximaAproximacao ap ON ap.id_asteroide = a.id_asteroide
WHERE al.ativo = 1;
GO

------------------------------------------------------------
-- 5) Estatísticas pedidas no Manual
------------------------------------------------------------
IF OBJECT_ID('dbo.vw_Estatisticas_Alertas','V') IS NOT NULL DROP VIEW dbo.vw_Estatisticas_Alertas;
GO
CREATE VIEW dbo.vw_Estatisticas_Alertas
AS
SELECT
    SUM(CASE WHEN nivel_cor='VERMELHO' THEN 1 ELSE 0 END) AS n_alertas_vermelhos,
    SUM(CASE WHEN nivel_cor='LARANJA' THEN 1 ELSE 0 END)  AS n_alertas_laranja,
    COUNT(*) AS n_alertas_ativos,
    SUM(CASE WHEN flag_pha=1 AND diametro_estimado_m > 100 THEN 1 ELSE 0 END) AS n_pha_maior_100m
FROM (
    SELECT
        a.id_asteroide, a.flag_pha,
        COALESCE(
            a.diametro_km,
            1329.0 * POWER(10.0, -a.h_mag/5.0) / SQRT(COALESCE(a.albedo, 0.14))
        ) * 1000.0 AS diametro_estimado_m,
        na.cor AS nivel_cor
    FROM dbo.vw_Alertas_Ativos va
    JOIN dbo.Asteroide a ON a.id_asteroide = va.id_asteroide
    LEFT JOIN dbo.Nivel_Alerta na ON na.codigo = va.nivel_codigo
) x;
GO

------------------------------------------------------------
-- 6) Próximos eventos críticos: próxima aproximação <5 LD
------------------------------------------------------------
IF OBJECT_ID('dbo.vw_Proximos_Eventos_Criticos','V') IS NOT NULL DROP VIEW dbo.vw_Proximos_Eventos_Criticos;
GO
CREATE VIEW dbo.vw_Proximos_Eventos_Criticos
AS
SELECT
    a.id_asteroide,
    a.pdes,
    a.nome_completo,
    p.datahora_aprox,
    p.distancia_ld,
    p.veloc_relativa_kms
FROM dbo.vw_ProximaAproximacao p
JOIN dbo.Asteroide a ON a.id_asteroide = p.id_asteroide
WHERE p.distancia_ld IS NOT NULL AND p.distancia_ld < 5
ORDER BY p.datahora_aprox ASC;
GO

------------------------------------------------------------
-- 7) Novos NEOs no último mês (quando data_descoberta existir)
------------------------------------------------------------
IF OBJECT_ID('dbo.vw_Novos_NEOs_UltimoMes','V') IS NOT NULL DROP VIEW dbo.vw_Novos_NEOs_UltimoMes;
GO
CREATE VIEW dbo.vw_Novos_NEOs_UltimoMes
AS
SELECT COUNT(*) AS n_novos_neos
FROM dbo.Asteroide
WHERE flag_neo = 1
  AND data_descoberta >= DATEADD(MONTH, -1, CAST(SYSUTCDATETIME() AS DATE));
GO

------------------------------------------------------------
-- 8) Evolução da precisão (RMS médio por mês de import)
------------------------------------------------------------
IF OBJECT_ID('dbo.vw_RMS_Medio_Mensal','V') IS NOT NULL DROP VIEW dbo.vw_RMS_Medio_Mensal;
GO
CREATE VIEW dbo.vw_RMS_Medio_Mensal
AS
SELECT
    DATEFROMPARTS(YEAR(dt_import), MONTH(dt_import), 1) AS mes,
    AVG(rms) AS rms_medio,
    COUNT(*) AS n_solucoes
FROM dbo.Solucao_Orbital
WHERE rms IS NOT NULL
GROUP BY DATEFROMPARTS(YEAR(dt_import), MONTH(dt_import), 1);
GO

------------------------------------------------------------
-- 9) Observações (trilha completa: asteroide→obs→centro/equip/software/astrónomo)
------------------------------------------------------------
IF OBJECT_ID('dbo.vw_Observacoes_Detalhe','V') IS NOT NULL DROP VIEW dbo.vw_Observacoes_Detalhe;
GO
CREATE VIEW dbo.vw_Observacoes_Detalhe
AS
SELECT
    o.id_observacao,
    o.datahora_observacao,
    o.duracao_min,
    o.modo,
    o.seeing_arcsec,
    o.magnitude,
    a.id_asteroide,
    a.pdes,
    a.nome_completo,
    c.codigo AS centro_codigo,
    c.nome   AS centro_nome,
    e.nome   AS equipamento_nome,
    e.tipo   AS equipamento_tipo,
    e.modelo AS equipamento_modelo,
    STRING_AGG(DISTINCT astro.nome_completo, '; ') WITHIN GROUP (ORDER BY astro.nome_completo) AS astronomos,
    STRING_AGG(DISTINCT s.nome, '; ') WITHIN GROUP (ORDER BY s.nome) AS software,
    COUNT(DISTINCT i.id_imagem) AS n_imagens
FROM dbo.Observacao o
JOIN dbo.Asteroide a ON a.id_asteroide = o.id_asteroide
JOIN dbo.Equipamento e ON e.id_equipamento = o.id_equipamento
JOIN dbo.Centro_Observacao c ON c.id_centro = e.id_centro
LEFT JOIN dbo.Observacao_Astronomo oa ON oa.id_observacao = o.id_observacao
LEFT JOIN dbo.Astronomo astro ON astro.id_astronomo = oa.id_astronomo
LEFT JOIN dbo.Observacao_Software osw ON osw.id_observacao = o.id_observacao
LEFT JOIN dbo.Software s ON s.id_software = osw.id_software
LEFT JOIN dbo.Imagem i ON i.id_observacao = o.id_observacao
GROUP BY
    o.id_observacao, o.datahora_observacao, o.duracao_min, o.modo, o.seeing_arcsec, o.magnitude,
    a.id_asteroide, a.pdes, a.nome_completo,
    c.codigo, c.nome, e.nome, e.tipo, e.modelo;
GO
