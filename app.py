import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Smart BudGet", page_icon="💰", layout="centered")

@st.dialog("Welcome to Smart BudGet!")
def welcome_popup():
    st.write("Guide on how to use the Smart BudGet app")
    st.markdown("""
        * At the corner top left, that is the section where
        you can input your allowance, day, and a fixed bill
        * Type your expenses into the form
        * Track your allowance seamlessly
        """)

    if st.button("Let's Get Started!"):
        st.session_state.welcome_popup = True
        st.rerun()

if "welcome_popup" not in st.session_state:
    st.session_state.welcome_popup = False

if not st.session_state.welcome_popup:
    welcome_popup()

CSV_FILE = "expenses_data.csv"

if os.path.exists(CSV_FILE):
    if "expenses" not in st.session_state:
        st.session_state.expenses = pd.read_csv(CSV_FILE)
else:
    if "expenses" not in st.session_state:
        st.session_state.expenses = pd.DataFrame(columns=["Description", "Amount"])

st.title("💰 Smart BudGet")
st.markdown("Dynamic daily allowance tracking with persistent session state.")

if "balance" not in st.session_state:
    st.session_state.balance = 0.0
if "initial_balance" not in st.session_state:
    st.session_state.initial_balance = 0.0
if "expenses_history" not in st.session_state:
    st.session_state.expenses_history = []

st.sidebar.header("Budget Settings")
input_balance = st.sidebar.number_input("Starting Balance (₱)", value=.0, step=0.0)
total_days = st.sidebar.number_input("Days Until Next Allowance", value=0, step=1)
fixed_bills = st.sidebar.number_input("Upcoming Fixed Bills (₱)", value=0.0, step=0.0)

if input_balance != st.session_state.initial_balance:
    st.session_state.initial_balance = input_balance
    st.session_state.balance = input_balance
    st.session_state.expenses_history = []

days_passed = len(st.session_state.expenses_history)
days_remaining = max(1, total_days - days_passed)
spendable_pool = st.session_state.balance - fixed_bills
daily_limit = max(0.0, spendable_pool / days_remaining)

col1, col2, col3 = st.columns(3)
col1.metric("Current Balance", f"₱{st.session_state.balance:.2f}")
col2.metric("Safe Daily Limit", f"₱{daily_limit:.2f}")
col3.metric("Days Remaining", f"{days_remaining}")

st.divider()

st.subheader("Log Today's Expenses")
with st.form("expense_form", clear_on_submit=True):
    expense_amount = st.number_input("Amount Spent (₱)", min_value=0.0, value=0.0, step=0.50)
    expense_desc = st.text_input("Description (e.g., Coffee, Lunch, Bus fare)")
    added = st.form_submit_button("Add Expense")

if "expenses" not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=["Description", "Amount"])

if added and expense_desc:
    new_data = pd.DataFrame({
        "Description": [expense_desc],
        "Amount": [expense_amount],
    })

    st.session_state.expenses = pd.concat([st.session_state.expenses, new_data], ignore_index=True)

st.subheader("Today's Expenses")
st.dataframe(st.session_state.expenses, use_container_width=True)

total_amount = st.session_state.expenses["Amount"].sum()
st.metric(label="Total Amount", value=f"₱{total_amount:.2f}")

submitted = st.button("Submit")

if submitted:
    if expense_amount > 0:
        st.session_state.balance -= expense_amount

        status = "Under Budget 🟢" if expense_amount <= daily_limit else "Over Budget 🔴"

        st.session_state.expenses_history.append({
            "Day": len(st.session_state.expenses_history) + 1,
            "Total Amount Spent": total_amount,
            "Daily Limit Was": round(daily_limit, 2),
            "Status": status
        })

        history_df = pd.DataFrame(st.session_state.expenses_history)
        history_df.to_csv("history_data.csv", index=False)

        st.session_state.expenses = pd.DataFrame(columns=["Description", "Amount"])
        st.session_state.expenses.to_csv(CSV_FILE, index=False)

        st.success("Day submitted and saved to history successfully!")
        st.rerun()
    else:
        st.warning("Please enter an amount greater than zero.")

if st.session_state.expenses_history:
    st.subheader("📊 Expense History")
    df = pd.DataFrame(st.session_state.expenses_history)
    st.dataframe(df, use_container_width=True)

    st.subheader("Spending Trend")
    st.line_chart(df, x="Day", y="Total Amount Spent")
else:
    st.info("No expenses logged yet. Use the form above to log your first transaction!")
