------------------------------------------------------------
-- 03_create_triggers.sql
-- Objetivo: Triggers + procedures para regras do Manual
-- IMPORTANTE (performance):
--   Para cargas massivas (neo.csv ~ 958k), recomenda-se:
--   1) importar para stg.*
--   2) executar 06/05/07 (loads set-based)
--   3) criar triggers depois (este script)
------------------------------------------------------------
USE [BD_PL2_09];
GO
SET NOCOUNT ON;
SET XACT_ABORT ON;
GO

------------------------------------------------------------
-- TYPE para passar listas de IDs a procedures (TVP)
------------------------------------------------------------
IF TYPE_ID('dbo.IntList') IS NOT NULL DROP TYPE dbo.IntList;
GO
CREATE TYPE dbo.IntList AS TABLE (id INT NOT NULL PRIMARY KEY);
GO

------------------------------------------------------------
-- PROCEDURE: Reavaliar alertas para uma lista de asteroides
------------------------------------------------------------
IF OBJECT_ID('dbo.sp_ReavaliarAlertas','P') IS NOT NULL DROP PROCEDURE dbo.sp_ReavaliarAlertas;
GO
CREATE PROCEDURE dbo.sp_ReavaliarAlertas
    @Asteroides dbo.IntList READONLY -- se vazio => processa TODOS
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @now DATETIME2(0) = SYSUTCDATETIME();

    ;WITH alvo AS (
        SELECT a.id_asteroide
        FROM dbo.Asteroide a
        WHERE NOT EXISTS (SELECT 1 FROM @Asteroides)  -- lista vazia
           OR EXISTS (SELECT 1 FROM @Asteroides x WHERE x.id = a.id_asteroide)
    ),
    fis AS (
        SELECT
            a.id_asteroide,
            a.flag_pha,
            a.flag_neo,
            COALESCE(
                a.diametro_km,
                1329.0 * POWER(10.0, -a.h_mag/5.0) / SQRT(COALESCE(a.albedo, 0.14))
            ) * 1000.0 AS diam_m,
            a.albedo,
            a.h_mag
        FROM dbo.Asteroide a
        JOIN alvo t ON t.id_asteroide = a.id_asteroide
    ),
    so_atual AS (
        SELECT so.*
        FROM dbo.Solucao_Orbital so
        JOIN alvo t ON t.id_asteroide = so.id_asteroide
        WHERE so.solucao_atual = 1
    ),
    so_prev AS (
        SELECT *
        FROM (
            SELECT
                so.id_asteroide, so.e, so.i_deg,
                ROW_NUMBER() OVER (PARTITION BY so.id_asteroide ORDER BY so.dt_import DESC, so.id_solucao_orbital DESC) AS rn
            FROM dbo.Solucao_Orbital so
            JOIN alvo t ON t.id_asteroide = so.id_asteroide
        ) x
        WHERE x.rn = 2
    ),
    next_ca AS (
        SELECT *
        FROM (
            SELECT
                ap.id_asteroide,
                ap.id_aprox_prox,
                ap.datahora_aprox,
                ap.distancia_ld,
                ap.distancia_ua,
                ap.veloc_relativa_kms,
                ROW_NUMBER() OVER (PARTITION BY ap.id_asteroide ORDER BY ap.datahora_aprox ASC) AS rn
            FROM dbo.Aproximacao_Proxima ap
            JOIN alvo t ON t.id_asteroide = ap.id_asteroide
            WHERE ap.datahora_aprox >= @now
        ) x
        WHERE x.rn = 1
    ),
    ca_month_count AS (
        SELECT
            ap.id_asteroide,
            DATEFROMPARTS(YEAR(ap.datahora_aprox), MONTH(ap.datahora_aprox), 1) AS mes,
            SUM(CASE WHEN ap.distancia_ld IS NOT NULL AND ap.distancia_ld < 10 THEN 1 ELSE 0 END) AS n_lt10ld
        FROM dbo.Aproximacao_Proxima ap
        JOIN alvo t ON t.id_asteroide = ap.id_asteroide
        WHERE ap.datahora_aprox >= DATEADD(MONTH, -1, @now) -- janela curta
        GROUP BY ap.id_asteroide, DATEFROMPARTS(YEAR(ap.datahora_aprox), MONTH(ap.datahora_aprox), 1)
    ),
    cond AS (
        SELECT
            f.id_asteroide,

            -- HIGH 1: <1 LD nos próximos 7 dias e diam >10m
            CASE WHEN nc.datahora_aprox <= DATEADD(DAY, 7, @now)
                   AND nc.distancia_ld IS NOT NULL AND nc.distancia_ld < 1
                   AND f.diam_m > 10
                 THEN 1 ELSE 0 END AS c_high_ca,

            -- HIGH 2: PHA >100m, rms>0.8, moid_ld<20 (solução atual)
            CASE WHEN f.flag_pha=1 AND f.diam_m > 100
                   AND sao.rms IS NOT NULL AND sao.rms > 0.8
                   AND sao.moid_ld IS NOT NULL AND sao.moid_ld < 20
                 THEN 1 ELSE 0 END AS c_high_pha_unc,

            -- MED 1: diâmetro >500m, "descoberto no último mês" (se data_descoberta existir), moid_ld<50
            CASE WHEN f.diam_m > 500
                   AND (SELECT a.data_descoberta FROM dbo.Asteroide a WHERE a.id_asteroide=f.id_asteroide) >= DATEADD(MONTH,-1,CAST(@now AS DATE))
                   AND sao.moid_ld IS NOT NULL AND sao.moid_ld < 50
                 THEN 1 ELSE 0 END AS c_med_newbig,

            -- MED 2: mudanças orbitais significativas (Δe>0.05 OU Δi>2º)
            CASE WHEN sp.e IS NOT NULL AND sao.e IS NOT NULL AND ABS(sao.e - sp.e) > 0.05
                   OR  sp.i_deg IS NOT NULL AND sao.i_deg IS NOT NULL AND ABS(sao.i_deg - sp.i_deg) > 2
                 THEN 1 ELSE 0 END AS c_med_orb_change,

            -- LOW 1: >5 aproximações <10 LD no mesmo mês (último mês)
            CASE WHEN EXISTS (
                    SELECT 1 FROM ca_month_count cm
                    WHERE cm.id_asteroide=f.id_asteroide AND cm.n_lt10ld > 5
                 ) THEN 1 ELSE 0 END AS c_low_cluster,

            -- LOW 2: características anómalas: albedo>0.3, e>0.8, i>70°, diam>200m
            CASE WHEN f.albedo IS NOT NULL AND f.albedo > 0.3
                   AND sao.e IS NOT NULL AND sao.e > 0.8
                   AND sao.i_deg IS NOT NULL AND sao.i_deg > 70
                   AND f.diam_m > 200
                 THEN 1 ELSE 0 END AS c_low_anom,

            -- campos de apoio
            nc.id_aprox_prox,
            nc.datahora_aprox,
            nc.distancia_ld,
            sao.id_solucao_orbital,
            sao.moid_ld,
            sao.rms,
            f.diam_m
        FROM fis f
        LEFT JOIN so_atual sao ON sao.id_asteroide = f.id_asteroide
        LEFT JOIN so_prev  sp  ON sp.id_asteroide  = f.id_asteroide
        LEFT JOIN next_ca  nc  ON nc.id_asteroide  = f.id_asteroide
    ),
    candidatos AS (
        -- monta a lista de alertas a existir (1 linha por regra)
        SELECT
            c.id_asteroide,
            'HIGH_CA_1LD_7D_10M' AS codigo_regra,
            (SELECT id_prio_alerta FROM dbo.Prioridade_Alerta WHERE codigo='ALTA') AS id_prio_alerta,
            NULL AS id_nivel_alerta,
            N'Aproximação iminente (<1 LD em 7 dias)' AS titulo,
            CONCAT(N'Próxima aproximação em ', CONVERT(NVARCHAR(30), c.datahora_aprox, 120),
                   N' a ', CONVERT(NVARCHAR(20), c.distancia_ld),
                   N' LD. Diâmetro estimado: ', CONVERT(NVARCHAR(20), c.diam_m), N' m.') AS descricao,
            c.id_aprox_prox AS id_aprox_prox,
            c.id_solucao_orbital AS id_solucao_orbital
        FROM cond c
        WHERE c.c_high_ca = 1

        UNION ALL
        SELECT
            c.id_asteroide,
            'HIGH_PHA_UNCERTAIN' AS codigo_regra,
            (SELECT id_prio_alerta FROM dbo.Prioridade_Alerta WHERE codigo='ALTA') AS id_prio_alerta,
            NULL,
            N'PHA com trajetória incerta' AS titulo,
            CONCAT(N'PHA >100m com RMS=', CONVERT(NVARCHAR(20), c.rms),
                   N' e MOID_LD=', CONVERT(NVARCHAR(20), c.moid_ld), N' (<20).') AS descricao,
            NULL, c.id_solucao_orbital
        FROM cond c
        WHERE c.c_high_pha_unc = 1

        UNION ALL
        SELECT
            c.id_asteroide,
            'MED_NEW_BIG' AS codigo_regra,
            (SELECT id_prio_alerta FROM dbo.Prioridade_Alerta WHERE codigo='MEDIA') AS id_prio_alerta,
            NULL,
            N'Novo asteroide de grande porte' AS titulo,
            N'Diâmetro >500m, descoberto no último mês e MOID_LD<50.' AS descricao,
            NULL, c.id_solucao_orbital
        FROM cond c
        WHERE c.c_med_newbig = 1

        UNION ALL
        SELECT
            c.id_asteroide,
            'MED_ORBIT_CHANGE' AS codigo_regra,
            (SELECT id_prio_alerta FROM dbo.Prioridade_Alerta WHERE codigo='MEDIA') AS id_prio_alerta,
            NULL,
            N'Mudança orbital significativa' AS titulo,
            N'Variação significativa na excentricidade ou inclinação face à solução anterior.' AS descricao,
            NULL, c.id_solucao_orbital
        FROM cond c
        WHERE c.c_med_orb_change = 1

        UNION ALL
        SELECT
            c.id_asteroide,
            'LOW_CLUSTER_CA' AS codigo_regra,
            (SELECT id_prio_alerta FROM dbo.Prioridade_Alerta WHERE codigo='BAIXA') AS id_prio_alerta,
            NULL,
            N'Agrupamento temporal de aproximações' AS titulo,
            N'>5 aproximações <10 LD no mesmo mês (janela recente).' AS descricao,
            NULL, c.id_solucao_orbital
        FROM cond c
        WHERE c.c_low_cluster = 1

        UNION ALL
        SELECT
            c.id_asteroide,
            'LOW_ANOMALY' AS codigo_regra,
            (SELECT id_prio_alerta FROM dbo.Prioridade_Alerta WHERE codigo='BAIXA') AS id_prio_alerta,
            NULL,
            N'Características anómalas' AS titulo,
            N'Albedo>0.3, e>0.8, i>70° e diâmetro>200m.' AS descricao,
            NULL, c.id_solucao_orbital
        FROM cond c
        WHERE c.c_low_anom = 1
    ),
    classificados AS (
        -- aplica Nível Torino modificado ao alerta (quando possível)
        SELECT
            cand.*,
            CASE
                WHEN cand.codigo_regra LIKE 'HIGH_CA_%' THEN
                    (SELECT TOP 1 id_nivel_alerta FROM dbo.Nivel_Alerta WHERE codigo='N4')
                WHEN cand.codigo_regra='HIGH_PHA_UNCERTAIN' THEN
                    (SELECT TOP 1 id_nivel_alerta FROM dbo.Nivel_Alerta WHERE codigo='N3')
                ELSE NULL
            END AS id_nivel_calculado
        FROM candidatos cand
    )
    -- 1) INSERIR novos alertas que ainda não existem ativos
    INSERT INTO dbo.Alerta
        (id_asteroide, id_aprox_prox, id_solucao_orbital, id_prio_alerta, id_nivel_alerta, codigo_regra, titulo, descricao)
    SELECT
        c.id_asteroide, c.id_aprox_prox, c.id_solucao_orbital, c.id_prio_alerta,
        COALESCE(c.id_nivel_calculado, c.id_nivel_alerta),
        c.codigo_regra, c.titulo, c.descricao
    FROM classificados c
    WHERE NOT EXISTS (
        SELECT 1
        FROM dbo.Alerta al
        WHERE al.id_asteroide = c.id_asteroide
          AND al.codigo_regra = c.codigo_regra
          AND al.ativo = 1
    );

    -- 2) ENCERRAR alertas ativos que já não se aplicam
    UPDATE al
    SET al.ativo = 0,
        al.datahora_encerramento = @now
    FROM dbo.Alerta al
    JOIN alvo t ON t.id_asteroide = al.id_asteroide
    WHERE al.ativo = 1
      AND NOT EXISTS (
          SELECT 1 FROM classificados c
          WHERE c.id_asteroide = al.id_asteroide
            AND c.codigo_regra = al.codigo_regra
      );
