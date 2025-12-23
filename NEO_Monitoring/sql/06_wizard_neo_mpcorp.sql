USE BD_PL2_09;
GO
SET NOCOUNT ON;
GO

/* ============================================================
   PATCH: MPCORB → Asteroide + Solucao_Orbital (corrige CTE final2)
   ============================================================ */

IF OBJECT_ID('tempdb..#mpcorb_final') IS NOT NULL
    DROP TABLE #mpcorb_final;

;WITH base AS (
    SELECT
        LTRIM(RTRIM(mw.designation)) AS pdes,
        COALESCE(NULLIF(LTRIM(RTRIM(mw.designation_full)), ''), LTRIM(RTRIM(mw.designation))) AS nome_completo,
        TRY_CONVERT(FLOAT, mw.abs_mag) AS H_mag,
        TRY_CONVERT(INT, mw.is_neo) AS is_neo,
        UPPER(LTRIM(RTRIM(mw.epoch))) AS epoch_packed,

        TRY_CONVERT(FLOAT, mw.eccentricity)    AS e,
        TRY_CONVERT(FLOAT, mw.semi_major_axis) AS a,
        TRY_CONVERT(FLOAT, mw.inclination)     AS inc,
        TRY_CONVERT(FLOAT, mw.long_asc_node)   AS om,
        TRY_CONVERT(FLOAT, mw.arg_perihelion)  AS w,
        TRY_CONVERT(FLOAT, mw.mean_anomaly)    AS ma,
        TRY_CONVERT(FLOAT, mw.rms_residual)    AS rms
    FROM dbo.mpcorb_wizard mw
    WHERE mw.designation IS NOT NULL AND LTRIM(RTRIM(mw.designation)) <> ''
),
packed AS (
    SELECT
        b.*,
        CASE WHEN LEN(b.epoch_packed) >= 5 THEN LEFT(b.epoch_packed,1) END        AS c,
        CASE WHEN LEN(b.epoch_packed) >= 5 THEN SUBSTRING(b.epoch_packed,2,2) END AS yy,
        CASE WHEN LEN(b.epoch_packed) >= 5 THEN SUBSTRING(b.epoch_packed,4,1) END AS mmc,
        CASE WHEN LEN(b.epoch_packed) >= 5 THEN SUBSTRING(b.epoch_packed,5,1) END AS ddc
    FROM base b
),
conv AS (
    SELECT
        p.*,
        (CASE p.c
            WHEN 'I' THEN 1800
            WHEN 'J' THEN 1900
            WHEN 'K' THEN 2000
            WHEN 'L' THEN 2100
            ELSE NULL
         END) + TRY_CONVERT(INT, p.yy) AS yyyy,

        (CASE
            WHEN p.mmc BETWEEN '1' AND '9' THEN TRY_CONVERT(INT, p.mmc)
            WHEN p.mmc='A' THEN 10
            WHEN p.mmc='B' THEN 11
            WHEN p.mmc='C' THEN 12
            ELSE NULL
         END) AS mm,

        (CASE
            WHEN p.ddc BETWEEN '1' AND '9' THEN TRY_CONVERT(INT, p.ddc)
            WHEN p.ddc='A' THEN 10 WHEN p.ddc='B' THEN 11 WHEN p.ddc='C' THEN 12
            WHEN p.ddc='D' THEN 13 WHEN p.ddc='E' THEN 14 WHEN p.ddc='F' THEN 15
            WHEN p.ddc='G' THEN 16 WHEN p.ddc='H' THEN 17 WHEN p.ddc='I' THEN 18
            WHEN p.ddc='J' THEN 19 WHEN p.ddc='K' THEN 20 WHEN p.ddc='L' THEN 21
            WHEN p.ddc='M' THEN 22 WHEN p.ddc='N' THEN 23 WHEN p.ddc='O' THEN 24
            WHEN p.ddc='P' THEN 25 WHEN p.ddc='Q' THEN 26 WHEN p.ddc='R' THEN 27
            WHEN p.ddc='S' THEN 28 WHEN p.ddc='T' THEN 29 WHEN p.ddc='U' THEN 30
            WHEN p.ddc='V' THEN 31
            ELSE NULL
         END) AS dd
    FROM packed p
),
final AS (
    SELECT
        c.pdes, c.nome_completo, c.H_mag, c.is_neo,
        c.e, c.a, c.inc, c.om, c.w, c.ma, c.rms,
        CASE
            WHEN c.yyyy IS NOT NULL AND c.mm IS NOT NULL AND c.dd IS NOT NULL
            THEN DATEFROMPARTS(c.yyyy, c.mm, c.dd)
            ELSE NULL
        END AS data_epoca
    FROM conv c
),
final2 AS (
    SELECT
        f.*,
        CASE
            WHEN f.data_epoca IS NULL THEN NULL
            ELSE (
                367.0*YEAR(f.data_epoca)
                - FLOOR(7.0*(YEAR(f.data_epoca) + FLOOR((MONTH(f.data_epoca)+9)/12.0))/4.0)
                + FLOOR(275.0*MONTH(f.data_epoca)/9.0)
                + DAY(f.data_epoca)
                + 1721013.5
            )
        END AS epoca_jd
    FROM final f
)
SELECT *
INTO #mpcorb_final
FROM final2;

