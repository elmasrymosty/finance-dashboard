import pandas as pd
import os

FILE_PATH = "date_financiare.csv"
BUGET_FILE_PATH = "bugete.csv"

# --- LOGICĂ TRANZACȚII ---

def initializeaza_baza_de_date():
    """Creează fișierul CSV cu coloanele necesare dacă nu există deja"""
    if not os.path.exists(FILE_PATH):
        df = pd.DataFrame(columns=["Data", "Tip", "Categorie", "Suma", "Descriere"])
        df.to_csv(FILE_PATH, index=False)

def incarca_tranzactii():
    """Citește tranzacțiile din fișierul CSV"""
    initializeaza_baza_de_date()
    return pd.read_csv(FILE_PATH)

def adauga_tranzactie(data, tip, categorie, suma, descriere):
    """Adaugă o nouă linie în fișierul CSV"""
    df = incarca_tranzactii()
    
    noua_linie = {
        "Data": str(data),
        "Tip": tip,          
        "Categorie": categorie,
        "Suma": float(suma),
        "Descriere": descriere
    }
    
    df = pd.concat([df, pd.DataFrame([noua_linie])], ignore_index=True)
    df.to_csv(FILE_PATH, index=False)

def sterge_toate_datele():
    """Golește complet fișierul CSV"""
    df = pd.DataFrame(columns=["Data", "Tip", "Categorie", "Suma", "Descriere"])
    df.to_csv(FILE_PATH, index=False)


# --- LOGICĂ BUGETE MAXIME ---

def initializeaza_bugete():
    """Creează fișierul CSV pentru bugete dacă nu există"""
    if not os.path.exists(BUGET_FILE_PATH):
        df = pd.DataFrame(columns=["Categorie", "Limita"])
        df.to_csv(BUGET_FILE_PATH, index=False)

def incarca_bugete():
    """Citește bugetele din fișierul CSV și le returnează ca dicționar"""
    initializeaza_bugete()
    df = pd.read_csv(BUGET_FILE_PATH)
    return dict(zip(df["Categorie"], df["Limita"]))

def salveaza_buget(categorie, limita):
    """Adaugă sau actualizează limita de buget pentru o categorie"""
    initializeaza_bugete()
    df = pd.read_csv(BUGET_FILE_PATH)
    
    # Ștergem limita veche dacă exista deja pentru această categorie
    df = df[df["Categorie"] != categorie]
    
    # Adăugăm noua limită
    noua_linie = {"Categorie": categorie, "Limita": float(limita)}
    df = pd.concat([df, pd.DataFrame([noua_linie])], ignore_index=True)
    df.to_csv(BUGET_FILE_PATH, index=False)
