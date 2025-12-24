USE BD_PL2_09;
GO
SET NOCOUNT ON;
SET XACT_ABORT ON;
GO

BEGIN TRY
    BEGIN TRAN;

    ----------------------------------------------------------------------
    -- 1) CENTROS (centro_de_observacoes.csv)
    ----------------------------------------------------------------------
    INSERT INTO dbo.Centro_Observacao (codigo, nome, pais, cidade, latitude, longitude, altitude_m)
    SELECT v.codigo, v.nome, v.pais, v.cidade, v.latitude, v.longitude, v.altitude_m
    FROM (VALUES
        (N'J04', N'Estação Óptica Terrestre da ESA', N'Espanha', N'Tenerife', 28.300833, -16.511944, 2393),
        (N'246', N'Observatorio Klet', N'Republica Checa', N'České Budějovice', 48.863889, 14.284722, 1070),
        (N'033', N'Observatório Estadual da Turíngia Tautenburg', N'Alemanha', N'Tautenburg', 50.980111, 11.711167, 341),
        (N'Z84', N'Observatório de Calar Alto-Schmidt', N'Espanha', N'Gergal', 37.223611, -2.546111, 2168),
        (N'J75', N'Observatorio Astronómico de La Sagra', N'Espanha', N'Granada', 37.982778, -2.566111, 1530),
        (N'204', N'Observatorio Schiaparelli', N'Itália', N'Varese', 45.867778, 8.770556, 1205),
        (N'B63', N'Observatorio Solaris', N'Polónia', N'Luczanowice', 50.111667, 20.108056, 240),
        (N'L80', N'Observatorio SpringBok', N'Namíbia', N'Tivoli', -23.46, 18.0175, 1340),
        (N'Q12', N'Observatorio Nagano', N'Japão', N'Nagano', 36.476944, 137.825278, 730),
        (N'W57', N'Observatorio La Silla TBT da ESA', N'Chile', N'La Higuera', -29.255278, -70.739167, 2326),
        (N'Z58', N'Observatorio Cebreros TBT da ESA', N'Espanha', N'Cebreros', 40.454167, -4.37, 706)
    ) AS v(codigo, nome, pais, cidade, latitude, longitude, altitude_m)
    WHERE NOT EXISTS (SELECT 1 FROM dbo.Centro_Observacao c WHERE c.codigo = v.codigo);

    ----------------------------------------------------------------------
    -- 2) EQUIPAMENTOS (equipamento.csv)
    -- Regra unidades:
    --   <= 50  -> assume metros e converte para mm (x1000)
    --   >  50  -> assume já em mm (não mexe)
    ----------------------------------------------------------------------
    INSERT INTO dbo.Equipamento (id_centro, nome, tipo, modelo, diametro_mm, distancia_focal_mm)
    SELECT
        c.id_centro,
        v.nome,
        v.tipo,
        NULLIF(v.modelo, N'') AS modelo,
        CASE
            WHEN v.abertura_m IS NULL THEN NULL
            WHEN v.abertura_m > 50 THEN v.abertura_m
            ELSE v.abertura_m * 1000
        END AS diametro_mm,
        CASE
            WHEN v.distancia_focal_m IS NULL THEN NULL
            WHEN v.distancia_focal_m > 50 THEN v.distancia_focal_m
            ELSE v.distancia_focal_m * 1000
        END AS distancia_focal_mm
    FROM (VALUES
        (N'033', N'Telescópio Óptico Alfred Jensch', N'Telescópio Universal Refletor', NULL, 2.0, 4.0),
        (N'204', N'Cúpula Galileo', N'Refletor', N'Cupola Galileo', 0.84, NULL),
        (N'Z84', N'Telescópio Schmidt', N'Catadióptrico', N'FLI ProLine 23042', 0.08, NULL),
        (N'Z58', N'Telescópios de Plataforma de Teste', N'Robótico', N'Test-Bed Telescope (>400mm)', 0.56, 1415.5),
        (N'246', N'Telescópio KLENOT', N'Refletor', NULL, 1.06, 2.862),
        (N'246', N'Telescópio Maksutov', N'Catadióptrico', N'Maksutov–Cassegrain', 0.15, 1.8),
        (N'Z84', N'Telescópio de 3.5 m de Calar Alto', N'Telescópio Cassegrain', NULL, 3.5, NULL)
    ) AS v(centro_codigo, nome, tipo, modelo, abertura_m, distancia_focal_m)
    JOIN dbo.Centro_Observacao c ON c.codigo = v.centro_codigo
    WHERE NOT EXISTS (
        SELECT 1
        FROM dbo.Equipamento e
        WHERE e.id_centro = c.id_centro
          AND e.nome = v.nome
    );

    ----------------------------------------------------------------------
    -- 3) ASTRÓNOMOS (astronomo.csv)
    -- dbo.Astronomo não tem telefone/funcao -> vão para Observacao.notas
    ----------------------------------------------------------------------
    INSERT INTO dbo.Astronomo (nome_completo, email, afiliacao)
    SELECT v.nome_completo, v.email, v.centro_codigo
    FROM (VALUES
        (N'246', N'Jana Tichá', N'jticha@klet.cz', N'38 635 20 44', N'Investigadora', 6),
        (N'Z84', N'José Feliciano Agüí Fernández', N'feli@caha.es', N'950 632 579', N'Astrónomo', 7),
        (N'033', N'João Paulo Bernaldez', N'jbern@tls-tautenburg.de', N'49 36427 863 67', N'Pesquisador', 1)
    ) AS v(centro_codigo, nome_completo, email, telefone, funcao, equip_csv_id)
    WHERE NOT EXISTS (
        SELECT 1
        FROM dbo.Astronomo a
        WHERE a.nome_completo = v.nome_completo
          AND ISNULL(a.afiliacao,'') = v.centro_codigo
    );

    ----------------------------------------------------------------------
    -- 4) SOFTWARE mínimo (garante pelo menos 1 fixo)
    ----------------------------------------------------------------------
    IF NOT EXISTS (SELECT 1 FROM dbo.Software WHERE nome = 'ESA NEOCC Services')
    BEGIN
        INSERT dbo.Software (nome, versao, fornecedor)
        VALUES ('ESA NEOCC Services', NULL, 'ESA');
    END;

    ----------------------------------------------------------------------
    -- 5) ASTEROIDE ÂNCORA (REF0000)
    ----------------------------------------------------------------------
    IF NOT EXISTS (SELECT 1 FROM dbo.Asteroide WHERE pdes = 'REF0000')
    BEGIN
        INSERT dbo.Asteroide (id_csv_original, spkid, pdes, nome_completo, flag_neo, flag_pha)
        VALUES (NULL, NULL, 'REF0000', 'Objeto de referência (ligações internas)', 0, 0);
    END;

    DECLARE @id_ref  INT = (SELECT TOP 1 id_asteroide FROM dbo.Asteroide WHERE pdes='REF0000');
    DECLARE @id_soft INT = (SELECT TOP 1 id_software FROM dbo.Software WHERE nome='ESA NEOCC Services');

    ----------------------------------------------------------------------
    -- 6) LIGAÇÕES via Observacao (modo='REFERENCIA')
    --    Usa o "equip_csv_id" para escolher o equipamento correto por nome+centro
    --    e grava telefone/funcao/notas do equipamento em Observacao.notas
    ----------------------------------------------------------------------
    ;WITH src_equip AS (
        SELECT * FROM (VALUES
            (1, N'033', N'Telescópio Óptico Alfred Jensch', N'É caracterizado por um campo de visão extremamente amplo e, portanto, é particularmente adequado para tirar fotos de objetos grandes.'),
            (2, N'204', N'Cúpula Galileo', N'Telescópio refletor principal do Observatório Schiaparelli'),
            (3, N'Z84', N'Telescópio Schmidt', N'O telescópio Schmidt (abertura de 80 cm, espelho de 1,2 m) está atualmente sob contrato com a Agência Espacial Europeia para monitoramento de NEOs.'),
            (4, N'Z58', N'Telescópios de Plataforma de Teste', N'Os Telescópios de Teste são usados para desenvolver e testar software, operação remota e técnicas de processamento de dados para o programa ESA TBT.'),
            (5, N'246', N'Telescópio KLENOT', N'O telescópio KLENOT utiliza um espelho parabólico em Zerodur fabricado pela Carl Zeiss Jena, garantindo grande estabilidade térmica e alta precisão.'),
            (6, N'246', N'Telescópio Maksutov', N'O telescópio Maksutov utiliza um espelho esférico combinado com uma lente corretora meniscal negativa colocada na abertura do tubo, reduzindo aberrações e proporcionando imagens nítidas.'),
            (7, N'Z84', N'Telescópio de 3.5 m de Calar Alto', N'O telescópio de 3,5 m em Calar Alto, o maior da Europa continental, combina um design Cassegrain com instrumentos avançados para astrometria e fotometria.')
        ) AS v(equip_csv_id, centro_codigo, equip_nome, equip_notas)
    ),
    src_astr AS (
        SELECT * FROM (VALUES
            (N'246', N'Jana Tichá', N'jticha@klet.cz', N'38 635 20 44', N'Investigadora', 6),
            (N'Z84', N'José Feliciano Agüí Fernández', N'feli@caha.es', N'950 632 579', N'Astrónomo', 7),
            (N'033', N'João Paulo Bernaldez', N'jbern@tls-tautenburg.de', N'49 36427 863 67', N'Pesquisador', 1)
        ) AS v(centro_codigo, nome_completo, email, telefone, funcao, equip_csv_id)
    )
    INSERT INTO dbo.Observacao
    (id_asteroide, id_astronomo, id_equipamento, id_software, datahora_observacao, duracao_min, modo, notas)
    SELECT
        @id_ref,
        a.id_astronomo,
        e.id_equipamento,
        @id_soft,
        CAST('2000-01-01 00:00:00' AS DATETIME2(0)),
        0,
        'REFERENCIA',
        CONCAT(
            N'Ligação de referência | centro=', sa.centro_codigo,
            N' | equipamento=', se.equip_nome,
            N' | astronomo=', sa.nome_completo,
            CASE WHEN sa.email    IS NULL THEN N'' ELSE CONCAT(N' | email=', sa.email) END,
            CASE WHEN sa.telefone IS NULL THEN N'' ELSE CONCAT(N' | tel=', sa.telefone) END,
            CASE WHEN sa.funcao   IS NULL THEN N'' ELSE CONCAT(N' | funcao=', sa.funcao) END,
            CASE WHEN se.equip_notas IS NULL THEN N'' ELSE CONCAT(N' | notas_equip=', se.equip_notas) END
        )
    FROM src_astr sa
    JOIN src_equip se ON se.equip_csv_id = sa.equip_csv_id
    JOIN dbo.Centro_Observacao c ON c.codigo = sa.centro_codigo
    JOIN dbo.Equipamento e ON e.id_centro = c.id_centro AND e.nome = se.equip_nome
    JOIN dbo.Astronomo a ON a.nome_completo = sa.nome_completo AND ISNULL(a.afiliacao,'') = sa.centro_codigo
    WHERE NOT EXISTS (
        SELECT 1
        FROM dbo.Observacao o
        WHERE o.id_asteroide=@id_ref
          AND o.id_astronomo=a.id_astronomo
          AND o.id_equipamento=e.id_equipamento
          AND o.id_software=@id_soft
          AND o.modo='REFERENCIA'
    );

    COMMIT;

    PRINT '=== CSV inseridos manualmente + ligações criadas (REFERENCIA) ===';

END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0 ROLLBACK;

    DECLARE @msg NVARCHAR(4000) = ERROR_MESSAGE();
    DECLARE @line INT = ERROR_LINE();
    RAISERROR('Erro ao inserir CSV manualmente (linha %d): %s', 16, 1, @line, @msg);
END CATCH;
GO
