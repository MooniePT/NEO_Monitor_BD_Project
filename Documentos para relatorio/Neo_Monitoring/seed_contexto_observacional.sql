/* ============================================================
   NEO_Monitoring — Seed do Contexto Observacional
   Tabelas: Astronomo, Equipamento, Software, Centro_Observacao

   - Script pensado para SQL Server
   - Evita duplicados usando NOT EXISTS (chave natural)
   - Ajusta nomes de schema/tabelas/colunas se os teus diferirem

   Ordem: Astronomo -> Equipamento -> Software -> Centro_Observacao
   ============================================================ */

SET NOCOUNT ON;

BEGIN TRY
    BEGIN TRAN;

    /* -------------------------
       1) ASTRONOMO
       Chave natural usada: email
       ------------------------- */
    ;WITH src AS (
        SELECT N'Ana Ribeiro'      AS nome_completo, N'+351 912345678' AS telefone, N'Observadora / Follow-up' AS funcao, N'ana.ribeiro@neo.local'      AS email UNION ALL
        SELECT N'Miguel Santos',   N'+351 934567890', N'Dinâmica / Órbitas',        N'miguel.santos@neo.local'   UNION ALL
        SELECT N'Beatriz Costa',   N'+351 966778899', N'Instrumentação',            N'beatriz.costa@neo.local'    UNION ALL
        SELECT N'João Ferreira',   N'+351 919876543', N'Pipeline / Software',       N'joao.ferreira@neo.local'    UNION ALL
        SELECT N'Sofia Almeida',   N'+351 968112233', N'Observação (fotometria)',   N'sofia.almeida@neo.local'    UNION ALL
        SELECT N'Tiago Pereira',   N'+351 932221111', N'Astrometria',               N'tiago.pereira@neo.local'    UNION ALL
        SELECT N'Inês Martins',    N'+351 965551212', N'Gestão de dados',           N'ines.martins@neo.local'     UNION ALL
        SELECT N'Rui Oliveira',    N'+351 931234567', N'Coordenação do centro',     N'rui.oliveira@neo.local'     UNION ALL
        SELECT N'Carla Silva',     N'+351 962222333', N'Observação (imaging)',      N'carla.silva@neo.local'      UNION ALL
        SELECT N'Pedro Gomes',     N'+351 963333444', N'Análise / QA',              N'pedro.gomes@neo.local'      UNION ALL
        SELECT N'Helena Duarte',   N'+351 964444555', N'Planeamento observacional', N'helena.duarte@neo.local'    UNION ALL
        SELECT N'Nuno Carvalho',   N'+351 965555666', N'Operador',                  N'nuno.carvalho@neo.local'
    )
    INSERT INTO dbo.Astronomo (nome_completo, telefone, funcao, email)
    SELECT s.nome_completo, s.telefone, s.funcao, s.email
    FROM src s
    WHERE NOT EXISTS (
        SELECT 1 FROM dbo.Astronomo a WHERE a.email = s.email
    );

    /* -------------------------
       2) EQUIPAMENTO
       Chave natural usada: nome
       Nota: se o teu campo [tipo] for FK numérica, troca estes valores
             (ou diz-me o nome da tabela de tipos para eu adaptar o script).
       ------------------------- */
    ;WITH src AS (
        SELECT N'RC Follow-up 0.6m'          AS nome, N'RC-600'      AS modelo, N'Telescópio' AS tipo, 0.60 AS abertura_m, 4.80 AS distancia_focal_m, N'Follow-up astrométrico (campo moderado)' AS notas UNION ALL
        SELECT N'Schmidt Survey 1.0m'        AS nome, N'SCH-1000'    AS modelo, N'Telescópio' AS tipo, 1.00 AS abertura_m, 3.00 AS distancia_focal_m, N'Campo largo para survey' UNION ALL
        SELECT N'Reflector 1.5m'             AS nome, N'REF-1500'    AS modelo, N'Telescópio' AS tipo, 1.50 AS abertura_m, 12.0 AS distancia_focal_m, N'Follow-up e fotometria' UNION ALL
        SELECT N'Telescope 2.0m Fast'        AS nome, N'FAST-2000'   AS modelo, N'Telescópio' AS tipo, 2.00 AS abertura_m, 8.00 AS distancia_focal_m, N'Follow-up rápido em janelas curtas' UNION ALL
        SELECT N'Small Survey 0.25m'         AS nome, N'SUR-250'     AS modelo, N'Telescópio' AS tipo, 0.25 AS abertura_m, 1.00 AS distancia_focal_m, N'Station de treino / testes' UNION ALL
        SELECT N'Wide-field Camera Rig'      AS nome, N'WFC-01'      AS modelo, N'Câmara'     AS tipo, NULL AS abertura_m, NULL AS distancia_focal_m, N'Conjunto de câmaras para campos largos' UNION ALL
        SELECT N'Spectrograph Module'        AS nome, N'SPEC-02'     AS modelo, N'Espectrógrafo' AS tipo, NULL AS abertura_m, NULL AS distancia_focal_m, N'Caracterização espectral' UNION ALL
        SELECT N'DSN Radar 70m'              AS nome, N'DSS-14'      AS modelo, N'Radar'      AS tipo, 70.0 AS abertura_m, NULL AS distancia_focal_m, N'Caracterização por radar (quando aplicável)'
    )
    INSERT INTO dbo.Equipamento (nome, modelo, tipo, abertura_m, distancia_focal_m, notas)
    SELECT s.nome, s.modelo, s.tipo, s.abertura_m, s.distancia_focal_m, s.notas
    FROM src s
    WHERE NOT EXISTS (
        SELECT 1 FROM dbo.Equipamento e WHERE e.nome = s.nome
    );

    /* -------------------------
       3) SOFTWARE
       Chave natural usada: (nome, versao)
       ------------------------- */
    ;WITH src AS (
        SELECT N'Astrometrica'              AS nome, N'4.12' AS versao, N'Herbert Raab'        AS fornecedor, N'Commercial'      AS tipo_licenca, N'https://www.astrometrica.at/'          AS website UNION ALL
        SELECT N'Tycho Tracker'             AS nome, N'2.3'  AS versao, N'Tycho Tracker'       AS fornecedor, N'Freemium'        AS tipo_licenca, N'https://tycho-tracker.com/'             UNION ALL
        SELECT N'SExtractor'                AS nome, N'2.28' AS versao, N'CEA / TERAPIX'       AS fornecedor, N'GPL'             AS tipo_licenca, N'https://sextractor.readthedocs.io/'      UNION ALL
        SELECT N'IRAF'                      AS nome, N'2.16' AS versao, N'NOIRLab / Community' AS fornecedor, N'Open Source'     AS tipo_licenca, N'https://iraf-community.github.io/'       UNION ALL
        SELECT N'NEO_Monitoring Pipeline'   AS nome, N'0.1'  AS versao, N'UBI'                 AS fornecedor, N'Internal'        AS tipo_licenca, N'https://example.invalid/neo-monitoring'  UNION ALL
        SELECT N'Python (Astropy stack)'    AS nome, N'2025.0' AS versao, N'Community'         AS fornecedor, N'BSD/MIT'         AS tipo_licenca, N'https://www.astropy.org/'                UNION ALL
        SELECT N'OpenCV'                    AS nome, N'4.10' AS versao, N'OpenCV'              AS fornecedor, N'Apache-2.0'      AS tipo_licenca, N'https://opencv.org/'                      UNION ALL
        SELECT N'MPC Tools (Export/Submit)' AS nome, N'1.0'  AS versao, N'MPC / Community'     AS fornecedor, N'Varies'          AS tipo_licenca, N'https://minorplanetcenter.net/'
    )
    INSERT INTO dbo.Software (nome, versao, fornecedor, tipo_licenca, website)
    SELECT s.nome, s.versao, s.fornecedor, s.tipo_licenca, s.website
    FROM src s
    WHERE NOT EXISTS (
        SELECT 1 FROM dbo.Software sw WHERE sw.nome = s.nome AND sw.versao = s.versao
    );

    /* -------------------------
       4) CENTRO_OBSERVACAO
       Chave natural usada: codigo
       FKs: id_equipamento (por nome do equipamento), id_astronomo (por email)
       ------------------------- */
    ;WITH src AS (
        SELECT N'PT-UBI'    AS codigo, N'Centro Observacional UBI (Covilhã)' AS nome, N'Portugal' AS pais, N'Covilhã' AS cidade,
               40.280 AS latitude_graus, -7.505 AS longitude_graus, 700 AS altitude_m,
               N'RC Follow-up 0.6m' AS equipamento_nome, N'ana.ribeiro@neo.local' AS astronomo_email UNION ALL

        SELECT N'ES-CALAR'  AS codigo, N'Observatório Calar Alto (seed)'     AS nome, N'Espanha'  AS pais, N'Almería' AS cidade,
               37.220 AS latitude_graus, -2.546 AS longitude_graus, 2168 AS altitude_m,
               N'Schmidt Survey 1.0m' AS equipamento_nome, N'miguel.santos@neo.local' AS astronomo_email UNION ALL

        SELECT N'US-KITT'   AS codigo, N'Kitt Peak Station (seed)'          AS nome, N'EUA'      AS pais, N'Arizona' AS cidade,
               31.958 AS latitude_graus, -111.598 AS longitude_graus, 2096 AS altitude_m,
               N'Reflector 1.5m' AS equipamento_nome, N'tiago.pereira@neo.local' AS astronomo_email UNION ALL

        SELECT N'CL-CTIO'   AS codigo, N'CTIO (seed)'                       AS nome, N'Chile'    AS pais, N'Coquimbo' AS cidade,
               -30.169 AS latitude_graus, -70.806 AS longitude_graus, 2200 AS altitude_m,
               N'Telescope 2.0m Fast' AS equipamento_nome, N'sofia.almeida@neo.local' AS astronomo_email UNION ALL

        SELECT N'CL-PAR'    AS codigo, N'Paranal (seed)'                    AS nome, N'Chile'    AS pais, N'Antofagasta' AS cidade,
               -24.627 AS latitude_graus, -70.404 AS longitude_graus, 2635 AS altitude_m,
               N'Telescope 2.0m Fast' AS equipamento_nome, N'helena.duarte@neo.local' AS astronomo_email UNION ALL

        SELECT N'HI-MKEA'   AS codigo, N'Mauna Kea (seed)'                  AS nome, N'EUA'      AS pais, N'Hawai‘i' AS cidade,
               19.820 AS latitude_graus, -155.468 AS longitude_graus, 4205 AS altitude_m,
               N'Reflector 1.5m' AS equipamento_nome, N'beatriz.costa@neo.local' AS astronomo_email UNION ALL

        SELECT N'AU-SSO'    AS codigo, N'Siding Spring (seed)'              AS nome, N'Austrália' AS pais, N'NSW' AS cidade,
               -31.273 AS latitude_graus, 149.071 AS longitude_graus, 1165 AS altitude_m,
               N'Small Survey 0.25m' AS equipamento_nome, N'carla.silva@neo.local' AS astronomo_email UNION ALL

        SELECT N'ZA-SUTH'   AS codigo, N'Sutherland (seed)'                 AS nome, N'África do Sul' AS pais, N'Northern Cape' AS cidade,
               -32.379 AS latitude_graus, 20.811 AS longitude_graus, 1798 AS altitude_m,
               N'Reflector 1.5m' AS equipamento_nome, N'pedro.gomes@neo.local' AS astronomo_email UNION ALL

        SELECT N'IT-ASIAGO' AS codigo, N'Asiago (seed)'                     AS nome, N'Itália'   AS pais, N'Vicenza' AS cidade,
               45.843 AS latitude_graus, 11.574 AS longitude_graus, 1366 AS altitude_m,
               N'RC Follow-up 0.6m' AS equipamento_nome, N'ines.martins@neo.local' AS astronomo_email UNION ALL

        SELECT N'US-DSN'    AS codigo, N'DSN Goldstone (seed)'              AS nome, N'EUA'      AS pais, N'Califórnia' AS cidade,
               35.247 AS latitude_graus, -116.793 AS longitude_graus, 1000 AS altitude_m,
               N'DSN Radar 70m' AS equipamento_nome, N'joao.ferreira@neo.local' AS astronomo_email
    )
    INSERT INTO dbo.Centro_Observacao (codigo, nome, pais, cidade, latitude_graus, longitude_graus, altitude_m, id_equipamento, id_astronomo)
    SELECT
        s.codigo, s.nome, s.pais, s.cidade, s.latitude_graus, s.longitude_graus, s.altitude_m,
        e.id_equipamento,
        a.id_astronomo
    FROM src s
    INNER JOIN dbo.Equipamento e ON e.nome = s.equipamento_nome
    INNER JOIN dbo.Astronomo a   ON a.email = s.astronomo_email
    WHERE NOT EXISTS (
        SELECT 1 FROM dbo.Centro_Observacao c WHERE c.codigo = s.codigo
    );

    COMMIT;

    PRINT 'Seed concluído com sucesso (Astronomo, Equipamento, Software, Centro_Observacao).';

END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0 ROLLBACK;
    DECLARE @msg NVARCHAR(4000) = ERROR_MESSAGE();
    RAISERROR('Falhou o seed do contexto observacional: %s', 16, 1, @msg);
END CATCH;
