-- VIEW para Diâmetro Estimado
-- Fórmula: D(km) = 1329 / sqrt(albedo) * 10^(-H/5)
-- Se albedo NULL → assumir 0.14 (média típica)

USE BD_PL2_09;
GO

IF EXISTS (SELECT * FROM sys.views WHERE name = 'vw_Asteroide_ComDiametro')
    DROP VIEW dbo.vw_Asteroide_ComDiametro;
GO

CREATE VIEW dbo.vw_Asteroide_ComDiametro AS
SELECT 
    id_asteroide,
    nasa_id,
    spkid,
    pdes,
    nome_asteroide,
    prefixo,
    nome_completo,
    flag_neo,
    flag_pha,
    h_mag,
    diametro_km,
    diametro_sigma_km,
    albedo,
    ast_key,
    -- Diâmetro estimado quando diametro_km é NULL
    COALESCE(
        diametro_km,
        CASE 
            WHEN h_mag IS NOT NULL THEN
                1329.0 * POWER(10.0, -h_mag/5.0) / SQRT(COALESCE(albedo, 0.14))
            ELSE NULL
        END
    ) AS diametro_estimado_km
FROM dbo.Asteroide;
GO