-- 4.1 Inserir asteroides MPCORB que ainda não existem
INSERT INTO dbo.Asteroide
(id_csv_original, spkid, pdes, nome_completo, flag_neo, flag_pha, H_mag, diametro_km, albedo, moid_ua, moid_ld, id_classe_orbital)
SELECT
    NULL, NULL,
    f.pdes,
    f.nome_completo,
    CASE WHEN f.is_neo = 1 THEN 1 ELSE 0 END,
    0,
    f.H_mag,
    NULL, NULL, NULL, NULL,
    NULL
FROM #mpcorb_final f
WHERE NOT EXISTS (SELECT 1 FROM dbo.Asteroide a WHERE a.pdes = f.pdes);

-- 4.2 Atualizar campos em falta (H_mag/nome/flag_neo)
UPDATE a
SET
    a.H_mag = COALESCE(a.H_mag, f.H_mag),
    a.nome_completo = CASE WHEN a.nome_completo IS NULL OR a.nome_completo='' THEN f.nome_completo ELSE a.nome_completo END,
    a.flag_neo = CASE WHEN a.flag_neo=1 THEN 1 WHEN f.is_neo=1 THEN 1 ELSE a.flag_neo END
FROM dbo.Asteroide a
JOIN #mpcorb_final f ON f.pdes = a.pdes;

-- 4.3 Inserir uma solução orbital “mpcorb_wizard” por objeto (a mais recente)
;WITH ranked AS (
    SELECT
        f.*,
        ROW_NUMBER() OVER (PARTITION BY f.pdes ORDER BY f.data_epoca DESC, f.epoca_jd DESC) AS rn
    FROM #mpcorb_final f
    WHERE f.e IS NOT NULL AND f.a IS NOT NULL
)
INSERT INTO dbo.Solucao_Orbital
(id_asteroide, epoca_jd, excentricidade, semi_eixo_maior_ua, inclinacao_graus, nodo_asc_graus,
 arg_perihelio_graus, anomalia_media_graus, moid_ua, moid_ld, rms, solucao_atual, origem, data_epoca)
SELECT
    a.id_asteroide,
    r.epoca_jd,
    r.e, r.a, r.inc, r.om, r.w, r.ma,
    NULL, NULL, r.rms,
    CASE
        WHEN EXISTS (SELECT 1 FROM dbo.Solucao_Orbital so WHERE so.id_asteroide=a.id_asteroide AND so.solucao_atual=1)
        THEN 0 ELSE 1
    END,
    'mpcorb_wizard',
    r.data_epoca
FROM ranked r
JOIN dbo.Asteroide a ON a.pdes = r.pdes
WHERE r.rn = 1
  AND NOT EXISTS (
      SELECT 1
      FROM dbo.Solucao_Orbital so
      WHERE so.id_asteroide = a.id_asteroide
        AND so.origem = 'mpcorb_wizard'
        AND ( (so.epoca_jd = r.epoca_jd) OR (so.epoca_jd IS NULL AND r.epoca_jd IS NULL) )
  );

DROP TABLE #mpcorb_final;

PRINT '=== PATCH MPCORB OK: Asteroide + Solucao_Orbital sincronizados ===';
GO
