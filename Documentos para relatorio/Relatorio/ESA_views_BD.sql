--------------------------------------------------------------------
-- Views ESA
--------------------------------------------------------------------
USE BD_PL2_09;
GO

--------------------------------------------------------------------
-- View: Risco atual ESA (lista de risco principal)
--------------------------------------------------------------------
IF OBJECT_ID('dbo.vw_ESA_Lista_Risco_Atual','V') IS NOT NULL
    DROP VIEW dbo.vw_ESA_Lista_Risco_Atual;
GO

CREATE VIEW dbo.vw_ESA_Lista_Risco_Atual
AS
SELECT
    r.id_risco_atual,
    r.num_lista,
    r.designacao_objeto,
    r.diametro_m_texto,
    r.datahora_impacto_utc,
    r.ip_max_texto,
    r.ps_max,
    r.ts,
    r.anos_intervalo,
    r.ip_cum_texto,
    r.ps_cum,
    r.velocidade_kms,
    r.dias_na_lista,

    -- Informação opcional do asteroide (se houver correspondência)
    a.id_asteroide,
    a.pdes,
    a.nome_completo      AS nome_asteroide,
    a.flag_neo,
    a.flag_pha,
    a.H_mag,
    a.diametro_km
FROM dbo.ESA_LISTA_RISCO_ATUAL AS r
LEFT JOIN dbo.ASTEROIDE AS a
       ON a.pdes = r.designacao_objeto;
GO

--------------------------------------------------------------------
-- View: Risco especial ESA
--------------------------------------------------------------------
IF OBJECT_ID('dbo.vw_ESA_Lista_Risco_Especial','V') IS NOT NULL
    DROP VIEW dbo.vw_ESA_Lista_Risco_Especial;
GO

CREATE VIEW dbo.vw_ESA_Lista_Risco_Especial
AS
SELECT
    r.id_risco_especial,
    r.num_lista,
    r.designacao_objeto,
    r.diametro_m_texto,
    r.datahora_impacto_utc,
    r.ip_max_texto,
    r.ps_max,
    r.velocidade_kms,
    r.dias_na_lista,
    r.comentario,

    a.id_asteroide,
    a.pdes,
    a.nome_completo      AS nome_asteroide,
    a.flag_neo,
    a.flag_pha,
    a.H_mag,
    a.diametro_km
FROM dbo.ESA_LISTA_RISCO_ESPECIAL AS r
LEFT JOIN dbo.ASTEROIDE AS a
       ON a.pdes = r.designacao_objeto;
GO

--------------------------------------------------------------------
-- View: Impactores passados ESA
--------------------------------------------------------------------
IF OBJECT_ID('dbo.vw_ESA_Impactores_Passados','V') IS NOT NULL
    DROP VIEW dbo.vw_ESA_Impactores_Passados;
GO

CREATE VIEW dbo.vw_ESA_Impactores_Passados
AS
SELECT
    i.id_impactor,
    i.num_lista,
    i.designacao_objeto,
    i.diametro_m_texto,
    i.datahora_impacto_utc,
    i.velocidade_impacto_kms,
    i.fpa_graus,
    i.azimute_graus,
    i.energia_kt,
    i.energia_kt_outras,

    a.id_asteroide,
    a.pdes,
    a.nome_completo      AS nome_asteroide,
    a.flag_neo,
    a.flag_pha,
    a.H_mag,
    a.diametro_km
FROM dbo.ESA_IMPACTORES_PASSADOS AS i
LEFT JOIN dbo.ASTEROIDE AS a
       ON a.pdes = i.designacao_objeto;
GO

--------------------------------------------------------------------
-- View: Objetos removidos da lista de risco
--------------------------------------------------------------------
IF OBJECT_ID('dbo.vw_ESA_Objetos_Removidos_Risco','V') IS NOT NULL
    DROP VIEW dbo.vw_ESA_Objetos_Removidos_Risco;
GO

CREATE VIEW dbo.vw_ESA_Objetos_Removidos_Risco
AS
SELECT
    o.id_remocao,
    o.designacao_objeto,
    o.data_remocao_utc,
    o.data_vi_utc,
    o.ultimo_ip,
    o.ultimo_ps,

    a.id_asteroide,
    a.pdes,
    a.nome_completo      AS nome_asteroide,
    a.flag_neo,
    a.flag_pha
FROM dbo.ESA_OBJETOS_REMOVIDOS_RISCO AS o
LEFT JOIN dbo.ASTEROIDE AS a
       ON a.pdes = o.designacao_objeto;
GO

--------------------------------------------------------------------
-- View: Próximas aproximações (ESA)
--------------------------------------------------------------------
IF OBJECT_ID('dbo.vw_ESA_Aproximacoes_Proximas','V') IS NOT NULL
    DROP VIEW dbo.vw_ESA_Aproximacoes_Proximas;
GO

CREATE VIEW dbo.vw_ESA_Aproximacoes_Proximas
AS
SELECT
    ap.id_aproximacao_esa,
    ap.designacao_objeto,
    ap.datahora_aproximacao_utc,
    ap.miss_dist_km,
    ap.miss_dist_au,
    ap.miss_dist_ld,
    ap.diametro_m_texto,
    ap.H_mag,
    ap.brilho_max_mag,
    ap.vel_rel_kms,
    ap.cai_index,

    a.id_asteroide,
    a.pdes,
    a.nome_completo      AS nome_asteroide,
    a.flag_neo,
    a.flag_pha
FROM dbo.ESA_APROXIMACOES_PROXIMAS AS ap
LEFT JOIN dbo.ASTEROIDE AS a
       ON a.pdes = ap.designacao_objeto;
GO

--------------------------------------------------------------------
-- View: Resumo de risco ESA por objeto
-- (quantas listas aparece, PS máximo e data mais recente de risco)
--------------------------------------------------------------------
IF OBJECT_ID('dbo.vw_ESA_Resumo_Risco_Por_Objeto','V') IS NOT NULL
    DROP VIEW dbo.vw_ESA_Resumo_Risco_Por_Objeto;
GO

CREATE VIEW dbo.vw_ESA_Resumo_Risco_Por_Objeto
AS
SELECT
    base.designacao_objeto,

    a.id_asteroide,
    a.pdes,
    a.nome_completo      AS nome_asteroide,
    a.flag_neo,
    a.flag_pha,

    base.qtd_registos_risco_atual,
    base.ps_max_global,
    base.data_impacto_mais_recente
FROM (
    SELECT
        r.designacao_objeto,
        COUNT(*)                      AS qtd_registos_risco_atual,
        MAX(ISNULL(r.ps_max, 0.0))    AS ps_max_global,
        MAX(r.datahora_impacto_utc)   AS data_impacto_mais_recente
    FROM dbo.ESA_LISTA_RISCO_ATUAL AS r
    GROUP BY r.designacao_objeto
) AS base
LEFT JOIN dbo.ASTEROIDE AS a
       ON a.pdes = base.designacao_objeto;
GO
