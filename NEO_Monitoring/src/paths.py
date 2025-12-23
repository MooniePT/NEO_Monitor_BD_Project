from pathlib import Path

def get_project_root() -> Path:
    """
    Devolve a pasta NEO_Monitoring, independentemente de onde corres o python.
    Procura para cima até encontrar as pastas docs/sql/src.
    """
    here = Path(__file__).resolve()
    candidates = [here.parent.parent, *here.parent.parent.parents]  # src/.. e pais
    for p in candidates:
        if (p / "docs").exists() and (p / "sql").exists() and (p / "src").exists():
            return p
    return here.parent.parent  # fallback

PROJECT_ROOT = get_project_root()
DOCS_DIR = PROJECT_ROOT / "docs"
SQL_DIR  = PROJECT_ROOT / "sql"
ASSETS_DIR = PROJECT_ROOT / "assets"
