
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Wczytanie danych
@st.cache_data
def load_data():
    df = pd.read_excel("LISTA_WPLAT_czysty.ods", engine="odf", header=2)
    df.columns = df.iloc[0]
    df = df[1:].reset_index(drop=True)
    df = df.dropna(how="all")
    df = df.dropna(axis=1, how="all")
    return df

df = load_data()

# Ustawienie nagłówków
df.columns.name = None
df = df.rename(columns=lambda x: str(x).strip())
month_cols = ['Wrzesień', 'Październik', 'Listopad', 'Grudzień',
              'Styczeń', 'Luty', 'Marzec', 'Kwiecień', 'Maj', 'Czerwiec']

# Konwersja wartości miesięcznych na liczby
for col in month_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

st.title("💰 Aplikacja do obsługi listy wpłat")

# 🔍 Wyszukiwanie
search = st.text_input("Wyszukaj po imieniu lub nazwisku")
if search:
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
st.subheader("📋 Dane")
st.dataframe(df[["Nazwisko i Imię", "Klasa"] + month_cols])

# 💾 Eksport danych
st.download_button("💾 Pobierz dane jako CSV", df.to_csv(index=False).encode("utf-8"), "lista_wplat.csv", "text/csv")
