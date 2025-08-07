
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Wczytanie danych
@st.cache_data
def load_data():
    df = pd.read_excel("LISTA_WPLAT_czysty.ods", engine="odf", header=None)

    # Szukanie wiersza z nagłówkiem (zawierającego "Nazwisko i Imię")
    header_row = df[df.apply(lambda row: row.astype(str).str.contains("Nazwisko i Imię", case=False).any(), axis=1)].index
    if not header_row.empty:
        header_idx = header_row[0]
        df.columns = df.iloc[header_idx]
        df = df[header_idx + 1:].reset_index(drop=True)
        df.columns.name = None
    else:
        st.error("❌ Nie znaleziono nagłówków z 'Nazwisko i Imię'")
        st.stop()

    return df

df = load_data()

# Przygotowanie kolumn miesięcznych
df.columns = df.columns.astype(str).str.strip()
month_cols = ['Wrzesień', 'Październik', 'Listopad', 'Grudzień',
              'Styczeń', 'Luty', 'Marzec', 'Kwiecień', 'Maj', 'Czerwiec']

# Konwersja danych miesięcznych do float
for col in month_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

st.title("💰 Aplikacja do obsługi listy wpłat")

# 🔍 Wyszukiwanie
search = st.text_input("Wyszukaj po imieniu lub nazwisku")
if search and "Nazwisko i Imię" in df.columns:
    df = df[df["Nazwisko i Imię"].str.contains(search, case=False, na=False)]

# ➕ Dodawanie nowej osoby
with st.expander("➕ Dodaj nową osobę"):
    with st.form("add_form"):
        name = st.text_input("Nazwisko i Imię")
        klasa = st.text_input("Klasa")
        new_row = {
            "Nazwisko i Imię": name,
            "Klasa": klasa,
            "Świetlica": "",
            "Kwota": "",
            "Warsztaty": "",
            "Dzień tygodnia": "",
            "Zgody zdjęcia": "",
        }
        for col in month_cols:
            new_row[col] = st.number_input(col, min_value=0.0, value=0.0, step=1.0)
        submitted = st.form_submit_button("Dodaj")
        if submitted and name:
            df.loc[len(df)] = new_row
            st.success(f"Dodano osobę: {name}")

# 📊 Wykres słupkowy - suma wpłat
st.subheader("📊 Suma wpłat miesięcznych")
monthly_sum = df[month_cols].sum()

fig, ax = plt.subplots()
monthly_sum.plot(kind="bar", ax=ax)
ax.set_ylabel("Suma wpłat (zł)")
st.pyplot(fig)

# 📋 Tabela z danymi
if "Nazwisko i Imię" in df.columns and "Klasa" in df.columns:
    st.subheader("📋 Dane")
    st.dataframe(df[["Nazwisko i Imię", "Klasa"] + [col for col in month_cols if col in df.columns]])
else:
    st.warning("Nie znaleziono kolumn 'Nazwisko i Imię' lub 'Klasa' w danych.")

# 💾 Eksport danych
st.download_button("💾 Pobierz dane jako CSV", df.to_csv(index=False).encode("utf-8"), "lista_wplat.csv", "text/csv")
