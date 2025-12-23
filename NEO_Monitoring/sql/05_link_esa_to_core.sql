USE BD_PL2_09;
GO
SET NOCOUNT ON;
GO

------------------------------------------------------------
-- 1) LIGAR id_asteroide nas tabelas ESA
-- Estratégia:
--   Passo A) match direto por nome_completo = designacao_objeto
--   Passo B) match removendo parêntesis (ex: "(101955) Bennu" -> "101955 Bennu")
--   Passo C) match removendo espaços (último recurso)
------------------------------------------------------------

-- Helper (expressões repetidas)
-- (não cria funções/tabelas novas, não mexe no diagrama)

--------------------------
-- ESA_LISTA_RISCO_ATUAL
--------------------------
UPDATE esa
SET esa.id_asteroide = a.id_asteroide
FROM dbo.ESA_LISTA_RISCO_ATUAL esa
JOIN dbo.Asteroide a
  ON a.nome_completo = esa.designacao_objeto
WHERE esa.id_asteroide IS NULL;

UPDATE esa
SET esa.id_asteroide = a.id_asteroide
FROM dbo.ESA_LISTA_RISCO_ATUAL esa
JOIN dbo.Asteroide a
  ON LTRIM(RTRIM(REPLACE(REPLACE(a.nome_completo,'(',''),')',''))) = LTRIM(RTRIM(esa.designacao_objeto))
WHERE esa.id_asteroide IS NULL;

UPDATE esa
SET esa.id_asteroide = a.id_asteroide
FROM dbo.ESA_LISTA_RISCO_ATUAL esa
JOIN dbo.Asteroide a
  ON REPLACE(REPLACE(REPLACE(REPLACE(a.nome_completo,'(',''),')',''),' ',''),'-','')
   = REPLACE(REPLACE(esa.designacao_objeto,' ',''),'-','')
WHERE esa.id_asteroide IS NULL;

--------------------------
-- ESA_LISTA_RISCO_ESPECIAL
--------------------------
UPDATE esa
SET esa.id_asteroide = a.id_asteroide
FROM dbo.ESA_LISTA_RISCO_ESPECIAL esa
JOIN dbo.Asteroide a
  ON a.nome_completo = esa.designacao_objeto
WHERE esa.id_asteroide IS NULL;

UPDATE esa
SET esa.id_asteroide = a.id_asteroide
FROM dbo.ESA_LISTA_RISCO_ESPECIAL esa
JOIN dbo.Asteroide a
  ON LTRIM(RTRIM(REPLACE(REPLACE(a.nome_completo,'(',''),')',''))) = LTRIM(RTRIM(esa.designacao_objeto))
WHERE esa.id_asteroide IS NULL;

UPDATE esa
SET esa.id_asteroide = a.id_asteroide
FROM dbo.ESA_LISTA_RISCO_ESPECIAL esa
JOIN dbo.Asteroide a
  ON REPLACE(REPLACE(REPLACE(REPLACE(a.nome_completo,'(',''),')',''),' ',''),'-','')
   = REPLACE(REPLACE(esa.designacao_objeto,' ',''),'-','')
WHERE esa.id_asteroide IS NULL;

--------------------------
-- ESA_IMPACTORES_PASSADOS
--------------------------
UPDATE esa
SET esa.id_asteroide = a.id_asteroide
FROM dbo.ESA_IMPACTORES_PASSADOS esa
JOIN dbo.Asteroide a
  ON a.nome_completo = esa.designacao_objeto
WHERE esa.id_asteroide IS NULL;

UPDATE esa
SET esa.id_asteroide = a.id_asteroide
FROM dbo.ESA_IMPACTORES_PASSADOS esa
JOIN dbo.Asteroide a
  ON LTRIM(RTRIM(REPLACE(REPLACE(a.nome_completo,'(',''),')',''))) = LTRIM(RTRIM(esa.designacao_objeto))
WHERE esa.id_asteroide IS NULL;

UPDATE esa
SET esa.id_asteroide = a.id_asteroide
FROM dbo.ESA_IMPACTORES_PASSADOS esa
JOIN dbo.Asteroide a
  ON REPLACE(REPLACE(REPLACE(REPLACE(a.nome_completo,'(',''),')',''),' ',''),'-','')
   = REPLACE(REPLACE(esa.designacao_objeto,' ',''),'-','')
WHERE esa.id_asteroide IS NULL;

--------------------------
-- ESA_OBJETOS_REMOVIDOS_RISCO
--------------------------
UPDATE esa
SET esa.id_asteroide = a.id_asteroide
FROM dbo.ESA_OBJETOS_REMOVIDOS_RISCO esa
JOIN dbo.Asteroide a
  ON a.nome_completo = esa.designacao_objeto
WHERE esa.id_asteroide IS NULL;

UPDATE esa
SET esa.id_asteroide = a.id_asteroide
FROM dbo.ESA_OBJETOS_REMOVIDOS_RISCO esa
JOIN dbo.Asteroide a
  ON LTRIM(RTRIM(REPLACE(REPLACE(a.nome_completo,'(',''),')',''))) = LTRIM(RTRIM(esa.designacao_objeto))
