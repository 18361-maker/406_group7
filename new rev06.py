import streamlit as st
import matplotlib.pyplot as plt
import datetime
import json
import os

DATA_FILE = "data.json"

# -------------------------
# Functions for storage
# -------------------------
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"users": {}, "records": {}}

def save_data():
    data = {
        "users": st.session_state["users"],
        "records": st.session_state["records"]
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# -------------------------
# Initialize session state
# -------------------------
if "loaded" not in st.session_state:
    data = load_data()
    st.session_state["users"] = data.get("users", {})
    st.session_state["records"] = data.get("records", {})
    st.session_state["current_user"] = None
    st.session_state["page"] = "login"
    st.session_state["loaded"] = True

# -------------------------
# Custom CSS
# -------------------------
st.markdown("""
    <style>
        body {background-color: #f8f4f9;}
        .main {background-color: #ffffff;}
        h1, h2, h3 {color: #d63384;}
        .stButton>button {
            background-color: #f4d6e7;
            color: #333;
            border-radius: 10px;
            border: none;
            padding: 0.5em 1em;
        }
        .stButton>button:hover {
            background-color: #d63384;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------------
# Pages
# -------------------------
def login_page():
    st.title("🔐 Login")
    tab1, tab2 = st.tabs(["เข้าสู่ระบบ", "สร้างบัญชี"])
    
    with tab1:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            if username in st.session_state["users"] and st.session_state["users"][username] == password:
                st.session_state["current_user"] = username
                st.session_state["page"] = "dashboard"
                st.success("เข้าสู่ระบบสำเร็จ ✅")
            else:
                st.error("Username หรือ Password ไม่ถูกต้อง ❌")

    with tab2:
        new_user = st.text_input("New Username", key="new_user")
        new_pass = st.text_input("New Password", type="password", key="new_pass")
        if st.button("Sign Up"):
            if new_user in st.session_state["users"]:
                st.error("Username นี้มีอยู่แล้ว ❌")
            else:
                st.session_state["users"][new_user] = new_pass
                save_data()
                st.success("สร้างบัญชีสำเร็จ 🎉")

def dashboard_page():
    st.title("📊 สรุปรายรับ-รายจ่าย")
    
    if st.button("🚪 Logout"):
        st.session_state["current_user"] = None
        st.session_state["page"] = "login"
        st.experimental_rerun()
    
    username = st.session_state["current_user"]
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    
    records = st.session_state["records"].get(username, {}).get(str(yesterday), {"income": [], "expense": []})
    total_income = sum([r["amount"] for r in records["income"]])
    total_expense = sum([r["amount"] for r in records["expense"]])
    
    saving = total_income * 0.3
    usable = total_income * 0.7
    balance = usable - total_expense
    
    # กราฟ
    fig, ax = plt.subplots()
    ax.bar(["รายรับ", "รายจ่าย"], [total_income, total_expense], color=["#d63384", "#999999"])
    st.pyplot(fig)
    
    # สรุป
    st.subheader("สรุปเมื่อวาน")
    st.write(f"💰 รายรับ: {total_income}")
    st.write(f"📉 รายจ่าย: {total_expense}")
    st.write(f"🏦 เงินเก็บ (30%): {saving}")
    st.write(f"✅ คงเหลือจากเงินใช้จ่าย: {balance}")
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("+ รายรับ"):
            st.session_state["page"] = "add_income"
    with col2:
        if st.button("- รายจ่าย"):
            st.session_state["page"] = "add_expense"

def add_income_page():
    st.title("➕ บันทึกรายรับ")
    username = st.session_state["current_user"]
    today = str(datetime.date.today())
    
    income_type = st.selectbox("ประเภท", ["เงินเดือน", "โบนัส", "อื่น ๆ"])
    amount = st.number_input("จำนวนเงิน", min_value=0)
    note = st.text_area("บันทึกเพิ่มเติม (ไม่บังคับ)")
    
    if st.button("บันทึก"):
        if username not in st.session_state["records"]:
            st.session_state["records"][username] = {}
        if today not in st.session_state["records"][username]:
            st.session_state["records"][username][today] = {"income": [], "expense": []}
        st.session_state["records"][username][today]["income"].append({"type": income_type, "amount": amount, "note": note})
        save_data()
        st.success("บันทึกสำเร็จ ✅")
        st.session_state["page"] = "dashboard"

def add_expense_page():
    st.title("➖ บันทึกรายจ่าย")
    username = st.session_state["current_user"]
    today = str(datetime.date.today())
    
    expense_type = st.selectbox("ประเภท", ["ค่าอาหาร", "ค่าเดินทาง", "ค่าน้ำ", "ค่าไฟ", "อื่น ๆ"])
    amount = st.number_input("จำนวนเงิน", min_value=0)
    note = st.text_area("บันทึกเพิ่มเติม (ไม่บังคับ)")
    
    if st.button("บันทึก"):
        if username not in st.session_state["records"]:
            st.session_state["records"][username] = {}
        if today not in st.session_state["records"][username]:
            st.session_state["records"][username][today] = {"income": [], "expense": []}
        st.session_state["records"][username][today]["expense"].append({"type": expense_type, "amount": amount, "note": note})
        save_data()
        st.success("บันทึกสำเร็จ ✅")
        st.session_state["page"] = "dashboard"

# -------------------------
# Navigation
# -------------------------
if st.session_state["current_user"] is None:
    login_page()
else:
    if st.session_state["page"] == "dashboard":
        dashboard_page()
    elif st.session_state["page"] == "add_income":
        add_income_page()
    elif st.session_state["page"] == "add_expense":
        add_expense_page()
    else:
        st.session_state["page"] = "dashboard"
        dashboard_page()
