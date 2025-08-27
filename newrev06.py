import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# ---------- DATABASE ----------
conn = sqlite3.connect("finance.db", check_same_thread=False)
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY, 
                password TEXT)""")
c.execute("""CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                date TEXT,
                income REAL,
                expense REAL,
                saving REAL)""")
conn.commit()

# ---------- CUSTOM STYLE ----------
def add_custom_css():
    st.markdown(
        """
        <style>
        /* 🌈 พื้นหลัง */
        .stApp {
            background: linear-gradient(135deg, #fceabb 0%, #f8b500 100%);
        }

        /* 🎨 หัวข้อ */
        h1, h2, h3, .stMarkdown {
            color: #2c003e;
        }

        /* 💖 ปุ่ม */
        div.stButton > button {
            background-color: #ff4b5c;
            color: white;
            border-radius: 12px;
            height: 3em;
            width: 100%;
            border: none;
            font-weight: bold;
        }
        div.stButton > button:hover {
            background-color: #d63384;
            color: #fff;
        }

        /* 💳 การ์ดสรุป */
        .metric-card {
            background: white;
            padding: 15px;
            border-radius: 15px;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.15);
            margin-bottom: 10px;
            font-size: 18px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# ---------- REGISTER / LOGIN ----------
def register_user(username, password):
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except:
        return False

def login_user(username, password):
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    return c.fetchone()

# ---------- APP ----------
def main():
    add_custom_css()
    st.title("💸 แอพรายรับรายจ่าย (สดใสเวอร์ชั่น)")

    menu = ["🔑 Login", "📝 SignUp"]
    choice = st.sidebar.selectbox("เมนู", menu)

    if choice == "📝 SignUp":
        st.subheader("สร้างบัญชีใหม่")
        new_user = st.text_input("ชื่อผู้ใช้")
        new_pass = st.text_input("รหัสผ่าน", type="password")
        if st.button("สร้างบัญชี"):
            if register_user(new_user, new_pass):
                st.success("✅ สร้างบัญชีสำเร็จ! ไปหน้า Login ได้เลย")
            else:
                st.error("⚠️ ชื่อผู้ใช้นี้ถูกใช้แล้ว")

    elif choice == "🔑 Login":
        st.subheader("เข้าสู่ระบบ")
        username = st.text_input("ชื่อผู้ใช้")
        password = st.text_input("รหัสผ่าน", type="password")
        if st.button("เข้าสู่ระบบ"):
            user = login_user(username, password)
            if user:
                st.success(f"ยินดีต้อนรับ {username} 🎉")
                app_dashboard(username)
            else:
                st.error("❌ ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")

# ---------- DASHBOARD ----------
def app_dashboard(username):
    st.header("📊 สรุปรายรับ-รายจ่าย")

    today = datetime.now().strftime("%Y-%m-%d")

    # --- Input ---
    st.subheader("➕ เพิ่มข้อมูลวันนี้")
    income = st.number_input("💰 รายรับ", min_value=0.0, step=100.0)
    expense = st.number_input("📉 รายจ่าย", min_value=0.0, step=100.0)
    saving = st.number_input("🏦 เงินเก็บ", min_value=0.0, step=100.0)

    if st.button("บันทึกข้อมูล"):
        c.execute("INSERT INTO records (username, date, income, expense, saving) VALUES (?, ?, ?, ?, ?)",
                  (username, today, income, expense, saving))
        conn.commit()
        st.success("✅ บันทึกเรียบร้อยแล้ว")

    # --- Summary Data ---
    df = pd.read_sql("SELECT * FROM records WHERE username=?", conn, params=(username,))
    if not df.empty:
        today_data = df[df["date"] == today]
        total_income_today = today_data["income"].sum()
        total_expense_today = today_data["expense"].sum()
        total_saving_today = today_data["saving"].sum()
        balance_today = total_income_today - total_expense_today - total_saving_today

        st.markdown(f'<div class="metric-card">💰 รายรับวันนี้: {total_income_today} บาท</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-card">📉 รายจ่ายวันนี้: {total_expense_today} บาท</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-card">🏦 เงินเก็บวันนี้: {total_saving_today} บาท</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-card">✅ คงเหลือวันนี้: {balance_today} บาท</div>', unsafe_allow_html=True)

        # --- Chart ---
        st.subheader("📈 กราฟสรุปวันนี้")
        fig, ax = plt.subplots()
        colors = ["#FF6F91", "#FF9671", "#FFC75F", "#F9F871"]
        ax.bar(["รายรับ", "รายจ่าย", "เงินเก็บ", "คงเหลือ"],
               [total_income_today, total_expense_today, total_saving_today, balance_today],
               color=colors)
        st.pyplot(fig)

if __name__ == "__main__":
    main()
