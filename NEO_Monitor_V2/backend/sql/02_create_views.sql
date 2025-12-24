------------------------------------------------------------
-- File: sql/02_create_views.sql
-- Descrição: Views NEO + ESA
------------------------------------------------------------
USE BD_PL2_09;
GO

------------------------------------------------------------
-- VIEWS NEO / ASTEROIDES
------------------------------------------------------------

IF OBJECT_ID('dbo.vw_Ultimos5AsteroidesDetetados','V') IS NOT NULL
    DROP VIEW dbo.vw_Ultimos5AsteroidesDetetados;
GO

CREATE VIEW dbo.vw_Ultimos5AsteroidesDetetados
AS
SELECT TOP (5)
       a.id_asteroide,
       a.nome_completo,
       a.pdes,
       a.flag_neo,
       a.flag_pha,
       a.diametro_km
FROM   dbo.Asteroide AS a
ORDER BY a.id_asteroide DESC;
GO

IF OBJECT_ID('dbo.vw_AsteroidesNEO','V') IS NOT NULL
    DROP VIEW dbo.vw_AsteroidesNEO;
GO

CREATE VIEW dbo.vw_AsteroidesNEO
AS
SELECT a.*
FROM   dbo.Asteroide AS a
WHERE  a.flag_neo = 1;
GO

IF OBJECT_ID('dbo.vw_AsteroidesPHA','V') IS NOT NULL
    DROP VIEW dbo.vw_AsteroidesPHA;
GO

CREATE VIEW dbo.vw_AsteroidesPHA
AS
SELECT a.*
FROM   dbo.Asteroide AS a
WHERE  a.flag_pha = 1;
GO

IF OBJECT_ID('dbo.vw_AsteroidesNEOePHA','V') IS NOT NULL
    DROP VIEW dbo.vw_AsteroidesNEOePHA;
GO

CREATE VIEW dbo.vw_AsteroidesNEOePHA
AS
SELECT a.*
FROM   dbo.Asteroide AS a
WHERE  a.flag_neo = 1
  AND  a.flag_pha = 1;
GO

IF OBJECT_ID('dbo.vw_CentrosComMaisObservacoes','V') IS NOT NULL
    DROP VIEW dbo.vw_CentrosComMaisObservacoes;
GO

CREATE VIEW dbo.vw_CentrosComMaisObservacoes
AS
SELECT
    c.id_centro,
    c.codigo,
    c.nome,
    c.pais,
    c.cidade,
    COUNT(DISTINCT o.id_observacao) AS total_observacoes
FROM dbo.Centro_Observacao AS c
LEFT JOIN dbo.Equipamento AS e
       ON e.id_centro = c.id_centro
LEFT JOIN dbo.Observacao AS o
       ON o.id_equipamento = e.id_equipamento
GROUP BY
    c.id_centro,
    c.codigo,
    c.nome,
    c.pais,
    c.cidade;
GO

IF OBJECT_ID('dbo.vw_RankingAsteroidesPHA_MaiorDiametro','V') IS NOT NULL
    DROP VIEW dbo.vw_RankingAsteroidesPHA_MaiorDiametro;
GO

CREATE VIEW dbo.vw_RankingAsteroidesPHA_MaiorDiametro
AS
SELECT
    a.id_asteroide,
    a.nome_completo,
    a.pdes,
    a.diametro_km,
    DENSE_RANK() OVER (ORDER BY a.diametro_km DESC) AS posicao_ranking
FROM dbo.Asteroide AS a
WHERE a.flag_pha = 1;
GO

IF OBJECT_ID('dbo.vw_Observacoes_Completo','V') IS NOT NULL
    DROP VIEW dbo.vw_Observacoes_Completo;
GO

CREATE VIEW dbo.vw_Observacoes_Completo
AS
SELECT
    o.id_observacao,
    o.datahora_observacao,
    o.duracao_min,
    o.modo,
    o.seeing_arcseg,
    o.filtro,
    o.magnitude,
    o.notas,

    a.id_asteroide,
    a.nome_completo      AS nome_asteroide,
    a.flag_neo,
    a.flag_pha,

    ast.id_astronomo,
    ast.nome_completo    AS nome_astronomo,
    ast.email,

    c.id_centro,
    c.nome               AS nome_centro,
    c.pais,
    c.cidade,

    e.id_equipamento,
    e.nome               AS nome_equipamento,
    e.tipo,
    e.modelo,

    s.id_software,
    s.nome               AS nome_software,
    s.versao
FROM dbo.Observacao AS o
JOIN dbo.Asteroide        AS a   ON a.id_asteroide   = o.id_asteroide
JOIN dbo.Astronomo        AS ast ON ast.id_astronomo = o.id_astronomo
JOIN dbo.Equipamento      AS e   ON e.id_equipamento = o.id_equipamento
JOIN dbo.Centro_Observacao AS c  ON c.id_centro      = e.id_centro
JOIN dbo.Software         AS s   ON s.id_software    = o.id_software;
GO

IF OBJECT_ID('dbo.vw_Alertas_Ativos_Detalhe','V') IS NOT NULL
    DROP VIEW dbo.vw_Alertas_Ativos_Detalhe;
GO

CREATE VIEW dbo.vw_Alertas_Ativos_Detalhe
AS
SELECT
    al.id_alerta,
    al.datahora_geracao,
    al.codigo_regra,
    al.titulo,
    al.descricao,
    al.ativo,

    a.id_asteroide,
    a.nome_completo        AS nome_asteroide,
    a.flag_neo,
    a.flag_pha,

    pa.codigo              AS prioridade_codigo,
    pa.nome                AS prioridade_nome,

    na.codigo              AS nivel_codigo,
    na.cor                 AS nivel_cor,

    al.id_solucao_orbital,
    al.id_aproximacao_proxima
