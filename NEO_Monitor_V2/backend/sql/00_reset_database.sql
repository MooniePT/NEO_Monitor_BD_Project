------------------------------------------------------------
-- File: sql/00_reset_database.sql
-- Descrição: APAGA TODAS AS TABELAS para reiniciar do zero
-- CUIDADO: EXECUTE APENAS SE QUISER PERDER TODOS OS DADOS
------------------------------------------------------------
USE BD_PL2_09;
GO

PRINT '=== INICIANDO RESET TOTAL DA BASE DE DADOS ==='
GO

------------------------------------------------------------
-- 1. REMOVER TRIGGERS
------------------------------------------------------------
PRINT 'Removendo triggers...'
IF OBJECT_ID('dbo.TRG_SolucaoOrbital_UnicaAtual','TR') IS NOT NULL DROP TRIGGER dbo.TRG_SolucaoOrbital_UnicaAtual;
IF OBJECT_ID('dbo.TRG_AproximacaoProxima_GeraAlerta','TR') IS NOT NULL DROP TRIGGER dbo.TRG_AproximacaoProxima_GeraAlerta;
IF OBJECT_ID('dbo.TRG_Alerta_SoftDelete','TR') IS NOT NULL DROP TRIGGER dbo.TRG_Alerta_SoftDelete;
IF OBJECT_ID('dbo.TRG_Observacao_DataValida','TR') IS NOT NULL DROP TRIGGER dbo.TRG_Observacao_DataValida;
GO

------------------------------------------------------------
-- 2. REMOVER VIEWS
------------------------------------------------------------
PRINT 'Removendo views...'
IF OBJECT_ID('dbo.vw_Ultimos5AsteroidesDetetados','V') IS NOT NULL DROP VIEW dbo.vw_Ultimos5AsteroidesDetetados;
IF OBJECT_ID('dbo.vw_AsteroidesNEO','V') IS NOT NULL DROP VIEW dbo.vw_AsteroidesNEO;
IF OBJECT_ID('dbo.vw_AsteroidesPHA','V') IS NOT NULL DROP VIEW dbo.vw_AsteroidesPHA;
IF OBJECT_ID('dbo.vw_AsteroidesNEOePHA','V') IS NOT NULL DROP VIEW dbo.vw_AsteroidesNEOePHA;
IF OBJECT_ID('dbo.vw_CentrosComMaisObservacoes','V') IS NOT NULL DROP VIEW dbo.vw_CentrosComMaisObservacoes;
IF OBJECT_ID('dbo.vw_RankingAsteroidesPHA_MaiorDiametro','V') IS NOT NULL DROP VIEW dbo.vw_RankingAsteroidesPHA_MaiorDiametro;
IF OBJECT_ID('dbo.vw_Observacoes_Completo','V') IS NOT NULL DROP VIEW dbo.vw_Observacoes_Completo;
IF OBJECT_ID('dbo.vw_Alertas_Ativos_Detalhe','V') IS NOT NULL DROP VIEW dbo.vw_Alertas_Ativos_Detalhe;
IF OBJECT_ID('dbo.vw_ResumoAlertasPorNivel','V') IS NOT NULL DROP VIEW dbo.vw_ResumoAlertasPorNivel;
IF OBJECT_ID('dbo.vw_Asteroide_OrbitalAtual','V') IS NOT NULL DROP VIEW dbo.vw_Asteroide_OrbitalAtual;
IF OBJECT_ID('dbo.vw_ProximasAproximacoesCriticas','V') IS NOT NULL DROP VIEW dbo.vw_ProximasAproximacoesCriticas;
IF OBJECT_ID('dbo.vw_ESA_Lista_Risco_Atual','V') IS NOT NULL DROP VIEW dbo.vw_ESA_Lista_Risco_Atual;
IF OBJECT_ID('dbo.vw_ESA_Aproximacoes_Proximas','V') IS NOT NULL DROP VIEW dbo.vw_ESA_Aproximacoes_Proximas;
IF OBJECT_ID('dbo.vw_ESA_Resumo_Risco_Por_Objeto','V') IS NOT NULL DROP VIEW dbo.vw_ESA_Resumo_Risco_Por_Objeto;
GO