WHERE esa.id_asteroide IS NULL;

UPDATE esa
SET esa.id_asteroide = a.id_asteroide
FROM dbo.ESA_OBJETOS_REMOVIDOS_RISCO esa
JOIN dbo.Asteroide a
  ON REPLACE(REPLACE(REPLACE(REPLACE(a.nome_completo,'(',''),')',''),' ',''),'-','')
   = REPLACE(REPLACE(esa.designacao_objeto,' ',''),'-','')
WHERE esa.id_asteroide IS NULL;

--------------------------
-- ESA_APROXIMACOES_PROXIMAS
--------------------------
UPDATE esa
SET esa.id_asteroide = a.id_asteroide
FROM dbo.ESA_APROXIMACOES_PROXIMAS esa
JOIN dbo.Asteroide a
  ON a.nome_completo = esa.designacao_objeto
WHERE esa.id_asteroide IS NULL;

UPDATE esa
SET esa.id_asteroide = a.id_asteroide
FROM dbo.ESA_APROXIMACOES_PROXIMAS esa
JOIN dbo.Asteroide a
  ON LTRIM(RTRIM(REPLACE(REPLACE(a.nome_completo,'(',''),')',''))) = LTRIM(RTRIM(esa.designacao_objeto))
WHERE esa.id_asteroide IS NULL;

UPDATE esa
SET esa.id_asteroide = a.id_asteroide
FROM dbo.ESA_APROXIMACOES_PROXIMAS esa
JOIN dbo.Asteroide a
  ON REPLACE(REPLACE(REPLACE(REPLACE(a.nome_completo,'(',''),')',''),' ',''),'-','')
   = REPLACE(REPLACE(esa.designacao_objeto,' ',''),'-','')
WHERE esa.id_asteroide IS NULL;

--------------------------
-- ESA_RESULTADOS_PESQUISA
--------------------------
UPDATE esa
SET esa.id_asteroide = a.id_asteroide
FROM dbo.ESA_RESULTADOS_PESQUISA esa
JOIN dbo.Asteroide a
  ON a.nome_completo = esa.designacao_objeto
WHERE esa.id_asteroide IS NULL;

UPDATE esa
SET esa.id_asteroide = a.id_asteroide
FROM dbo.ESA_RESULTADOS_PESQUISA esa
JOIN dbo.Asteroide a
  ON LTRIM(RTRIM(REPLACE(REPLACE(a.nome_completo,'(',''),')',''))) = LTRIM(RTRIM(esa.designacao_objeto))
WHERE esa.id_asteroide IS NULL;

UPDATE esa
SET esa.id_asteroide = a.id_asteroide
FROM dbo.ESA_RESULTADOS_PESQUISA esa
JOIN dbo.Asteroide a
  ON REPLACE(REPLACE(REPLACE(REPLACE(a.nome_completo,'(',''),')',''),' ',''),'-','')
   = REPLACE(REPLACE(esa.designacao_objeto,' ',''),'-','')
WHERE esa.id_asteroide IS NULL;

------------------------------------------------------------
-- 2) (Opcional mas MUITO útil) Sincronizar aproximações ESA
--    para a tabela core dbo.Aproximacao_Proxima
------------------------------------------------------------
INSERT INTO dbo.Aproximacao_Proxima (
    id_asteroide,
    id_solucao_orbital,
    datahora_aproximacao,
    distancia_ua,
    distancia_ld,
    velocidade_rel_kms,
    flag_critica,
    origem
)
SELECT
    esa.id_asteroide,
    NULL,
    esa.datahora_aproximacao_utc,
    esa.miss_dist_au,
    esa.miss_dist_ld,
    esa.vel_rel_kms,
    CASE WHEN esa.miss_dist_ld IS NOT NULL AND esa.miss_dist_ld <= 10 THEN 1 ELSE 0 END,
    'ESA_IMPORT'
FROM dbo.ESA_APROXIMACOES_PROXIMAS esa
WHERE esa.id_asteroide IS NOT NULL
  AND esa.datahora_aproximacao_utc IS NOT NULL
  AND NOT EXISTS (
      SELECT 1
      FROM dbo.Aproximacao_Proxima ap
      WHERE ap.id_asteroide = esa.id_asteroide
        AND ap.datahora_aproximacao = esa.datahora_aproximacao_utc
  );

PRINT '=== ESA ligado ao core + aproximações sincronizadas ===';
GO

------------------------------------------------------------
-- 3) Checks rápidos
------------------------------------------------------------
SELECT COUNT(*) AS RiscoAtual_total, SUM(CASE WHEN id_asteroide IS NULL THEN 1 ELSE 0 END) AS RiscoAtual_sem_link
FROM dbo.ESA_LISTA_RISCO_ATUAL;

SELECT COUNT(*) AS AproxESA_total, SUM(CASE WHEN id_asteroide IS NULL THEN 1 ELSE 0 END) AS AproxESA_sem_link
FROM dbo.ESA_APROXIMACOES_PROXIMAS;

SELECT COUNT(*) AS AproxCore_ESA
FROM dbo.Aproximacao_Proxima
WHERE origem = 'ESA_IMPORT';
GO
