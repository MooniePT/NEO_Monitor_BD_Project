------------------------------------------------------------
-- 05_link_esa_to_core.sql
-- Objetivo:
--   1) Carregar CSVs ESA (stg.*) para tabelas ESA (core)
--   2) Ligar id_asteroide por matching (Asteroide.ast_key = ESA.designation_key)
--   3) Converter ESA_UpcomingCloseApproaches em Aproximacao_Proxima (eventos)
------------------------------------------------------------
USE [BD_PL2_09];
GO
SET NOCOUNT ON;
SET XACT_ABORT ON;
GO

BEGIN TRY
    BEGIN TRAN;

    ------------------------------------------------------------
    -- 1) LOAD ESA_RiskList
    ------------------------------------------------------------
    IF EXISTS (SELECT 1 FROM stg.esa_risklist)
    BEGIN
        TRUNCATE TABLE dbo.ESA_RiskList;

        INSERT INTO dbo.ESA_RiskList
        (
            num_lista, object_designation, diameter_m, impact_datetime_utc,
            ip_max, ps_max, ts, years, ip_cum, ps_cum, vel_kms, in_list_since_days
        )
        SELECT
            TRY_CONVERT(INT, NULLIF(LTRIM(RTRIM(no_)),'')),
            NULLIF(LTRIM(RTRIM(object_designation)),''),
            TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(diameter_in_m)),''),'nan')),
            TRY_CONVERT(DATETIME2(0), NULLIF(LTRIM(RTRIM(impact_datetime_utc)),'')),
            TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(ip_max)),''),'nan')),
            TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(ps_max)),''),'nan')),
            TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(ts)),''),'nan')),
            TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(years)),''),'nan')),
            TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(ip_cum)),''),'nan')),
            TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(ps_cum)),''),'nan')),
            TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(vel_kms)),''),'nan')),
            TRY_CONVERT(INT, NULLIF(NULLIF(LTRIM(RTRIM(in_list_since_days)),''),'nan'))
        FROM stg.esa_risklist
        WHERE NULLIF(LTRIM(RTRIM(object_designation)), '') IS NOT NULL;

        INSERT INTO dbo.Import_Log(fonte, descricao, linhas_afetadas)
        VALUES ('ESA', N'Load ESA_RiskList', @@ROWCOUNT);
    END

    ------------------------------------------------------------
    -- 2) LOAD ESA_SpecialRiskList
    ------------------------------------------------------------
    IF EXISTS (SELECT 1 FROM stg.esa_specialrisklist)
    BEGIN
        TRUNCATE TABLE dbo.ESA_SpecialRiskList;

        INSERT INTO dbo.ESA_SpecialRiskList
        (
            num_lista, object_designation, diameter_m, impact_datetime_utc,
            ip_max, ps_max, vel_kms, in_list_since_days, comment
        )
        SELECT
            TRY_CONVERT(INT, NULLIF(LTRIM(RTRIM(no_)),'')),
            NULLIF(LTRIM(RTRIM(object_designation)),''),
            TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(diameter_in_m)),''),'nan')),
            TRY_CONVERT(DATETIME2(0), NULLIF(LTRIM(RTRIM(impact_datetime_utc)),'')),
            TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(ip_max)),''),'nan')),
            TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(ps_max)),''),'nan')),
            TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(vel_kms)),''),'nan')),
            TRY_CONVERT(INT, NULLIF(NULLIF(LTRIM(RTRIM(in_list_since_days)),''),'nan')),
            NULLIF(LTRIM(RTRIM(comment)), '')
        FROM stg.esa_specialrisklist
        WHERE NULLIF(LTRIM(RTRIM(object_designation)), '') IS NOT NULL;

        INSERT INTO dbo.Import_Log(fonte, descricao, linhas_afetadas)
        VALUES ('ESA', N'Load ESA_SpecialRiskList', @@ROWCOUNT);
    END

    ------------------------------------------------------------
    -- 3) LOAD ESA_RemovedFromRiskList
    ------------------------------------------------------------
    IF EXISTS (SELECT 1 FROM stg.esa_removedrisk)
    BEGIN
        TRUNCATE TABLE dbo.ESA_RemovedFromRiskList;

        INSERT INTO dbo.ESA_RemovedFromRiskList
        (
            object_designation, removal_date_utc, vi_date_utc, last_ip, last_ps
        )
        SELECT
            NULLIF(LTRIM(RTRIM(object_designation)),''),
            TRY_CONVERT(DATETIME2(0), NULLIF(LTRIM(RTRIM(removal_date_utc)),'')),
            TRY_CONVERT(DATETIME2(0), NULLIF(LTRIM(RTRIM(vi_date_utc)),'')),
            TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(last_ip)),''),'nan')),
            TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(last_ps)),''),'nan'))
        FROM stg.esa_removedrisk
        WHERE NULLIF(LTRIM(RTRIM(object_designation)), '') IS NOT NULL;

        INSERT INTO dbo.Import_Log(fonte, descricao, linhas_afetadas)
        VALUES ('ESA', N'Load ESA_RemovedFromRiskList', @@ROWCOUNT);
    END

    ------------------------------------------------------------
    -- 4) LOAD ESA_PastImpactors
    ------------------------------------------------------------
    IF EXISTS (SELECT 1 FROM stg.esa_pastimpactors)
    BEGIN
        TRUNCATE TABLE dbo.ESA_PastImpactors;

        INSERT INTO dbo.ESA_PastImpactors
        (
            num_lista, object_designation, diameter_m, impact_datetime_utc,
            impact_velocity_kms, impact_fpa_deg, impact_azimuth_deg,
            estimated_energy_kt, estimated_energy_other_kt
        )
        SELECT
            TRY_CONVERT(INT, NULLIF(LTRIM(RTRIM(no_)),'')),
            NULLIF(LTRIM(RTRIM(object_designation)),''),
            TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(diameter_in_m)),''),'nan')),
            TRY_CONVERT(DATETIME2(0), NULLIF(LTRIM(RTRIM(impact_datetime_utc)),'')),
            TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(impact_velocity_kms)),''),'nan')),
            TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(impact_fpa_deg)),''),'nan')),
            TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(impact_azimuth_deg)),''),'nan')),
            TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(estimated_energy_kt)),''),'nan')),
            TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(estimated_energy_other_kt)),''),'nan'))
        FROM stg.esa_pastimpactors
        WHERE NULLIF(LTRIM(RTRIM(object_designation)), '') IS NOT NULL;

        INSERT INTO dbo.Import_Log(fonte, descricao, linhas_afetadas)
        VALUES ('ESA', N'Load ESA_PastImpactors', @@ROWCOUNT);
    END

    ------------------------------------------------------------
    -- 5) LOAD ESA_UpcomingCloseApproaches
    ------------------------------------------------------------
    IF EXISTS (SELECT 1 FROM stg.esa_upcomingclapp)
    BEGIN
        TRUNCATE TABLE dbo.ESA_UpcomingCloseApproaches;

        INSERT INTO dbo.ESA_UpcomingCloseApproaches
        (
            object_designation, close_approach_date_utc,
            miss_distance_km, miss_distance_au, miss_distance_ld,
            diameter_m, h_mag, max_brightness_mag, relative_velocity_kms, cai_index
        )
        SELECT
            NULLIF(LTRIM(RTRIM(object_designation)),''),
            TRY_CONVERT(DATETIME2(0), NULLIF(LTRIM(RTRIM(close_approach_date_utc)),'')),
            TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(miss_distance_km)),''),'nan')),
            TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(miss_distance_au)),''),'nan')),
            TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(miss_distance_ld)),''),'nan')),
            TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(diameter_in_m)),''),'nan')),
            TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(h_mag)),''),'nan')),
            TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(max_brightness_mag)),''),'nan')),
            TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(relative_velocity_kms)),''),'nan')),
            TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(cai_index)),''),'nan'))
        FROM stg.esa_upcomingclapp
        WHERE NULLIF(LTRIM(RTRIM(object_designation)), '') IS NOT NULL;

        INSERT INTO dbo.Import_Log(fonte, descricao, linhas_afetadas)
        VALUES ('ESA', N'Load ESA_UpcomingCloseApproaches', @@ROWCOUNT);
    END

    ------------------------------------------------------------
    -- 6) LOAD ESA_SearchResult
    ------------------------------------------------------------
    IF EXISTS (SELECT 1 FROM stg.esa_searchresult)
    BEGIN
        TRUNCATE TABLE dbo.ESA_SearchResult;

        INSERT INTO dbo.ESA_SearchResult (object_designation)
        SELECT NULLIF(LTRIM(RTRIM(object_designation)), '')
        FROM stg.esa_searchresult
        WHERE NULLIF(LTRIM(RTRIM(object_designation)), '') IS NOT NULL;

        INSERT INTO dbo.Import_Log(fonte, descricao, linhas_afetadas)
        VALUES ('ESA', N'Load ESA_SearchResult', @@ROWCOUNT);
    END

    ------------------------------------------------------------
    -- 7) LINK id_asteroide nas tabelas ESA via (Asteroide.ast_key)
    ------------------------------------------------------------
    UPDATE e
    SET e.id_asteroide = a.id_asteroide
    FROM dbo.ESA_RiskList e
    JOIN dbo.Asteroide a ON a.ast_key = e.designation_key
    WHERE e.id_asteroide IS NULL;

    UPDATE e
    SET e.id_asteroide = a.id_asteroide
    FROM dbo.ESA_SpecialRiskList e
    JOIN dbo.Asteroide a ON a.ast_key = e.designation_key
    WHERE e.id_asteroide IS NULL;

    UPDATE e
    SET e.id_asteroide = a.id_asteroide
    FROM dbo.ESA_RemovedFromRiskList e
    JOIN dbo.Asteroide a ON a.ast_key = e.designation_key
    WHERE e.id_asteroide IS NULL;

    UPDATE e
    SET e.id_asteroide = a.id_asteroide
    FROM dbo.ESA_PastImpactors e
    JOIN dbo.Asteroide a ON a.ast_key = e.designation_key
    WHERE e.id_asteroide IS NULL;

    UPDATE e
    SET e.id_asteroide = a.id_asteroide
    FROM dbo.ESA_UpcomingCloseApproaches e
    JOIN dbo.Asteroide a ON a.ast_key = e.designation_key
    WHERE e.id_asteroide IS NULL;

    UPDATE e
    SET e.id_asteroide = a.id_asteroide
    FROM dbo.ESA_SearchResult e
    JOIN dbo.Asteroide a ON a.ast_key = e.designation_key
    WHERE e.id_asteroide IS NULL;

    INSERT INTO dbo.Import_Log(fonte, descricao, linhas_afetadas)
    VALUES ('ESA', N'Link ESA→Asteroide (id_asteroide)', @@ROWCOUNT);

    ------------------------------------------------------------
    -- 8) Converter upcoming close approaches → Aproximacao_Proxima
    ------------------------------------------------------------
    INSERT INTO dbo.Aproximacao_Proxima
        (id_asteroide, datahora_aprox, distancia_ua, distancia_ld, veloc_relativa_kms, origem, critica)
    SELECT
        e.id_asteroide,
        e.close_approach_date_utc,
        e.miss_distance_au,
        e.miss_distance_ld,
        e.relative_velocity_kms,
        'ESA' AS origem,
        0
    FROM dbo.ESA_UpcomingCloseApproaches e
    WHERE e.id_asteroide IS NOT NULL
      AND e.close_approach_date_utc IS NOT NULL
      AND NOT EXISTS (
          SELECT 1
          FROM dbo.Aproximacao_Proxima ap
          WHERE ap.id_asteroide = e.id_asteroide
            AND ap.datahora_aprox = e.close_approach_date_utc
      );

    INSERT INTO dbo.Import_Log(fonte, descricao, linhas_afetadas)
    VALUES ('ESA', N'Insert Aproximacao_Proxima (from ESA Upcoming)', @@ROWCOUNT);

    COMMIT;
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0 ROLLBACK;
    THROW;
END CATCH;
GO
