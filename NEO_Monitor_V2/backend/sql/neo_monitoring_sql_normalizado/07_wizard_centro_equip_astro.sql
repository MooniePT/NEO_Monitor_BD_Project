------------------------------------------------------------
-- 07_wizard_centro_equip_astro.sql
-- Objetivo:
--   1) Importar CENTROS (stg.centro_observacoes) para dbo.Centro_Observacao
--   2) Importar EQUIPAMENTO (stg.equipamento) para dbo.Equipamento, ligando ao Centro por codigo
--   3) (Opcional) Inserir Astrónomos mínimos/placeholder (podes importar tu mais tarde)
------------------------------------------------------------
USE [BD_PL2_09];
GO
SET NOCOUNT ON;
SET XACT_ABORT ON;
GO

BEGIN TRY
    BEGIN TRAN;

    ------------------------------------------------------------
    -- 1) CENTROS
    ------------------------------------------------------------
    IF EXISTS (SELECT 1 FROM stg.centro_observacoes)
    BEGIN
        ;WITH src AS (
            SELECT DISTINCT
                NULLIF(LTRIM(RTRIM(codigo)), '') AS codigo,
                NULLIF(LTRIM(RTRIM(nome)), '') AS nome,
                NULLIF(LTRIM(RTRIM(pais)), '') AS pais,
                NULLIF(LTRIM(RTRIM(cidade)), '') AS cidade,
                TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(latitude)),''),'nan')) AS latitude_graus,
                TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(longitude)),''),'nan')) AS longitude_graus,
                TRY_CONVERT(INT, NULLIF(NULLIF(LTRIM(RTRIM(altitude_m)),''),'nan')) AS altitude_m
            FROM stg.centro_observacoes
            WHERE NULLIF(LTRIM(RTRIM(codigo)), '') IS NOT NULL
        )
        MERGE dbo.Centro_Observacao AS t
        USING src AS s
          ON t.codigo = s.codigo
        WHEN MATCHED THEN
          UPDATE SET
            t.nome = COALESCE(t.nome, s.nome),
            t.pais = COALESCE(t.pais, s.pais),
            t.cidade = COALESCE(t.cidade, s.cidade),
            t.latitude_graus = COALESCE(t.latitude_graus, s.latitude_graus),
            t.longitude_graus = COALESCE(t.longitude_graus, s.longitude_graus),
            t.altitude_m = COALESCE(t.altitude_m, s.altitude_m)
        WHEN NOT MATCHED THEN
          INSERT (codigo, nome, pais, cidade, latitude_graus, longitude_graus, altitude_m)
          VALUES (s.codigo, COALESCE(s.nome, s.codigo), s.pais, s.cidade, s.latitude_graus, s.longitude_graus, s.altitude_m);

        INSERT INTO dbo.Import_Log(fonte, descricao, linhas_afetadas)
        VALUES ('OBS', N'Upsert Centro_Observacao', @@ROWCOUNT);
    END

    ------------------------------------------------------------
    -- 2) EQUIPAMENTO
    -- O CSV equipamento tem id_centro (numérico) e não tem codigo; por isso fazemos:
    --  - stg.equipamento.id_centro → join com stg.centro_observacoes.id_centro → obtém codigo
    --  - codigo → join com dbo.Centro_Observacao → id_centro real
    ------------------------------------------------------------
    IF EXISTS (SELECT 1 FROM stg.equipamento)
    BEGIN
        ;WITH eq AS (
            SELECT
                e.*,
                c.codigo AS centro_codigo
            FROM stg.equipamento e
            LEFT JOIN stg.centro_observacoes c
              ON NULLIF(LTRIM(RTRIM(e.id_centro)), '') = NULLIF(LTRIM(RTRIM(c.id_centro)), '')
        ),
        src AS (
            SELECT
                co.id_centro,
                NULLIF(LTRIM(RTRIM(eq.nome)), '') AS nome,
                NULLIF(LTRIM(RTRIM(eq.tipo)), '') AS tipo,
                NULLIF(LTRIM(RTRIM(eq.modelo)), '') AS modelo,
                TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(eq.abertura_m)),''),'nan')) AS abertura_m,
                TRY_CONVERT(FLOAT, NULLIF(NULLIF(LTRIM(RTRIM(eq.distancia_focal_m)),''),'nan')) AS distancia_focal_m,
                NULLIF(LTRIM(RTRIM(eq.notas)), '') AS notas
            FROM eq
            JOIN dbo.Centro_Observacao co
              ON co.codigo = eq.centro_codigo
            WHERE NULLIF(LTRIM(RTRIM(eq.nome)), '') IS NOT NULL
        )
        -- Inserir se ainda não existir (por centro+nome+modelo)
        INSERT INTO dbo.Equipamento (id_centro, nome, tipo, modelo, abertura_m, distancia_focal_m, notas)
        SELECT s.id_centro, s.nome, s.tipo, s.modelo, s.abertura_m, s.distancia_focal_m, s.notas
        FROM src s
        WHERE NOT EXISTS (
            SELECT 1
            FROM dbo.Equipamento e
            WHERE e.id_centro = s.id_centro
              AND e.nome = s.nome
              AND ISNULL(e.modelo,'') = ISNULL(s.modelo,'')
        );

        INSERT INTO dbo.Import_Log(fonte, descricao, linhas_afetadas)
        VALUES ('OBS', N'Insert Equipamento', @@ROWCOUNT);
    END

    ------------------------------------------------------------
    -- 3) ASTRÓNOMOS (placeholder opcional)
    ------------------------------------------------------------
    IF NOT EXISTS (SELECT 1 FROM dbo.Astronomo)
    BEGIN
        INSERT INTO dbo.Astronomo (id_centro, nome_completo, email, funcao)
        SELECT TOP (1) c.id_centro, N'Astrónomo Desconhecido', NULL, N'Operador'
        FROM dbo.Centro_Observacao c
        ORDER BY c.id_centro;

        INSERT INTO dbo.Import_Log(fonte, descricao, linhas_afetadas)
        VALUES ('OBS', N'Insert Astronomo (placeholder)', @@ROWCOUNT);
    END

    COMMIT;
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0 ROLLBACK;
    THROW;
END CATCH;
GO
