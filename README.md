# Miniapp GeCO Import

Miniapp Streamlit per generare automaticamente:
- `GeCO_import_standard_compilato.xlsx`
- `GeCO_recapiti_telefonici_compilato.xlsx`
- ZIP finale con entrambi i file

## Avvio in locale

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy su Streamlit Cloud

1. carica questi file su GitHub
2. crea una nuova app su Streamlit Cloud
3. file principale: `app.py`
4. la app sarà subito utilizzabile dal browser

## Nota importante

Per la colonna **E** del file import standard è stato impostato come default `DBT_PIVA`, perché nel tracciato CSV ricevuto questa è la corrispondenza più probabile.
Se vuoi usare un'altra colonna, puoi cambiarla dalla sidebar della app.
