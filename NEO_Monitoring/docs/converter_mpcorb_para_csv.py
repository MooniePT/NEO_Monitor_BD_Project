from pathlib import Path
from datetime import datetime
import csv

# ======= CONFIGURAÇÃO =======
BASE_DIR = Path(__file__).parent
INPUT_FILE = BASE_DIR / "MPCORB.DAT"
OUTPUT_FILE = BASE_DIR / "mpcorb.csv"
# =============================


def unpack_packed_epoch(packed: str) -> str:
    """
    Converte a data compactada do MPC (ex: 'K25BL') para 'YYYY-MM-DD'.
    Formato: CYYMD
      C: I=1800, J=1900, K=2000
      YY: ano
      M: mês (1-9, A=10, B=11, C=12)
      D: dia (1-9, A=10, ..., V=31)
    """
    if not packed or len(packed) != 5:
        return ""

    century_map = {"I": 1800, "J": 1900, "K": 2000}
    c = packed[0]
    if c not in century_map:
        return ""

    year = century_map[c] + int(packed[1:3])

    m_char = packed[3]
    if m_char.isdigit():
        month = int(m_char)
    else:
        month = 10 + (ord(m_char) - ord("A"))

    d_char = packed[4]
    if d_char.isdigit():
        day = int(d_char)
    else:
        day = 10 + (ord(d_char) - ord("A"))

    try:
        dt = datetime(year, month, day)
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return ""


def date_to_jd(date_str: str) -> str:
    """
    Converte data 'YYYY-MM-DD' para Julian Date em string (com 5 casas decimais).
    """
    if not date_str:
        return ""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        a = (14 - dt.month) // 12
        y = dt.year + 4800 - a
        m = dt.month + 12 * a - 3
        jdn = (
            dt.day
            + (153 * m + 2) // 5
            + 365 * y
            + y // 4
            - y // 100
            + y // 400
            - 32045
        )
        jd = jdn - 0.5  # JD começa ao meio-dia
        return f"{jd:.5f}"
    except Exception:
        return ""


def parse_mpc_line(line: str):
    """
    Faz o parse de uma linha do MPCORB.DAT (largura fixa, 202 chars)
    e devolve uma lista de campos prontos para o CSV.
    """
    line = line.rstrip("\n")
    if len(line) < 10:
        return None

    line = line.ljust(202)

    packed_desig = line[0:7].strip()
    H = line[8:13].strip()
    G = line[14:19].strip()
    epoch_packed = line[20:25].strip()
    M = line[26:35].strip()
    peri = line[37:46].strip()
    node = line[48:57].strip()
    incl = line[59:68].strip()
    e = line[70:79].strip()
    n = line[80:91].strip()
    a = line[92:103].strip()
    U = line[105:106].strip()
    ref = line[107:116].strip()
    n_obs = line[117:122].strip()
    n_opps = line[123:126].strip()
    arc = line[127:136].strip()
    rms = line[137:141].strip()
    pert_coarse = line[142:145].strip()
    pert_prec = line[146:149].strip()
    computer = line[150:160].strip()
    hexflags = line[161:165].strip()
    designation = line[166:194].strip()
    last_obs = line[194:202].strip()

    epoch_date = unpack_packed_epoch(epoch_packed)
    epoch_jd = date_to_jd(epoch_date)

    # pdes compatível com o neo.csv:
    #   "(1) Ceres" -> "1"
    #   "1995 SG75" -> "1995 SG75"
    #   fallback -> packed_desig ("00001")
    pdes = ""
    if designation.startswith("(") and ")" in designation:
        closing = designation.find(")")
        num_str = designation[1:closing]
        if num_str.isdigit():
            pdes = num_str
    if not pdes:
        pdes = designation if designation else packed_desig

    return [
        packed_desig,  # 0
        H,             # 1
        G,             # 2
        epoch_packed,  # 3
        epoch_date,    # 4
        epoch_jd,      # 5
        M,             # 6
        peri,          # 7
        node,          # 8
        incl,          # 9
        e,             # 10
        n,             # 11
        a,             # 12
        U,             # 13
        ref,           # 14
        n_obs,         # 15
        n_opps,        # 16
        arc,           # 17
        rms,           # 18
        pert_coarse,   # 19
        pert_prec,     # 20
        computer,      # 21
        hexflags,      # 22
        designation,   # 23
        last_obs,      # 24
        pdes           # 25
    ]


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Ficheiro {INPUT_FILE} não encontrado.")

    with INPUT_FILE.open("r", encoding="utf-8", errors="ignore") as fin, \
         OUTPUT_FILE.open("w", newline="", encoding="utf-8") as fout:

        writer = csv.writer(fout, delimiter=';')
        # Cabeçalho do CSV
        headers = [
            "packed_desig", "H", "G", "epoch_packed", "epoch_date", "epoch_jd",
            "M", "peri", "node", "incl", "e", "n", "a", "U", "ref",
            "n_obs", "n_opps", "arc", "rms", "pert_coarse", "pert_prec",
            "computer", "hexflags", "designation", "last_obs", "pdes"
        ]
        writer.writerow(headers)

        linhas_total = 0
        linhas_dados = 0

        for i, line in enumerate(fin, start=1):
            linhas_total += 1

            # Saltar cabeçalho do MPCORB (primeiras 43 linhas, pela estrutura do ficheiro)
            if i <= 43:
                continue

            if not line.strip():
                continue

            row = parse_mpc_line(line)
            if row is None:
                continue

            writer.writerow(row)
            linhas_dados += 1

    print(f"Concluído. Linhas lidas: {linhas_total}, linhas de dados: {linhas_dados}")
    print(f"CSV criado em: {OUTPUT_FILE.absolute()}")


if __name__ == "__main__":
    main()