FROM dbo.Alerta AS al
JOIN dbo.Asteroide         AS a  ON a.id_asteroide          = al.id_asteroide
JOIN dbo.Prioridade_Alerta AS pa ON pa.id_prioridade_alerta = al.id_prioridade_alerta
LEFT JOIN dbo.Nivel_Alerta AS na ON na.id_nivel_alerta      = al.id_nivel_alerta
WHERE al.ativo = 1;
GO

IF OBJECT_ID('dbo.vw_ResumoAlertasPorNivel','V') IS NOT NULL
    DROP VIEW dbo.vw_ResumoAlertasPorNivel;
GO

CREATE VIEW dbo.vw_ResumoAlertasPorNivel
AS
SELECT
    na.codigo        AS nivel_codigo,
    na.cor           AS nivel_cor,
    COUNT(*)         AS total_alertas_ativos
FROM dbo.Alerta AS al
LEFT JOIN dbo.Nivel_Alerta AS na
       ON na.id_nivel_alerta = al.id_nivel_alerta
WHERE al.ativo = 1
GROUP BY
    na.codigo,
    na.cor;
GO

IF OBJECT_ID('dbo.vw_Asteroide_OrbitalAtual','V') IS NOT NULL
    DROP VIEW dbo.vw_Asteroide_OrbitalAtual;
GO

CREATE VIEW dbo.vw_Asteroide_OrbitalAtual
AS
SELECT
    a.id_asteroide,
    a.nome_completo      AS nome_asteroide,
    a.pdes,
    a.flag_neo,
    a.flag_pha,

    so.id_solucao_orbital,
    so.epoca_jd,
    so.excentricidade,
    so.semi_eixo_maior_ua,
    so.inclinacao_graus,
    so.moid_ua,
    so.moid_ld,
    so.rms
FROM dbo.Asteroide AS a
LEFT JOIN dbo.Solucao_Orbital AS so
       ON so.id_asteroide  = a.id_asteroide
      AND so.solucao_atual = 1;
GO

IF OBJECT_ID('dbo.vw_ProximasAproximacoesCriticas','V') IS NOT NULL
    DROP VIEW dbo.vw_ProximasAproximacoesCriticas;
GO

CREATE VIEW dbo.vw_ProximasAproximacoesCriticas
AS
SELECT
    ap.id_aproximacao_proxima,
    ap.id_asteroide,
    ap.id_solucao_orbital,
    ap.datahora_aproximacao,
    ap.distancia_ua,
    ap.distancia_ld,
    ap.velocidade_rel_kms
FROM dbo.Aproximacao_Proxima AS ap
WHERE ap.distancia_ld IS NOT NULL
  AND ap.distancia_ld <= 5
  AND ap.datahora_aproximacao >= SYSDATETIME();
GO

------------------------------------------------------------
-- VIEWS ESA
------------------------------------------------------------

IF OBJECT_ID('dbo.vw_ESA_Lista_Risco_Atual','V') IS NOT NULL
    DROP VIEW dbo.vw_ESA_Lista_Risco_Atual;
GO

CREATE VIEW dbo.vw_ESA_Lista_Risco_Atual
AS
SELECT
    esa.id_risco_atual,
    esa.num_lista,
    esa.designacao_objeto,
    esa.diametro_m_texto,
    esa.datahora_impacto_utc,
    esa.ip_max_texto,
    esa.ps_max,
    esa.ts,
    esa.anos_intervalo,
    esa.ip_cum_texto,
    esa.ps_cum,
    esa.velocidade_kms,
    esa.dias_na_lista,
    esa.id_asteroide,
    a.nome_completo AS nome_asteroide
FROM dbo.ESA_LISTA_RISCO_ATUAL AS esa
LEFT JOIN dbo.Asteroide AS a
       ON a.id_asteroide = esa.id_asteroide;
GO

IF OBJECT_ID('dbo.vw_ESA_Aproximacoes_Proximas','V') IS NOT NULL
    DROP VIEW dbo.vw_ESA_Aproximacoes_Proximas;
GO

CREATE VIEW dbo.vw_ESA_Aproximacoes_Proximas
AS
SELECT
    esa.id_aproximacao_esa,
    esa.designacao_objeto,
    esa.datahora_aproximacao_utc,
    esa.miss_dist_km,
    esa.miss_dist_au,
    esa.miss_dist_ld,
    esa.diametro_m_texto,
    esa.H_mag,
    esa.brilho_max_mag,
    esa.vel_rel_kms,
    esa.cai_index,
    esa.id_asteroide,
    a.nome_completo AS nome_asteroide
FROM dbo.ESA_APROXIMACOES_PROXIMAS AS esa
LEFT JOIN dbo.Asteroide AS a
       ON a.id_asteroide = esa.id_asteroide;
GO

IF OBJECT_ID('dbo.vw_ESA_Resumo_Risco_Por_Objeto','V') IS NOT NULL
    DROP VIEW dbo.vw_ESA_Resumo_Risco_Por_Objeto;
GO

CREATE VIEW dbo.vw_ESA_Resumo_Risco_Por_Objeto
AS
SELECT
    esa.designacao_objeto,
    MAX(esa.ps_max)        AS ps_maxima,
    MAX(esa.datahora_impacto_utc) AS impacto_mais_recente,
    COUNT(*)               AS total_registos
FROM dbo.ESA_LISTA_RISCO_ATUAL AS esa
GROUP BY esa.designacao_objeto;
GO
