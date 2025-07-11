import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

DB = "crm.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS eggs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            subscription TEXT NOT NULL,
            egg_type TEXT NOT NULL,
            delivery_day TEXT NOT NULL,
            delivery_time TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def yumurta_ekle(name, price):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO eggs (name, price) VALUES (?, ?)", (name, price))
    conn.commit()
    conn.close()

def uye_ekle(name, subscription, egg_type, delivery_day, delivery_time, phone):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''INSERT INTO members 
        (name, subscription, egg_type, delivery_day, delivery_time, phone)
        VALUES (?, ?, ?, ?, ?, ?)''', 
        (name, subscription, egg_type, delivery_day, delivery_time, phone))
    conn.commit()
    conn.close()

def yumurtalari_getir():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM eggs")
    eggs = c.fetchall()
    conn.close()
    return eggs

def uyeleri_getir():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM members")
    members = c.fetchall()
    conn.close()
    return members

def uye_guncelle(id, name, subscription, egg_type, delivery_day, delivery_time, phone):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''UPDATE members SET name=?, subscription=?, egg_type=?, delivery_day=?, delivery_time=?, phone=? WHERE id=?''',
              (name, subscription, egg_type, delivery_day, delivery_time, phone, id))
    conn.commit()
    conn.close()

def uye_sil(id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DELETE FROM members WHERE id=?", (id,))
    conn.commit()
    conn.close()

def yumurta_guncelle(id, name, price):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("UPDATE eggs SET name=?, price=? WHERE id=?", (name, price, id))
    conn.commit()
    conn.close()

def yumurta_sil(id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DELETE FROM eggs WHERE id=?", (id,))
    conn.commit()
    conn.close()

def bugunun_teslimatlari_getir():
    today = datetime.now().strftime("%A")
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT name, egg_type, delivery_time FROM members WHERE delivery_day=?", (today,))
    deliveries = c.fetchall()
    conn.close()
    return deliveries

def aylik_kazanc_getir():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM members WHERE subscription='Aylık'")
    aylik_uye = c.fetchone()[0]
    c.execute("SELECT price FROM eggs")
    prices = [row[0] for row in c.fetchall()]
    aylik_kazanc = aylik_uye * (prices[0] if prices else 0) * 4  
    conn.close()
    return aylik_kazanc

def gunluk_kazanc_getir():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM members WHERE subscription='Haftalık'")
    haftalik_uye = c.fetchone()[0]
    c.execute("SELECT price FROM eggs")
    prices = [row[0] for row in c.fetchall()]
    gunluk_kazanc = haftalik_uye * (prices[0] if prices else 0) / 7 
    conn.close()
    return gunluk_kazanc

init_db()
st.set_page_config(page_title="Gezen Tavuk Yumurtası CRM", layout="wide")
st.title("Gezen Tavuk Yumurtası Satış CRM")

menu = [
    "Ana Sayfa",
    "Üyelik Ekle",
    "Yumurta Türü Ekle",
    "Üyeler",
    "Yumurtalar",
    "Üye Sil/Düzenle",
    "Yumurta Sil/Düzenle"
]
choice = st.sidebar.selectbox("Sayfa Seç", menu)

if choice == "Ana Sayfa":
    st.header("Ana Sayfa")
    st.subheader("Bugünün Teslimatları")
    deliveries = bugunun_teslimatlari_getir()
    st.table(deliveries)
    st.subheader("Aylık Kazanç")
    st.write(f"{aylik_kazanc_getir():.2f} TL")
    st.subheader("Günlük Kazanç")
    st.write(f"{gunluk_kazanc_getir():.2f} TL")
    st.subheader("Toplam Üye Sayısı")
    st.write(len(uyeleri_getir()))

elif choice == "Üyelik Ekle":
    st.header("Üyelik Ekle")
    eggs = yumurtalari_getir()
    with st.form("add_member_form"):
        name = st.text_input("Üye İsmi")
        subscription = st.selectbox("Abonelik Türü", ["Haftalık", "Aylık"])
        egg_type = st.selectbox("Yumurta Türü", [egg[1] for egg in eggs])
        delivery_day = st.selectbox("Teslimat Günü", ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"])
        delivery_time = st.text_input("Teslimat Saati (örn: 07:45)")
        phone = st.text_input("Telefon Numarası")
        submitted = st.form_submit_button("Ekle")
        if submitted:
            uye_ekle(name, subscription, egg_type, delivery_day, delivery_time, phone)
            st.success("Üye eklendi.")

elif choice == "Yumurta Türü Ekle":
    st.header("Yumurta Türü Ekle")
    with st.form("add_egg_form"):
        name = st.text_input("Yumurta İsmi")
        price = st.number_input("Adet Fiyatı", min_value=0.0, step=0.1)
        submitted = st.form_submit_button("Ekle")
        if submitted:
            yumurta_ekle(name, price)
            st.success("Yumurta türü eklendi.")

elif choice == "Üyeler":
    st.header("Üyeler")
    members = uyeleri_getir()
    df = pd.DataFrame(members, columns=["ID", "İsim", "Abonelik", "Yumurta Türü", "Teslimat Günü", "Teslimat Saati", "Telefon"])
    st.table(df[["İsim", "Abonelik", "Yumurta Türü", "Teslimat Günü", "Teslimat Saati", "Telefon"]])

elif choice == "Yumurtalar":
    st.header("Yumurtalar")
    eggs = yumurtalari_getir()
    df = pd.DataFrame(eggs, columns=["ID", "İsim", "Fiyat"])
    st.table(df[["İsim", "Fiyat"]])


elif choice == "Üye Sil/Düzenle":
    st.header("Üye Sil ve Düzenle")
    members = uyeleri_getir()
    for member in members:
        st.write(f"İsim: {member[1]} / Abonelik: {member[2]} / Yumurta: {member[3]}")
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"{member[1]} Sil"):
                uye_sil(member[0])
                st.success("Üye silindi.")
        with col2:
            if st.button(f"{member[1]} Düzenle"):
                with st.form(f"edit_member_{member[0]}"):
                    name = st.text_input("İsim", member[1])
                    subscription = st.selectbox("Abonelik Türü", ["Haftalık", "Aylık"], index=0 if member[2]=="Haftalık" else 1)
                    egg_type = st.text_input("Yumurta Türü", member[3])
                    delivery_day = st.text_input("Teslimat Günü", member[4])
                    delivery_time = st.text_input("Teslimat Saati", member[5])
                    phone = st.text_input("Telefon", member[6])
                    submitted = st.form_submit_button("Kaydet")
                    if submitted:
                        uye_guncelle(member[0], name, subscription, egg_type, delivery_day, delivery_time, phone)
                        st.success("Üye güncellendi.")

elif choice == "Yumurta Sil/Düzenle":
    st.header("Yumurta Sil ve Düzenle")
    eggs = yumurtalari_getir()
    for egg in eggs:
        with st.form(key=f"form_{egg[0]}"):
            name = st.text_input("Yeni İsim", egg[1], key=f"name_{egg[0]}")
            price = st.number_input("Yeni Fiyat", value=egg[2], step=0.1, key=f"price_{egg[0]}")
            delete_button = st.form_submit_button("Sil")
            save_button = st.form_submit_button("Kaydet")
            if delete_button:
                yumurta_sil(egg[0])
                st.success("Yumurta silindi.")
                st.rerun()
            if save_button:
                yumurta_guncelle(egg[0], name, price)
                st.success("Yumurta güncellendi.")
                st.rerun()