------------------------------------------------------------
-- File: sql/03_create_triggers.sql
-- Descrição: Triggers de regras de negócio
------------------------------------------------------------
USE BD_PL2_09;
GO

/***********************************************************
  1) TRG_SolucaoOrbital_UnicaAtual
     - Garante que para cada asteroide existe, no máximo,
       uma solução orbital marcada como solucao_atual = 1.
************************************************************/
IF OBJECT_ID('dbo.TRG_SolucaoOrbital_UnicaAtual','TR') IS NOT NULL
    DROP TRIGGER dbo.TRG_SolucaoOrbital_UnicaAtual;
GO

CREATE TRIGGER dbo.TRG_SolucaoOrbital_UnicaAtual
ON dbo.Solucao_Orbital
AFTER INSERT, UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    ;WITH AstComAtual AS (
        SELECT DISTINCT id_asteroide
        FROM inserted
        WHERE solucao_atual = 1
    )
    UPDATE so
    SET solucao_atual = 0
    FROM dbo.Solucao_Orbital AS so
    JOIN AstComAtual AS x
        ON x.id_asteroide = so.id_asteroide
    WHERE so.id_solucao_orbital NOT IN (
        SELECT id_solucao_orbital
        FROM inserted
        WHERE solucao_atual = 1
    );
END;
GO

/***********************************************************
  2) TRG_AproximacaoProxima_GeraAlerta
     - Quando se regista/actualiza uma aproximação marcada
       como crítica (flag_critica = 1) e com data futura,
       cria um alerta associado.
************************************************************/
IF OBJECT_ID('dbo.TRG_AproximacaoProxima_GeraAlerta','TR') IS NOT NULL
    DROP TRIGGER dbo.TRG_AproximacaoProxima_GeraAlerta;
GO

CREATE TRIGGER dbo.TRG_AproximacaoProxima_GeraAlerta
ON dbo.Aproximacao_Proxima
AFTER INSERT, UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @id_prioridade INT;
    DECLARE @id_nivel INT;

    -- Prioridade 'ALTA' (ou o menor id se não existir)
    SELECT TOP (1) @id_prioridade = id_prioridade_alerta
    FROM dbo.Prioridade_Alerta
    WHERE codigo = 'ALTA';

    IF @id_prioridade IS NULL
        SELECT TOP (1) @id_prioridade = id_prioridade_alerta
        FROM dbo.Prioridade_Alerta
        ORDER BY id_prioridade_alerta;

    -- Nível 'VERMELHO' (ou o menor id se não existir)
    SELECT TOP (1) @id_nivel = id_nivel_alerta
    FROM dbo.Nivel_Alerta
    WHERE codigo = 'VERMELHO';

    IF @id_nivel IS NULL
        SELECT TOP (1) @id_nivel = id_nivel_alerta
        FROM dbo.Nivel_Alerta
        ORDER BY id_nivel_alerta;

    IF @id_prioridade IS NULL OR @id_nivel IS NULL
        RETURN;

    INSERT INTO dbo.Alerta (
        datahora_geracao,
        codigo_regra,
        titulo,
        descricao,
        id_asteroide,
        id_solucao_orbital,
        id_aproximacao_proxima,
        id_prioridade_alerta,
        id_nivel_alerta,
        ativo
    )
    SELECT
        SYSDATETIME()                                       AS datahora_geracao,
        'APROX_CRITICA'                                     AS codigo_regra,
        CONCAT('Aproximação crítica de ', a.nome_completo) AS titulo,
        CONCAT(
            'Aproximação crítica prevista para ',
            CONVERT(varchar(19), i.datahora_aproximacao, 120),
            ' a ',
            i.distancia_ld, ' LD (',
            i.distancia_ua, ' UA).'
        )                                                   AS descricao,
        i.id_asteroide,
        i.id_solucao_orbital,
        i.id_aproximacao_proxima,
        @id_prioridade,
        @id_nivel,
        1                                                   AS ativo
    FROM inserted AS i
    JOIN dbo.Asteroide AS a
         ON a.id_asteroide = i.id_asteroide
    WHERE i.flag_critica = 1
      AND i.datahora_aproximacao >= SYSDATETIME()
      AND NOT EXISTS (
            SELECT 1
            FROM dbo.Alerta AS al
            WHERE al.id_aproximacao_proxima = i.id_aproximacao_proxima
              AND al.codigo_regra = 'APROX_CRITICA'
              AND al.ativo = 1
        );
END;
GO

/***********************************************************
  3) TRG_Alerta_SoftDelete
     - Em vez de apagar alertas, marca-os como inactivos.
************************************************************/
IF OBJECT_ID('dbo.TRG_Alerta_SoftDelete','TR') IS NOT NULL
    DROP TRIGGER dbo.TRG_Alerta_SoftDelete;
GO

CREATE TRIGGER dbo.TRG_Alerta_SoftDelete
ON dbo.Alerta
INSTEAD OF DELETE
AS
BEGIN
    SET NOCOUNT ON;

    UPDATE al
    SET ativo = 0
    FROM dbo.Alerta AS al
    JOIN deleted AS d
         ON d.id_alerta = al.id_alerta;
END;
GO

/***********************************************************
  4) TRG_Observacao_DataValida
     - Impede observações no futuro ou antes da
       data de descoberta do asteroide.
************************************************************/
IF OBJECT_ID('dbo.TRG_Observacao_DataValida','TR') IS NOT NULL
    DROP TRIGGER dbo.TRG_Observacao_DataValida;
GO

CREATE TRIGGER dbo.TRG_Observacao_DataValida
ON dbo.Observacao
AFTER INSERT, UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    IF EXISTS (
        SELECT 1
        FROM inserted AS i
        WHERE i.datahora_observacao > SYSDATETIME()
    )
    BEGIN
        RAISERROR (
            'Data/hora da observação inválida: não pode ser no futuro.',
            16, 1
        );
        ROLLBACK TRANSACTION;
        RETURN;
    END;
END;
GO