END
GO

------------------------------------------------------------
-- TRIGGER 1: Garantir uma única solução atual por asteroide
------------------------------------------------------------
IF OBJECT_ID('dbo.TRG_SolucaoOrbital_UnicaAtual','TR') IS NOT NULL
    DROP TRIGGER dbo.TRG_SolucaoOrbital_UnicaAtual;
GO
CREATE TRIGGER dbo.TRG_SolucaoOrbital_UnicaAtual
ON dbo.Solucao_Orbital
AFTER INSERT, UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    IF EXISTS (SELECT 1 FROM inserted WHERE solucao_atual = 1)
    BEGIN
        UPDATE so
        SET so.solucao_atual = 0
        FROM dbo.Solucao_Orbital so
        JOIN inserted i ON i.id_asteroide = so.id_asteroide
        WHERE so.id_solucao_orbital <> i.id_solucao_orbital
          AND i.solucao_atual = 1;
    END
END
GO

------------------------------------------------------------
-- TRIGGER 2: Marcar crítica em Aproximacao_Proxima (condição alta prioridade 1)
------------------------------------------------------------
IF OBJECT_ID('dbo.TRG_Aproximacao_MarcaCritica','TR') IS NOT NULL
    DROP TRIGGER dbo.TRG_Aproximacao_MarcaCritica;
