import streamlit as st
import pandas as pd
from io import BytesIO
import zipfile
from datetime import datetime

st.set_page_config(page_title="GeCO Generator", layout="wide")

# -----------------------
# LOGIN
# -----------------------
def login():
    if "logged" not in st.session_state:
        st.session_state.logged = False

    if not st.session_state.logged:
        st.title("🔐 Accesso")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Accedi"):
            if username == "RECAP" and password == "Recap26@":
                st.session_state.logged = True
                st.rerun()
            else:
                st.error("Credenziali errate")

        st.stop()

login()

# -----------------------
# APP
# -----------------------
st.title("📄 GeCO File Generator")
st.markdown("Carica i file e genera automaticamente Import Standard e Recapiti")

# -----------------------
# MAPPATURA COLONNE CSV
# -----------------------
CSV_MAP = {
    "A": "POS_NUM",
    "B": "POS_COD",
    "C": "LOTTO",
    "D": "DATA_AFFIDAMENTO",
    "E": "DATA_SCADENZA",
    "F": "CAPITALE",
    "G": "INTERESSI",
    "H": "ONERI",
    "I": "TOTALE",
    "J": "DBT_RAGIONESOCIALE",
    "K": "DBT_INDIRIZZO",
    "L": "DBT_CAP",
    "M": "DBT_COMUNE",
    "N": "DBT_PROVINCIA",
    "O": "DBT_CODFISCALE",
    "P": "DBT_PIVA",
    "Q": "TEL1",
    "R": "TEL2",
    "S": "TEL3",
    "T": "TEL4",
    "U": "TEL5",
    "V": "TEL6",
    "W": "EMAIL",
    "X": "NOTE1",
    "Y": "NOTE2",
    "Z": "UNNAMED: 25",
}

REQUIRED_REAL_COLUMNS = [
    "POS_NUM",
    "CAPITALE",
    "INTERESSI",
    "ONERI",
    "DBT_RAGIONESOCIALE",
    "DBT_INDIRIZZO",
    "DBT_CAP",
    "DBT_COMUNE",
    "DBT_PROVINCIA",
    "DBT_CODFISCALE",
    "EMAIL",
    "TEL1",
    "TEL2",
    "TEL3",
    "TEL4",
    "TEL5",
    "TEL6",
]

# -----------------------
# FUNZIONI
# -----------------------
def add_zero_if_needed(value):
    if pd.isna(value):
        return ""

    value = str(value).strip()

    if value == "" or value.lower() == "nan":
        return ""

    if value.startswith("+"):
        return value

    if value.startswith("00"):
        return value

    if value.startswith("0"):
        return value

    only_digits = "".join(ch for ch in value if ch.isdigit())
    if only_digits == "":
        return value

    return "0" + only_digits


def normalize_columns(df):
    df.columns = [str(c).strip().upper() for c in df.columns]
    return df


def read_csv_robust(uploaded_file):
    raw = uploaded_file.getvalue()

    encodings = ["utf-8-sig", "utf-8", "latin1", "cp1252"]
    seps = [";", ",", "\t", "|"]

    last_error = None

    for enc in encodings:
        for sep in seps:
            try:
                df = pd.read_csv(
                    BytesIO(raw),
                    sep=sep,
                    encoding=enc,
                    dtype=str,
                    keep_default_na=False,
                )
                df = normalize_columns(df)

                if len(df.columns) >= 10:
                    return df
            except Exception as e:
                last_error = e

    raise last_error if last_error else Exception("Impossibile leggere il CSV")


def read_excel_robust(uploaded_file):
    return pd.read_excel(uploaded_file, dtype=str)


def check_required_columns(df):
    return [c for c in REQUIRED_REAL_COLUMNS if c not in df.columns]


def get_csv_value(row, logical_col):
    real_col = CSV_MAP.get(logical_col, "")
    return row.get(real_col, "")

