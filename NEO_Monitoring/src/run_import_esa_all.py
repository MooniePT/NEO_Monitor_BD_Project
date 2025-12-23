from paths import DOCS_DIR
from db import pedir_e_ligar_bd
from services.import_esa import (
    importar_risk_list,
    importar_special_risk_list,
    importar_past_impactors,
    importar_removed_from_risk,
    importar_upcoming_cl_app,
    importar_search_result,
)

LIMPAR_TABELAS_ANTES = False  # põe True se quiseres apagar e reimportar

def limpar_tabelas_esa(conn) -> None:
    cur = conn.cursor()
    cur.execute("DELETE FROM dbo.ESA_RESULTADOS_PESQUISA;")
    cur.execute("DELETE FROM dbo.ESA_APROXIMACOES_PROXIMAS;")
    cur.execute("DELETE FROM dbo.ESA_OBJETOS_REMOVIDOS_RISCO;")
    cur.execute("DELETE FROM dbo.ESA_IMPACTORES_PASSADOS;")
    cur.execute("DELETE FROM dbo.ESA_LISTA_RISCO_ESPECIAL;")
    cur.execute("DELETE FROM dbo.ESA_LISTA_RISCO_ATUAL;")
    conn.commit()
    cur.close()

def main():
    paths = {
        "riskList": DOCS_DIR / "riskList.csv",
        "specialRiskList": DOCS_DIR / "specialRiskList.csv",
        "pastImpactorsList": DOCS_DIR / "pastImpactorsList.csv",
        "removedObjectsFromRiskList": DOCS_DIR / "removedObjectsFromRiskList.csv",
        "upcomingClApp": DOCS_DIR / "upcomingClApp.csv",
        "searchResult": DOCS_DIR / "searchResult.csv",
    }

    missing = [str(p) for p in paths.values() if not p.exists()]
    if missing:
        raise FileNotFoundError("Faltam CSV em docs/: \n- " + "\n- ".join(missing))

    conn = pedir_e_ligar_bd()  # escolhe BD_PL2_09

    if LIMPAR_TABELAS_ANTES:
        print("A limpar tabelas ESA...")
        limpar_tabelas_esa(conn)

    print("A importar ESA... (searchResult pode demorar)")

    c1 = importar_risk_list(conn, str(paths["riskList"]))
    c2 = importar_special_risk_list(conn, str(paths["specialRiskList"]))
    c3 = importar_past_impactors(conn, str(paths["pastImpactorsList"]))
    c4 = importar_removed_from_risk(conn, str(paths["removedObjectsFromRiskList"]))
    c5 = importar_upcoming_cl_app(conn, str(paths["upcomingClApp"]))
    c6 = importar_search_result(conn, str(paths["searchResult"]))

    conn.close()

    print("\n=== IMPORT ESA CONCLUÍDO ===")
    print(f"riskList               -> {c1}")
    print(f"specialRiskList        -> {c2}")
    print(f"pastImpactorsList      -> {c3}")
    print(f"removedObjectsFromRisk -> {c4}")
    print(f"upcomingClApp          -> {c5}")
    print(f"searchResult           -> {c6}")

if __name__ == "__main__":
    main()
