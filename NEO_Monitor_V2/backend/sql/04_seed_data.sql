------------------------------------------------------------
-- File: sql/04_seed_data.sql
-- Descrição: Povoamento inicial de dados estáticos
------------------------------------------------------------
USE BD_PL2_09;
GO

PRINT '=== POVOANDO DADOS INICIAIS ==='
GO

------------------------------------------------------------
-- POVOAR CLASSE_ORBITAL
------------------------------------------------------------
PRINT 'Povoando tabela Classe_Orbital...'
GO

-- Garantir que está vazia antes de inserir (se for reset)
-- DELETE FROM dbo.Classe_Orbital; 
-- DBCC CHECKIDENT ('dbo.Classe_Orbital', RESEED, 0);

IF NOT EXISTS (SELECT * FROM dbo.Classe_Orbital)
BEGIN
    INSERT INTO dbo.Classe_Orbital (codigo, nome, descricao)
    VALUES 
        ('MBA', 'Main-Belt Asteroid', 'Main-Belt Asteroid (between Mars and Jupiter, ~2.1–3.3 AU)'),
        ('IMB', 'Inner Main-Belt Asteroid', 'Inner Main-Belt Asteroid (2.0–2.5 AU from Sun)'),
        ('OMB', 'Outer Main-Belt Asteroid', 'Outer Main-Belt Asteroid (3.0–3.5 AU from Sun)'),
        ('MCA', 'Mars-Crossing Asteroid', 'Mars-Crossing Asteroid (crosses Mars orbit but not Earth''s)'),
        ('AMO', 'Amor', 'Amor-type NEA'),
        ('APO', 'Apollo', 'Apollo-type NEA'),
        ('ATE', 'Aten', 'Aten-type NEA'),
        ('IEO', 'Atira', 'Atira-type NEA (Interior Earth Object)');
    PRINT '  Classes orbitais inseridas.';
END
ELSE
BEGIN
    PRINT '  Tabela Classe_Orbital já tem dados.';
END
GO

------------------------------------------------------------
-- POVOAR NIVEL_ALERTA
------------------------------------------------------------
PRINT 'Povoando tabela Nivel_Alerta...'
IF NOT EXISTS (SELECT * FROM dbo.Nivel_Alerta)
BEGIN
    INSERT INTO dbo.Nivel_Alerta (codigo, cor, descricao)
    VALUES
        ('VERDE',    'verde',    'Risco negligenciável'),
        ('AMARELO',  'amarelo',  'Risco baixo / atenção'),
        ('LARANJA',  'laranja',  'Risco moderado / ameaça'),
        ('VERMELHO', 'vermelho', 'Risco elevado / crítico');
    PRINT '  Níveis de alerta inseridos.';
END
ELSE
BEGIN
    PRINT '  Tabela Nivel_Alerta já tem dados.';
END
GO

------------------------------------------------------------
-- POVOAR PRIORIDADE_ALERTA
------------------------------------------------------------
PRINT 'Povoando tabela Prioridade_Alerta...'
IF NOT EXISTS (SELECT * FROM dbo.Prioridade_Alerta)
BEGIN
    INSERT INTO dbo.Prioridade_Alerta (codigo, nome, ordem)
    VALUES
        ('BAIXA', 'Baixa Prioridade', 10),
        ('MEDIA', 'Média Prioridade', 50),
        ('ALTA',  'Alta Prioridade',  90);
    PRINT '  Prioridades de alerta inseridas.';
END
ELSE
BEGIN
    PRINT '  Tabela Prioridade_Alerta já tem dados.';
END
GO


PRINT '=== POVOAMENTO CONCLUÍDO ==='
GO