------------------------------------------------------------
-- 3. REMOVER TABELAS (Ordem inversa de dependência)
------------------------------------------------------------
PRINT 'Removendo tabelas...'

-- Tabelas ESA (dependem de Asteroide)
IF OBJECT_ID('dbo.ESA_RESULTADOS_PESQUISA', 'U') IS NOT NULL DROP TABLE dbo.ESA_RESULTADOS_PESQUISA;
IF OBJECT_ID('dbo.ESA_APROXIMACOES_PROXIMAS', 'U') IS NOT NULL DROP TABLE dbo.ESA_APROXIMACOES_PROXIMAS;
IF OBJECT_ID('dbo.ESA_OBJETOS_REMOVIDOS_RISCO', 'U') IS NOT NULL DROP TABLE dbo.ESA_OBJETOS_REMOVIDOS_RISCO;
IF OBJECT_ID('dbo.ESA_IMPACTORES_PASSADOS', 'U') IS NOT NULL DROP TABLE dbo.ESA_IMPACTORES_PASSADOS;
IF OBJECT_ID('dbo.ESA_LISTA_RISCO_ESPECIAL', 'U') IS NOT NULL DROP TABLE dbo.ESA_LISTA_RISCO_ESPECIAL;
IF OBJECT_ID('dbo.ESA_LISTA_RISCO_ATUAL', 'U') IS NOT NULL DROP TABLE dbo.ESA_LISTA_RISCO_ATUAL;

-- Tabelas de Imagens e Observações
IF OBJECT_ID('dbo.Imagem', 'U') IS NOT NULL DROP TABLE dbo.Imagem;
IF OBJECT_ID('dbo.Observacao', 'U') IS NOT NULL DROP TABLE dbo.Observacao;

-- Tabelas de Contexto Observacional
IF OBJECT_ID('dbo.Software', 'U') IS NOT NULL DROP TABLE dbo.Software;
IF OBJECT_ID('dbo.Astronomo', 'U') IS NOT NULL DROP TABLE dbo.Astronomo;
IF OBJECT_ID('dbo.Equipamento', 'U') IS NOT NULL DROP TABLE dbo.Equipamento;
IF OBJECT_ID('dbo.Centro_Observacao', 'U') IS NOT NULL DROP TABLE dbo.Centro_Observacao;

-- Tabelas de Alertas e Aproximações
IF OBJECT_ID('dbo.Alerta', 'U') IS NOT NULL DROP TABLE dbo.Alerta;
IF OBJECT_ID('dbo.Aproximacao_Proxima', 'U') IS NOT NULL DROP TABLE dbo.Aproximacao_Proxima;
IF OBJECT_ID('dbo.Solucao_Orbital', 'U') IS NOT NULL DROP TABLE dbo.Solucao_Orbital;

-- Tabelas Principais
IF OBJECT_ID('dbo.Asteroide', 'U') IS NOT NULL DROP TABLE dbo.Asteroide;

-- Tabelas de Apoio
IF OBJECT_ID('dbo.Prioridade_Alerta', 'U') IS NOT NULL DROP TABLE dbo.Prioridade_Alerta;
IF OBJECT_ID('dbo.Nivel_Alerta', 'U') IS NOT NULL DROP TABLE dbo.Nivel_Alerta;
IF OBJECT_ID('dbo.Classe_Orbital', 'U') IS NOT NULL DROP TABLE dbo.Classe_Orbital;

-- Tabelas Temporarias.
IF OBJECT_ID('dbo.neo_wizard', 'U') IS NOT NULL DROP TABLE dbo.neo_wizard;
IF OBJECT_ID('dbo.mpcorb_wizard', 'U') IS NOT NULL DROP TABLE dbo.mpcorb_wizard;  
GO

PRINT '=== RESET CONCLUÍDO - BASE DE DADOS LIMPA ==='
PRINT 'Agora execute os scripts na ordem: 01, 02, 03, 04, 05, 06 e 07.'
GO