# -----------------------
# UPLOAD
# -----------------------
file_csv = st.file_uploader("📂 File madre (CSV)", type=["csv"])
file_import = st.file_uploader("📂 Template Import Standard (.xlsx)", type=["xlsx"])
file_recap = st.file_uploader("📂 Template Recapiti (.xlsx)", type=["xlsx"])

# -----------------------
# GENERAZIONE
# -----------------------
if st.button("🚀 Genera File"):
    if not file_csv or not file_import or not file_recap:
        st.error("❌ Carica tutti i file")
        st.stop()

    try:
        df = read_csv_robust(file_csv)
    except Exception:
        st.error("❌ Impossibile leggere il CSV. Controlla formato, separatore o encoding.")
        st.stop()

    missing = check_required_columns(df)
    if missing:
        st.error(f"❌ Colonne mancanti nel CSV: {missing}")
        st.write("Colonne trovate nel file:", list(df.columns))
        st.stop()

    try:
        template_import = read_excel_robust(file_import)
        template_recap = read_excel_robust(file_recap)
    except Exception:
        st.error("❌ Errore nella lettura dei template Excel.")
        st.stop()

    while len(template_import) < len(df):
        template_import.loc[len(template_import)] = ""

    while len(template_recap) < len(df):
        template_recap.loc[len(template_recap)] = ""

    # -----------------------
    # IMPORT STANDARD
    # -----------------------
    for i, row in df.iterrows():
        template_import.at[i, "A"] = get_csv_value(row, "J")   # DBT_RAGIONESOCIALE
        template_import.at[i, "D"] = get_csv_value(row, "O")   # DBT_CODFISCALE
        template_import.at[i, "E"] = ""                        # lasciata vuota
        template_import.at[i, "I"] = get_csv_value(row, "W")   # EMAIL
        template_import.at[i, "J"] = get_csv_value(row, "K")   # DBT_INDIRIZZO
        template_import.at[i, "K"] = get_csv_value(row, "L")   # DBT_CAP
        template_import.at[i, "L"] = get_csv_value(row, "M")   # DBT_COMUNE
        template_import.at[i, "M"] = get_csv_value(row, "N")   # DBT_PROVINCIA
        template_import.at[i, "N"] = get_csv_value(row, "F")   # CAPITALE
        template_import.at[i, "O"] = get_csv_value(row, "H")   # ONERI
        template_import.at[i, "P"] = get_csv_value(row, "G")   # INTERESSI
        template_import.at[i, "U"] = add_zero_if_needed(get_csv_value(row, "A"))  # POS_NUM

    buffer_import = BytesIO()
    template_import.to_excel(buffer_import, index=False)
    buffer_import.seek(0)

    # -----------------------
    # RECAPITI
    # -----------------------
    for i, row in df.iterrows():
        template_recap.at[i, "B"] = add_zero_if_needed(get_csv_value(row, "A"))  # POS_NUM

        telefoni = []
        for logical_col in ["Q", "R", "S", "T", "U", "V"]:
            val = get_csv_value(row, logical_col)
            if str(val).strip() != "":
                telefoni.append(add_zero_if_needed(val))

        for col in [chr(c) for c in range(ord("H"), ord("V") + 1)]:
            template_recap.at[i, col] = ""

        col_index = ord("H")
        for t in telefoni:
            if col_index <= ord("V"):
                template_recap.at[i, chr(col_index)] = t
                col_index += 1

    buffer_recap = BytesIO()
    template_recap.to_excel(buffer_recap, index=False)
    buffer_recap.seek(0)

    # -----------------------
    # ZIP
    # -----------------------
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("GeCO_import_standard.xlsx", buffer_import.getvalue())
        z.writestr("GeCO_recapiti.xlsx", buffer_recap.getvalue())

    zip_buffer.seek(0)

    st.success("✅ File generati correttamente")

    st.download_button(
        "⬇️ Scarica ZIP",
        data=zip_buffer,
        file_name=f"geco_output_{datetime.now().strftime('%Y%m%d_%H%M')}.zip",
        mime="application/zip",
    )
