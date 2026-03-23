import streamlit as st
import pandas as pd
from io import BytesIO
import zipfile
from datetime import datetime

st.set_page_config(page_title="GeCO Generator", layout="wide")

st.title("📄 GeCO File Generator")

st.markdown("Carica i file e genera automaticamente Import Standard e Recapiti")

# -----------------------
# FUNZIONI UTILI
# -----------------------

def add_zero_if_needed(value):
    if pd.isna(value):
        return ""
    value = str(value).strip()
    if value == "":
        return ""
    if value.startswith("0"):
        return value
    if value.startswith("00") or value.startswith("+"):
        return value
    return "0" + value

def check_columns(df, required_cols):
    missing = [c for c in required_cols if c not in df.columns]
    return missing

# -----------------------
# UPLOAD FILE
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

    df = pd.read_csv(file_csv)

    required_cols = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    missing = check_columns(df, required_cols)

    if missing:
        st.error(f"❌ Colonne mancanti nel CSV: {missing}")
        st.stop()

    # =========================
    # IMPORT STANDARD
    # =========================
    template_import = pd.read_excel(file_import)

    for i, row in df.iterrows():
        if i >= len(template_import):
            template_import.loc[i] = ""

        template_import.at[i, "A"] = row["J"]
        template_import.at[i, "D"] = row["O"]
        template_import.at[i, "E"] = row["J"]  # fallback
        template_import.at[i, "I"] = row["W"]
        template_import.at[i, "J"] = row["K"]
        template_import.at[i, "K"] = row["L"]
        template_import.at[i, "L"] = row["M"]
        template_import.at[i, "M"] = row["N"]
        template_import.at[i, "N"] = row["F"]
        template_import.at[i, "O"] = row["H"]
        template_import.at[i, "P"] = row["G"]
        template_import.at[i, "U"] = add_zero_if_needed(row["A"])

    buffer_import = BytesIO()
    template_import.to_excel(buffer_import, index=False)
    buffer_import.seek(0)

    # =========================
    # RECAPITI
    # =========================
    template_recap = pd.read_excel(file_recap)

    for i, row in df.iterrows():
        if i >= len(template_recap):
            template_recap.loc[i] = ""

        template_recap.at[i, "B"] = add_zero_if_needed(row["A"])

        telefoni = []
        for col in ["Q", "R", "S", "T", "U", "V"]:
            val = row[col]
            if pd.notna(val) and str(val).strip() != "":
                telefoni.append(add_zero_if_needed(val))

        col_index = ord("H")
        for t in telefoni:
            template_recap.at[i, chr(col_index)] = t
            col_index += 1

    buffer_recap = BytesIO()
    template_recap.to_excel(buffer_recap, index=False)
    buffer_recap.seek(0)

    # =========================
    # ZIP
    # =========================
    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, "w") as z:
        z.writestr("GeCO_import_standard.xlsx", buffer_import.getvalue())
        z.writestr("GeCO_recapiti.xlsx", buffer_recap.getvalue())

    zip_buffer.seek(0)

    st.success("✅ File generati correttamente")

    st.download_button(
        "⬇️ Scarica ZIP",
        data=zip_buffer,
        file_name=f"geco_output_{datetime.now().strftime('%Y%m%d_%H%M')}.zip",
        mime="application/zip"
    )