GO
CREATE TRIGGER dbo.TRG_Aproximacao_MarcaCritica
ON dbo.Aproximacao_Proxima
AFTER INSERT, UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @now DATETIME2(0) = SYSUTCDATETIME();

    UPDATE ap
    SET ap.critica = 1
    FROM dbo.Aproximacao_Proxima ap
    JOIN inserted i ON i.id_aprox_prox = ap.id_aprox_prox
    JOIN dbo.Asteroide a ON a.id_asteroide = ap.id_asteroide
    WHERE ap.datahora_aprox >= @now
      AND ap.datahora_aprox <= DATEADD(DAY, 7, @now)
      AND ap.distancia_ld IS NOT NULL AND ap.distancia_ld < 1
      AND COALESCE(
            a.diametro_km,
            1329.0 * POWER(10.0, -a.h_mag/5.0) / SQRT(COALESCE(a.albedo, 0.14))
          ) * 1000.0 > 10;
END
GO

------------------------------------------------------------
-- TRIGGER 3: Reavaliar alertas quando entram novas aproximações/soluções
------------------------------------------------------------
IF OBJECT_ID('dbo.TRG_Aproximacao_ReavaliarAlertas','TR') IS NOT NULL
    DROP TRIGGER dbo.TRG_Aproximacao_ReavaliarAlertas;
GO
CREATE TRIGGER dbo.TRG_Aproximacao_ReavaliarAlertas
ON dbo.Aproximacao_Proxima
AFTER INSERT, UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @ids dbo.IntList;
    INSERT INTO @ids(id)
    SELECT DISTINCT id_asteroide FROM inserted WHERE id_asteroide IS NOT NULL;

    EXEC dbo.sp_ReavaliarAlertas @Asteroides=@ids;
END
GO

IF OBJECT_ID('dbo.TRG_Solucao_ReavaliarAlertas','TR') IS NOT NULL
    DROP TRIGGER dbo.TRG_Solucao_ReavaliarAlertas;
GO
CREATE TRIGGER dbo.TRG_Solucao_ReavaliarAlertas
ON dbo.Solucao_Orbital
AFTER INSERT, UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @ids dbo.IntList;
    INSERT INTO @ids(id)
    SELECT DISTINCT id_asteroide FROM inserted WHERE id_asteroide IS NOT NULL;

    EXEC dbo.sp_ReavaliarAlertas @Asteroides=@ids;
END
GO
