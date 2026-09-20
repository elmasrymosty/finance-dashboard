import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
from database import (
    incarca_tranzactii, 
    adauga_tranzactie, 
    sterge_toate_datele,
    incarca_bugete,
    salveaza_buget
)

# Configurare pagină
st.set_page_config(page_title="Dashboard Finanțe Personale", page_icon="📊", layout="wide")

st.title("📊 Dashboard de Finanțe Personale + Alerte Buget")
st.markdown("Urmărește-ți veniturile, cheltuielile și controlează-ți bugetul maxim pe categorii.")

# Încărcăm datele brute din fișiere
df = incarca_tranzactii()
bugete = incarca_bugete() # Dicționar cu limitele setate {Categorie: Limita}

# --- REZUMAT MATEMATIC (KPI-uri) ---
st.markdown("### 📈 Rezumat Financiar General")
col1, col2, col3 = st.columns(3)

if not df.empty:
    total_venituri = df[df["Tip"] == "Venit"]["Suma"].sum()
    total_cheltuieli = df[df["Tip"] == "Cheltuială"]["Suma"].sum()
    balanta_totala = total_venituri - total_cheltuieli
else:
    total_venituri, total_cheltuieli, balanta_totala = 0.0, 0.0, 0.0

with col1:
    st.metric(label="💰 Total Venituri", value=f"{total_venituri:.2f} RON")
with col2:
    st.metric(label="📉 Total Cheltuieli", value=f"{total_cheltuieli:.2f} RON")
with col3:
    st.metric(label="⚖️ Balanță (Economii)", value=f"{balanta_totala:.2f} RON", 
              delta=f"{'Profit' if balanta_totala >= 0 else 'Deficit'}")

st.markdown("---")

# --- MONITORIZARE BUGETE MAXIME (ALERTE VISUALE) ---
st.markdown("### ⚠️ Monitorizare Bugete Maxime pe Categorii")
if bugete and not df.empty:
    col_buget_1, col_buget_2 = st.columns(2)
    
    # Luăm doar cheltuielile
    df_cheltuieli_totale = df[df["Tip"] == "Cheltuială"]
    
    for i, (cat, limita) in enumerate(bugete.items()):
        # Calculăm cât s-a cheltuit de fapt în această categorie
        cheltuit = df_cheltuieli_totale[df_cheltuieli_totale["Categorie"] == cat]["Suma"].sum()
        procent = min(float(cheltuit / limita), 1.0) if limita > 0 else 0.0
        
        # Împărțim afișarea în mod egal pe cele 2 coloane pentru design curat
        with col_buget_1 if i % 2 == 0 else col_buget_2:
            st.markdown(f"**{cat}** — Cheltuit: `{cheltuit:.2f} RON` din limita de `{limita:.2f} RON`")
            
            if cheltuit > limita:
                # Alertă roșie de depășire
                st.error(f"🚨 BUGET DEPĂȘIT la {cat} cu {cheltuit - limita:.2f} RON!")
                st.progress(procent)
            elif cheltuit >= limita * 0.8:
                # Alertă galbenă de avertizare (80% din buget consumat)
                st.warning(f"⚠️ Atenție! Ai consumat {procent*100:.0f}% din bugetul pentru {cat}.")
                st.progress(procent)
            else:
                # Buget în zonă sigură (verde)
                st.success(f"✅ Buget în siguranță. Consumat: {procent*100:.0f}%")
                st.progress(procent)
else:
    st.info("💡 Sfat: Setează un 'Buget Maxim' din panoul din stânga pentru a activa alertele automate de cheltuieli.")

st.markdown("---")

# --- BARA LATERALĂ (SIDEBAR) ---
st.sidebar.header("📥 Adaugă Tranzacție")
tip_tranzactie = st.sidebar.selectbox("Tipul tranzacției", ["Cheltuială", "Venit"])

Toate_Categoriile_Cheltuieli = ["Mâncare", "Chirie/Utilități", "Transport", "Divertisment", "Sănătate", "Cumpărături"]

if tip_tranzactie == "Venit":
    categorii = ["Salariu", "Investiții", "Freelance", "Altele"]
else:
    categorii = Toate_Categoriile_Cheltuieli

categorie_aleasa = st.sidebar.selectbox("Categoria", categorii)
suma_introdusa = st.sidebar.number_input("Suma (RON)", min_value=0.01, step=10.0, key="suma_tr")
data_aleasa = st.sidebar.date_input("Data tranzacției", date.today())
descriere_introdusa = st.sidebar.text_input("Descriere scurtă")

if st.sidebar.button("Salvează Tranzacția", type="primary"):
    adauga_tranzactie(data_aleasa, tip_tranzactie, categorie_aleasa, suma_introdusa, descriere_introdusa)
    st.sidebar.success("Tranzacție salvată!")
    st.rerun()

st.sidebar.markdown("---")

# --- FORMULAR SETARE BUGETE (FUNCȚIONALITATEA NOUĂ) ---
st.sidebar.header("⚙️ Setează Buget Maxim")
cat_buget = st.sidebar.selectbox("Alege Categoria pentru Limită", Toate_Categoriile_Cheltuieli)
limita_buget = st.sidebar.number_input("Limită maximă lunară (RON)", min_value=1.0, step=50.0, key="lim_bg")

if st.sidebar.button("Configurează Buget"):
    salveaza_buget(cat_buget, limita_buget)
    st.sidebar.success(f"Buget setat pentru {cat_buget}!")
    st.rerun()

st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
if st.sidebar.button("🔴 Șterge Toate Datele", use_container_width=True):
    sterge_toate_datele()
    # Ștergem și fișierul de bugete dacă dăm reset total
    if pd.io.common.os.path.exists("bugete.csv"):
        pd.io.common.os.remove("bugete.csv")
    st.rerun()

# --- GRAFICE INTERACTIVE ---
if not df.empty:
    st.markdown("### 📊 Analiza Vizuală a Bugetului")
    grafic_col1, grafic_col2 = st.columns(2)
    
    with grafic_col1:
        st.subheader("Distribuție pe Categorii de Cheltuieli")
        df_cheltuieli = df[df["Tip"] == "Cheltuială"]
        if not df_cheltuieli.empty:
            fig_pie = px.pie(df_cheltuieli, values="Suma", names="Categorie", title="Unde se duc banii tăi?", hole=0.4, template="plotly_dark")
            st.plotly_chart(fig_pie, use_container_width=True)
            
    with grafic_col2:
        st.subheader("Evoluția Istorică a Tranzacțiilor")
        df_istoric = df.groupby(["Data", "Tip"])["Suma"].sum().reset_index()
        fig_bar = px.bar(df_istoric, x="Data", y="Suma", color="Tip", barmode="group", title="Venituri vs Cheltuieli",
                         template="plotly_dark", color_discrete_map={"Venit": "#238636", "Cheltuială": "#DA3633"})
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("### 🗒️ Istoric Tranzacții Recente")
    st.dataframe(df.sort_index(ascending=False), use_container_width=True)
