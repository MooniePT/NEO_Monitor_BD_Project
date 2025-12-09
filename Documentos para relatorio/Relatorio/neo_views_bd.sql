--------------------------------------------------------------------
-- VIEWS NEO / ASTEROIDES
-- Base de dados: BD_PL2_09
--------------------------------------------------------------------
USE BD_PL2_09;
GO

--------------------------------------------------------------------
-- 1) Últimos 5 asteroides detetados
--------------------------------------------------------------------
IF OBJECT_ID('dbo.vw_Ultimos5AsteroidesDetetados','V') IS NOT NULL
    DROP VIEW dbo.vw_Ultimos5AsteroidesDetetados;
GO

CREATE VIEW dbo.vw_Ultimos5AsteroidesDetetados
AS
SELECT TOP (5)
       a.id_asteroide,
       a.nome_completo,
       a.pdes,
       a.data_descoberta,
       a.flag_neo,
       a.flag_pha,
       a.diametro_km
FROM   dbo.Asteroide AS a
ORDER BY a.data_descoberta DESC,
         a.id_asteroide DESC;
GO

--------------------------------------------------------------------
-- 2) Asteroides NEO
--------------------------------------------------------------------
IF OBJECT_ID('dbo.vw_AsteroidesNEO','V') IS NOT NULL
    DROP VIEW dbo.vw_AsteroidesNEO;
GO

CREATE VIEW dbo.vw_AsteroidesNEO
AS
SELECT a.*
FROM   dbo.Asteroide AS a
WHERE  a.flag_neo = 1;
GO

--------------------------------------------------------------------
-- 3) Asteroides PHA
--------------------------------------------------------------------
IF OBJECT_ID('dbo.vw_AsteroidesPHA','V') IS NOT NULL
    DROP VIEW dbo.vw_AsteroidesPHA;
GO

CREATE VIEW dbo.vw_AsteroidesPHA
AS
SELECT a.*
FROM   dbo.Asteroide AS a
WHERE  a.flag_pha = 1;
GO

--------------------------------------------------------------------
-- 4) Asteroides que são NEO E PHA ao mesmo tempo
--------------------------------------------------------------------
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

--------------------------------------------------------------------
-- 5) Centros com mais observações
--------------------------------------------------------------------
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
-- Exemplo de uso:
-- SELECT TOP (10) * FROM dbo.vw_CentrosComMaisObservacoes ORDER BY total_observacoes DESC;

--------------------------------------------------------------------
-- 6) Ranking dos asteroides PHA por maior diâmetro
--------------------------------------------------------------------
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
-- Exemplo:
-- SELECT * FROM dbo.vw_RankingAsteroidesPHA_MaiorDiametro WHERE posicao_ranking <= 10;

--------------------------------------------------------------------
-- 7) Observações com detalhe completo
--------------------------------------------------------------------
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

--------------------------------------------------------------------
-- 8) Alertas activos com detalhe
--------------------------------------------------------------------
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

--------------------------------------------------------------------
-- 9) Resumo de alertas por nível (verde, amarelo, laranja, vermelho, etc.)
--------------------------------------------------------------------
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

--------------------------------------------------------------------
-- 10) Asteroide + solução orbital marcada como actual
--     (usa coluna so.solucao_atual = 1)
--------------------------------------------------------------------
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

--------------------------------------------------------------------
-- 11) Próximas aproximações "críticas"
--     Critério simples: distancia_ld <= 5 e data futura
--------------------------------------------------------------------
IF OBJECT_ID('dbo.vw_ProximasAproximacoesCriticas','V') IS NOT NULL
    DROP VIEW dbo.vw_ProximasAproximacoesCriticas;
GO

CREATE VIEW dbo.vw_ProximasAproximacoesCriticas
AS
SELECT
    ap.id_aproximacao_proxima,
    ap.id_asteroide,
    ap.datahora_aproximacao,
    ap.distancia_ua,
    ap.distancia_ld
FROM dbo.Aproximacao_Proxima AS ap
WHERE ap.distancia_ld IS NOT NULL
  AND ap.distancia_ld <= 5         -- ajusta o critério se quiseres
  AND ap.datahora_aproximacao >= SYSDATETIME();
GO
