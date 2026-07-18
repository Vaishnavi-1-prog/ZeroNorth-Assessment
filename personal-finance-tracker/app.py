import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
import database as db

db.init_db()

st.set_page_config(page_title="Personal Finance Tracker", layout="wide")
st.title("💰 Personal Finance Tracker")

tab1, tab2, tab3, tab4 = st.tabs(["Add Transaction", "Dashboard", "Search & Filter", "Insights"])

CATEGORIES = {
    "Income": ["Salary", "Freelance", "Investment", "Other"],
    "Expense": ["Rent", "Groceries", "Transport", "Entertainment", "Utilities", "Health", "Other"],
    "Savings": ["Fixed Deposit", "Mutual Fund", "Emergency Fund", "Child Care","Other"]
}

# ---------- Add Transaction ----------
with tab1:
    st.subheader("Add a Transaction")
    col1, col2 = st.columns(2)
    with col1:
        t_date = st.date_input("Date", value=date.today())
        t_type = st.selectbox("Type", ["Income", "Expense", "Savings"])
    with col2:
        t_category = st.selectbox("Category", CATEGORIES[t_type])
        t_amount = st.number_input("Amount", min_value=0.0, step=100.0)
    t_note = st.text_input("Note (optional)")

    if st.button("Add Transaction"):
        if t_amount > 0:
            db.add_transaction(str(t_date), t_type, t_category, t_amount, t_note)
            st.success("Transaction added!")
            st.rerun()
        else:
            st.warning("Amount must be greater than 0")

# ---------- Load data once for other tabs ----------
rows = db.get_all_transactions()
df = pd.DataFrame(rows, columns=["id", "date", "type", "category", "amount", "note"])
if not df.empty:
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)

# ---------- Dashboard ----------
with tab2:
    st.subheader("Monthly Summary")
    if df.empty:
        st.info("No transactions yet.")
    else:
        income = df[df["type"] == "Income"]["amount"].sum()
        expense = df[df["type"] == "Expense"]["amount"].sum()
        savings = df[df["type"] == "Savings"]["amount"].sum()
        balance = income - expense - savings

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Income", f"₹{income:,.0f}")
        c2.metric("Total Expense", f"₹{expense:,.0f}")
        c3.metric("Total Savings", f"₹{savings:,.0f}")
        c4.metric("Balance", f"₹{balance:,.0f}")

        monthly = df.groupby(["month", "type"])["amount"].sum().reset_index()
        fig1 = px.bar(monthly, x="month", y="amount", color="type", barmode="group",
                       title="Income vs Expense by Month")
        st.plotly_chart(fig1, use_container_width=True)

        exp_by_cat = df[df["type"] == "Expense"].groupby("category")["amount"].sum().reset_index()
        if not exp_by_cat.empty:
            fig2 = px.pie(exp_by_cat, names="category", values="amount", title="Expenses by Category")
            st.plotly_chart(fig2, use_container_width=True)
# ---------- Search & Filter ----------
with tab3:
    st.subheader("Search & Filter Transactions")
    if df.empty:
        st.info("No transactions yet.")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            f_type = st.multiselect("Type", df["type"].unique(), default=list(df["type"].unique()))
        with col2:
            f_category = st.multiselect("Category", df["category"].unique(), default=list(df["category"].unique()))
        with col3:
            f_search = st.text_input("Search note")

        filtered = df[df["type"].isin(f_type) & df["category"].isin(f_category)]
        if f_search:
            filtered = filtered[filtered["note"].str.contains(f_search, case=False, na=False)]

        st.dataframe(filtered[["id", "date", "type", "category", "amount", "note"]], use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            del_id = st.number_input("Enter ID to delete", min_value=0, step=1)
            if st.button("Delete Transaction"):
                db.delete_transaction(del_id)
                st.success(f"Deleted transaction {del_id}")
                st.rerun()
        with col2:
            st.write("")
            st.write("")
            if st.button("🗑️ Delete All Transactions"):
                db.delete_all_transactions()
                st.success("All transactions deleted")
                st.rerun()

        st.subheader("Update a Transaction")
        edit_id = st.number_input("Enter ID to update", min_value=0, step=1, key="edit_id")
        match = df[df["id"] == edit_id]
        if not match.empty:
            row = match.iloc[0]
            e_date = st.date_input("New Date", value=row["date"], key="e_date")
            e_type = st.selectbox("New Type", ["Income", "Expense", "Savings"],
                                   index=["Income", "Expense", "Savings"].index(row["type"]), key="e_type")
            e_category = st.selectbox("New Category", CATEGORIES[e_type], key="e_category")
            e_amount = st.number_input("New Amount", min_value=0.0, step=100.0, value=float(row["amount"]), key="e_amount")
            e_note = st.text_input("New Note", value=row["note"] or "", key="e_note")

            if st.button("Update Transaction"):
                db.update_transaction(edit_id, str(e_date), e_type, e_category, e_amount, e_note)
                st.success(f"Updated transaction {edit_id}")
                st.rerun()
        elif edit_id != 0:
            st.warning("No transaction with that ID")

# ---------- Insights ----------
with tab4:
    st.subheader("AI Spending Insights")
    if df.empty:
        st.info("No transactions yet.")
    else:
        exp = df[df["type"] == "Expense"]
        if not exp.empty:
            top_cat = exp.groupby("category")["amount"].sum().idxmax()
            top_amt = exp.groupby("category")["amount"].sum().max()
            st.write(f"📌 Your highest spending category is **{top_cat}** (₹{top_amt:,.0f} total).")

            monthly_exp = exp.groupby("month")["amount"].sum()
            if len(monthly_exp) >= 2:
                change = monthly_exp.iloc[-1] - monthly_exp.iloc[-2]
                trend = "increased 📈" if change > 0 else "decreased 📉"
                st.write(f"📌 Your spending {trend} by ₹{abs(change):,.0f} compared to last month.")

            st.subheader("Next Month's Expense Prediction")
            avg_expense = monthly_exp.mean()
            st.write(f"Based on your average monthly spending, next month's expense is predicted to be **₹{avg_expense:,.0f}**.")
        else:
            st.info("Add some expenses to see insights.")
