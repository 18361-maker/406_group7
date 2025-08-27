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
# Custom CSS (พาสเทล)
# -------------------------
st.markdown("""
    <style>
        body {background-color: #f8f4f9;}
        .main {background-color: #ffffff;}
        h1, h2, h3 {color: #d63384;}
        .stButton>button {
            background-color: #FFB6C1; /* ชมพูพาสเทล */
            color: #333;
            border-radius: 10px;
            border: none;
            padding: 0.5em 1em;
        }
        .stButton>button:hover {
            background-color: #FFFDD0; /* เหลืองพาสเทล */
            color: #000;
        }
        .stTabs [role="tab"] {
            background-color: #f4d6e7;
            color: #333;
            border-radius: 8px;
            padding: 0.3em 1em;
        }
        .stTabs [role="tab"][aria-selected="true"] {
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
        st.caption("ℹ️ โปรดคลิกปุ่ม 2 รอบหากไม่รีเฟรชอัตโนมัติ")

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

    # -------------------
    # เมื่อวาน
    # -------------------
    records_y = st.session_state["records"].get(username, {}).get(str(yesterday), {"income": [], "expense": []})
    total_income_y = sum([r["amount"] for r in records_y["income"]])
    total_expense_y = sum([r["amount"] for r in records_y["expense"]])
    saving_y = total_income_y * 0.3
    balance_y = total_income_y * 0.7 - total_expense_y

    # -------------------
    # วันนี้
    # -------------------
    st.markdown("---")
    records_t = st.session_state["records"].get(username, {}).get(str(today), {"income": [], "expense": []})
    total_income_t = sum([r["amount"] for r in records_t["income"]])
    total_expense_t = sum([r["amount"] for r in records_t["expense"]])
    saving_t = total_income_t * 0.3
    balance_t = total_income_t * 0.7 - total_expense_t

    st.subheader("📅 วันนี้")

    # 👉 เพิ่มกราฟวันนี้
    fig, ax = plt.subplots()
    ax.bar(["Income", "Expense"], [total_income_t, total_expense_t], color=["#FFB6C1", "#999999"])
    st.pyplot(fig)

    st.write(f"💰 รายรับ: {total_income_t}")
    st.write(f"📉 รายจ่าย: {total_expense_t}")
    st.write(f"🏦 เงินเก็บ (30%): {saving_t}")
    st.write(f"✅ คงเหลือจากเงินใช้จ่าย: {balance_t}")

    
    st.subheader("📅 เมื่อวาน")
    fig, ax = plt.subplots()
    ax.bar(["Income", "Expense"], [total_income_y, total_expense_y], color=["#FFB6C1", "#999999"])
    st.pyplot(fig)
    
    st.write(f"💰 รายรับ: {total_income_y}")
    st.write(f"📉 รายจ่าย: {total_expense_y}")
    st.write(f"🏦 เงินเก็บ (30%): {saving_y}")
    st.write(f"✅ คงเหลือจากเงินใช้จ่าย: {balance_y}")

    # -------------------
    # ปุ่มเพิ่มข้อมูล
    # -------------------
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("+ รายรับ"):
            st.session_state["page"] = "add_income"
    with col2:
        if st.button("- รายจ่าย"):
            st.session_state["page"] = "add_expense"
    st.caption("ℹ️ โปรดคลิกปุ่ม 2 รอบหากไม่รีเฟรชอัตโนมัติ")

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
    st.caption("ℹ️ โปรดคลิกปุ่ม 2 รอบหากไม่รีเฟรชอัตโนมัติ")
    st.caption("ℹ️ หมายเหตุ ไม่ต้องใส่เครื่องหมายจุลภาค ( , )")

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
    st.caption("ℹ️ โปรดคลิกปุ่ม 2 รอบหากไม่รีเฟรชอัตโนมัติ")
    st.caption("ℹ️ หมายเหตุ ไม่ต้องใส่เครื่องหมายจุลภาค ( , )")

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
