------------------------------------------------------------
-- 06_wizard_neo_mpcorb.sql
-- Objetivo:
--   1) Importar/conciliar NEO (stg.neo_wizard) → Asteroide + Classe_Orbital + Solucao_Orbital
--   2) Importar/conciliar MPCORB (stg.mpcorb_wizard) → Asteroide + Solucao_Orbital
-- Nota: Para performance em cargas grandes, recomenda-se criar views/triggers DEPOIS do load.
------------------------------------------------------------
USE [BD_PL2_09];
GO
SET NOCOUNT ON;
SET XACT_ABORT ON;
GO

BEGIN TRY
    BEGIN TRAN;

    ------------------------------------------------------------
    -- Helper inline: normalizar texto (converter ''/nan para NULL)
    ------------------------------------------------------------
    -- (usamos NULLIF em cada campo quando necessário)

    ------------------------------------------------------------
    -- 1) CLASSES ORBITAIS (NEO)
    ------------------------------------------------------------
    ;WITH c AS (
        SELECT DISTINCT
            LTRIM(RTRIM([class])) AS codigo,
            NULLIF(LTRIM(RTRIM([class_description])), '') AS descricao
        FROM stg.neo_wizard
        WHERE NULLIF(LTRIM(RTRIM([class])), '') IS NOT NULL
    )
    MERGE dbo.Classe_Orbital AS t
    USING c AS s
      ON t.codigo = s.codigo
    WHEN MATCHED THEN
      UPDATE SET t.descricao = COALESCE(t.descricao, s.descricao)
    WHEN NOT MATCHED THEN
      INSERT (codigo, descricao) VALUES (s.codigo, s.descricao);
    ------------------------------------------------------------
    -- log
    INSERT INTO dbo.Import_Log(fonte, descricao, linhas_afetadas)
    VALUES ('NEO', N'Upsert Classe_Orbital', @@ROWCOUNT);

    ------------------------------------------------------------
    -- 2) ASTEROIDES (NEO) - INSERT (novos)
    ------------------------------------------------------------
    INSERT INTO dbo.Asteroide
        (nasa_id, spkid, pdes, nome_asteroide, prefixo, nome_completo,
         flag_neo, flag_pha, h_mag, diametro_km, diametro_sigma_km, albedo)
    SELECT
        TRY_CONVERT(INT, NULLIF(NULLIF(LTRIM(RTRIM(s.id)),''),'nan')),
        TRY_CONVERT(BIGINT, NULLIF(NULLIF(LTRIM(RTRIM(s.spkid)),''),'nan')),
        LTRIM(RTRIM(s.pdes)),
        NULLIF(LTRIM(RTRIM(s.name)),''),
        NULLIF(LTRIM(RTRIM(s.prefix)),''),
        NULLIF(LTRIM(RTRIM(s.full_name)),''),
        CASE WHEN UPPER(LTRIM(RTRIM(s.neo)))='Y' THEN 1 ELSE 0 END,
        CASE WHEN UPPER(LTRIM(RTRIM(s.pha)))='Y' THEN 1 ELSE 0 END,
        TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(s.h)),''),'nan')),
        TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(s.diameter)),''),'nan')),
        TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(s.diameter_sigma)),''),'nan')),
        TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(s.albedo)),''),'nan'))
    FROM stg.neo_wizard s
    WHERE NULLIF(LTRIM(RTRIM(s.pdes)), '') IS NOT NULL
      AND NOT EXISTS (
          SELECT 1 FROM dbo.Asteroide a WHERE a.pdes = LTRIM(RTRIM(s.pdes))
      );

    INSERT INTO dbo.Import_Log(fonte, descricao, linhas_afetadas)
    VALUES ('NEO', N'Insert Asteroide (novos)', @@ROWCOUNT);

    ------------------------------------------------------------
    -- 3) ASTEROIDES (NEO) - UPDATE (preencher/atualizar flags e físicos)
    ------------------------------------------------------------
    UPDATE a
    SET
        a.nasa_id = COALESCE(a.nasa_id, TRY_CONVERT(INT, NULLIF(NULLIF(LTRIM(RTRIM(s.id)),''),'nan'))),
        a.spkid   = COALESCE(a.spkid,   TRY_CONVERT(BIGINT, NULLIF(NULLIF(LTRIM(RTRIM(s.spkid)),''),'nan'))),
        a.nome_asteroide = COALESCE(a.nome_asteroide, NULLIF(LTRIM(RTRIM(s.name)),'')),
        a.prefixo        = COALESCE(a.prefixo,        NULLIF(LTRIM(RTRIM(s.prefix)),'')),
        a.nome_completo  = COALESCE(a.nome_completo,  NULLIF(LTRIM(RTRIM(s.full_name)),'')),

        -- flags (se alguma fonte diz Y, ficamos com 1)
        a.flag_neo = CASE WHEN a.flag_neo=1 OR UPPER(LTRIM(RTRIM(s.neo)))='Y' THEN 1 ELSE 0 END,
        a.flag_pha = CASE WHEN a.flag_pha=1 OR UPPER(LTRIM(RTRIM(s.pha)))='Y' THEN 1 ELSE 0 END,

        -- físicos (só preenche se ainda estiver NULL)
        a.h_mag             = COALESCE(a.h_mag, TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(s.h)),''),'nan'))),
        a.diametro_km       = COALESCE(a.diametro_km, TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(s.diameter)),''),'nan'))),
        a.diametro_sigma_km = COALESCE(a.diametro_sigma_km, TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(s.diameter_sigma)),''),'nan'))),
        a.albedo            = COALESCE(a.albedo, TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(s.albedo)),''),'nan')))
    FROM dbo.Asteroide a
    JOIN stg.neo_wizard s
      ON a.pdes = LTRIM(RTRIM(s.pdes));

    INSERT INTO dbo.Import_Log(fonte, descricao, linhas_afetadas)
    VALUES ('NEO', N'Update Asteroide (flags + físicos)', @@ROWCOUNT);

    ------------------------------------------------------------
    -- 4) SOLUÇÕES ORBITAIS (NEO)
    ------------------------------------------------------------
    INSERT INTO dbo.Solucao_Orbital
    (
      id_asteroide, fonte, orbit_id,
      epoch_jd, epoch_mjd, epoch_cal,
      e, a_au, q_au, i_deg, om_deg, w_deg, ma_deg, ad_au, n_deg_d,
      tp_jd, tp_cal, per_d, per_y,
      moid_ua, moid_ld, rms,
      sigma_e, sigma_a, sigma_q, sigma_i, sigma_om, sigma_w, sigma_ma, sigma_ad, sigma_n, sigma_tp, sigma_per,
      id_classe_orbital,
      solucao_atual
    )
    SELECT
      a.id_asteroide,
      'NEO' AS fonte,
      TRY_CONVERT(BIGINT, NULLIF(NULLIF(LTRIM(RTRIM(s.orbit_id)),''),'nan')),
      TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(s.epoch)),''),'nan')),
      TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(s.epoch_mjd)),''),'nan')),
      TRY_CONVERT(DATE,  NULLIF(NULLIF(LTRIM(RTRIM(s.epoch_cal)),''),'nan')),

      TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(s.e)),''),'nan')),
      TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(s.a)),''),'nan')),
      TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(s.q)),''),'nan')),
      TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(s.i)),''),'nan')),
      TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(s.om)),''),'nan')),
      TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(s.w)),''),'nan')),
      TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(s.ma)),''),'nan')),
      TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(s.ad)),''),'nan')),
      TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(s.n)),''),'nan')),

      TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(s.tp)),''),'nan')),
      TRY_CONVERT(DATE,  NULLIF(NULLIF(LTRIM(RTRIM(s.tp_cal)),''),'nan')),
      TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(s.per)),''),'nan')),
      TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(s.per_y)),''),'nan')),

      TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(s.moid)),''),'nan')),
      TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(s.moid_ld)),''),'nan')),
      TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(s.rms)),''),'nan')),

      TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(s.sigma_e)),''),'nan')),
      TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(s.sigma_a)),''),'nan')),
      TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(s.sigma_q)),''),'nan')),
      TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(s.sigma_i)),''),'nan')),
      TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(s.sigma_om)),''),'nan')),
      TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(s.sigma_w)),''),'nan')),
      TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(s.sigma_ma)),''),'nan')),
      TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(s.sigma_ad)),''),'nan')),
      TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(s.sigma_n)),''),'nan')),
      TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(s.sigma_tp)),''),'nan')),
      TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(s.sigma_per)),''),'nan')),

      co.id_classe_orbital,

      0 AS solucao_atual
    FROM stg.neo_wizard s
    JOIN dbo.Asteroide a
      ON a.pdes = LTRIM(RTRIM(s.pdes))
    LEFT JOIN dbo.Classe_Orbital co
      ON co.codigo = NULLIF(LTRIM(RTRIM(s.[class])), '')
    WHERE NULLIF(LTRIM(RTRIM(s.orbit_id)), '') IS NOT NULL
      AND NOT EXISTS (
        SELECT 1
        FROM dbo.Solucao_Orbital so
        WHERE so.id_asteroide = a.id_asteroide
          AND so.fonte = 'NEO'
          AND so.orbit_id = TRY_CONVERT(BIGINT, NULLIF(NULLIF(LTRIM(RTRIM(s.orbit_id)),''),'nan'))
      );

    INSERT INTO dbo.Import_Log(fonte, descricao, linhas_afetadas)
    VALUES ('NEO', N'Insert Solucao_Orbital (NEO)', @@ROWCOUNT);

    ------------------------------------------------------------
    -- 5) Marcar solução atual (NEO): maior epoch_jd / orbit_id por asteroide
    ------------------------------------------------------------
    ;WITH ranked AS (
        SELECT
            so.id_solucao_orbital,
            ROW_NUMBER() OVER (
                PARTITION BY so.id_asteroide
                ORDER BY COALESCE(so.epoch_jd, 0) DESC, COALESCE(so.orbit_id, 0) DESC, so.dt_import DESC
            ) AS rn
        FROM dbo.Solucao_Orbital so
        WHERE so.fonte = 'NEO'
    )
    UPDATE so
    SET so.solucao_atual = CASE WHEN r.rn = 1 THEN 1 ELSE 0 END
    FROM dbo.Solucao_Orbital so
    JOIN ranked r ON r.id_solucao_orbital = so.id_solucao_orbital;

    INSERT INTO dbo.Import_Log(fonte, descricao, linhas_afetadas)
    VALUES ('NEO', N'Update Solucao_Orbital.solucao_atual (NEO)', @@ROWCOUNT);

    ------------------------------------------------------------
    -- 6) IMPORT MPCORB (stg.mpcorb_wizard) → Asteroide + Solucao_Orbital
    -- Converte epoch "packed" (Kyy...).
    ------------------------------------------------------------
    IF EXISTS (SELECT 1 FROM stg.mpcorb_wizard)
    BEGIN
        -- Upsert Asteroide (pdes)
        INSERT INTO dbo.Asteroide (pdes, nome_completo, h_mag, flag_neo)
        SELECT
            LTRIM(RTRIM(m.designation)) AS pdes,
            NULLIF(LTRIM(RTRIM(m.designation_full)), ''),
            TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(m.abs_mag)),''),'nan')),
            CASE WHEN UPPER(LTRIM(RTRIM(m.is_neo))) IN ('1','Y','YES','TRUE','T') THEN 1 ELSE 0 END
        FROM stg.mpcorb_wizard m
        WHERE NULLIF(LTRIM(RTRIM(m.designation)), '') IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM dbo.Asteroide a WHERE a.pdes = LTRIM(RTRIM(m.designation)));

        INSERT INTO dbo.Import_Log(fonte, descricao, linhas_afetadas)
        VALUES ('MPCORB', N'Insert Asteroide (novos)', @@ROWCOUNT);

        UPDATE a
        SET
            a.nome_completo = COALESCE(a.nome_completo, NULLIF(LTRIM(RTRIM(m.designation_full)), '')),
            a.h_mag = COALESCE(a.h_mag, TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(m.abs_mag)),''),'nan'))),
            a.flag_neo = CASE WHEN a.flag_neo=1 OR UPPER(LTRIM(RTRIM(m.is_neo))) IN ('1','Y','YES','TRUE','T') THEN 1 ELSE 0 END
        FROM dbo.Asteroide a
        JOIN stg.mpcorb_wizard m
          ON a.pdes = LTRIM(RTRIM(m.designation));

        INSERT INTO dbo.Import_Log(fonte, descricao, linhas_afetadas)
        VALUES ('MPCORB', N'Update Asteroide (nome/h/neo)', @@ROWCOUNT);

        -- Converter epoch packed → DATE (aproximação: ano 1800/1900/2000/2100 + YY, mês A-L, dia 1-9/A-V)
        ;WITH base AS (
            SELECT
                LTRIM(RTRIM(m.designation)) AS pdes,
                m.epoch AS epoch_packed,
                TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(m.eccentricity)),''),'nan')) AS e,
                TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(m.semi_major_axis)),''),'nan')) AS a_au,
                TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(m.inclination)),''),'nan')) AS i_deg,
                TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(m.long_asc_node)),''),'nan')) AS om_deg,
                TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(m.arg_perihelion)),''),'nan')) AS w_deg,
                TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(m.mean_anomaly)),''),'nan')) AS ma_deg,
                TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(m.rms_residual)),''),'nan')) AS rms
            FROM stg.mpcorb_wizard m
            WHERE NULLIF(LTRIM(RTRIM(m.designation)), '') IS NOT NULL
        ),
        parts AS (
            SELECT
                b.*,
                SUBSTRING(b.epoch_packed,1,1) AS c,
                SUBSTRING(b.epoch_packed,2,2) AS yy,
                SUBSTRING(b.epoch_packed,4,1) AS mmc,
                SUBSTRING(b.epoch_packed,5,1) AS ddc
            FROM base b
            WHERE LEN(b.epoch_packed) >= 5
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
                (ASCII(UPPER(p.mmc)) - ASCII('A') + 1) AS mm,
                CASE
                    WHEN p.ddc BETWEEN '0' AND '9' THEN TRY_CONVERT(INT, p.ddc)
                    WHEN UPPER(p.ddc) BETWEEN 'A' AND 'V' THEN (ASCII(UPPER(p.ddc)) - ASCII('A') + 10)
                    ELSE NULL
                END AS dd
            FROM parts p
        ),
        ready AS (
            SELECT
                c.pdes,
                TRY_CONVERT(DATE, CONCAT(c.yyyy,'-',RIGHT('0'+CONVERT(VARCHAR(2),c.mm),2),'-',RIGHT('0'+CONVERT(VARCHAR(2),c.dd),2))) AS epoch_cal,
                c.e, c.a_au, c.i_deg, c.om_deg, c.w_deg, c.ma_deg, c.rms
            FROM conv c
            WHERE c.yyyy IS NOT NULL AND c.mm BETWEEN 1 AND 12 AND c.dd BETWEEN 1 AND 31
        )
        INSERT INTO dbo.Solucao_Orbital
            (id_asteroide, fonte, orbit_id, epoch_cal, e, a_au, i_deg, om_deg, w_deg, ma_deg, rms, solucao_atual)
        SELECT
            a.id_asteroide,
            'MPCORB' AS fonte,
            NULL AS orbit_id,
            r.epoch_cal,
            r.e, r.a_au, r.i_deg, r.om_deg, r.w_deg, r.ma_deg, r.rms,
            0
        FROM ready r
        JOIN dbo.Asteroide a
          ON a.pdes = r.pdes
        WHERE NOT EXISTS (
            SELECT 1
            FROM dbo.Solucao_Orbital so
            WHERE so.id_asteroide = a.id_asteroide
              AND so.fonte = 'MPCORB'
              AND so.epoch_cal = r.epoch_cal
        );

        INSERT INTO dbo.Import_Log(fonte, descricao, linhas_afetadas)
        VALUES ('MPCORB', N'Insert Solucao_Orbital (MPCORB)', @@ROWCOUNT);

        -- Se um asteroide ainda não tem solução atual, marcar a mais recente MPCORB como atual
        ;WITH rankedM AS (
            SELECT
                so.id_solucao_orbital,
                ROW_NUMBER() OVER (PARTITION BY so.id_asteroide ORDER BY so.epoch_cal DESC, so.dt_import DESC) rn
            FROM dbo.Solucao_Orbital so
            WHERE so.fonte='MPCORB'
        ),
        noCurrent AS (
            SELECT a.id_asteroide
            FROM dbo.Asteroide a
            WHERE NOT EXISTS (SELECT 1 FROM dbo.Solucao_Orbital so WHERE so.id_asteroide=a.id_asteroide AND so.solucao_atual=1)
        )
        UPDATE so
        SET so.solucao_atual = 1
        FROM dbo.Solucao_Orbital so
        JOIN rankedM r ON r.id_solucao_orbital = so.id_solucao_orbital AND r.rn=1
        JOIN noCurrent n ON n.id_asteroide = so.id_asteroide;

        INSERT INTO dbo.Import_Log(fonte, descricao, linhas_afetadas)
        VALUES ('MPCORB', N'Update solucao_atual (apenas onde faltava)', @@ROWCOUNT);
    END

    COMMIT;
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0 ROLLBACK;
    THROW;
END CATCH;
GO
