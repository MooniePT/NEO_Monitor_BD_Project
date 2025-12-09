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

PRINT '=== POVOAMENTO CONCLUÍDO ==='
GO
