import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Load data
data = pd.read_csv("transactions.csv")

st.title("AI Personal Finance Coach")


st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go to",
    ["Dashboard", "Transactions", "Simulator"]
)



st.sidebar.header("Upload Your Transactions")

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV file",
    type=["csv"]
)

if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)

st.sidebar.header("Add New Expense")

date = st.sidebar.date_input("Date")
description = st.sidebar.text_input("Description")
amount = st.sidebar.number_input("Amount", min_value=0)

if st.sidebar.button("Add Expense"):
    new_row = {
        "Date": date,
        "Description": description,
        "Amount": amount
    }
    data = pd.concat([data, pd.DataFrame([new_row])], ignore_index=True)


monthly_income = 25000  # demo income
total_spent = data["Amount"].sum()
savings = monthly_income - total_spent
savings_rate = (savings / monthly_income) * 100


# Simple AI-like categorization
def categorize(desc):
    desc = desc.lower()
    if "grocery" in desc or "restaurant" in desc:
        return "Food"
    elif "bus" in desc or "uber" in desc:
        return "Transport"
    elif "movie" in desc or "shopping" in desc:
        return "Entertainment"
    elif "bill" in desc or "recharge" in desc:
        return "Utilities"
    else:
        return "Other"

data["Category"] = data["Description"].apply(categorize)

# Budget limits (monthly)
budgets = {
    "Food": 2000,
    "Transport": 800,
    "Entertainment": 1500,
    "Utilities": 1200,
    "Other": 500
}

summary = data.groupby("Category")["Amount"].sum()

# STREAMLIT UI

if page == "Dashboard":
    st.header("Overview")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Income", f"₹{monthly_income}")
    col2.metric("Total Spent", f"₹{total_spent}")
    col3.metric("Savings", f"₹{savings}")
    col4.metric("Savings Rate", f"{savings_rate:.1f}%")
    
    st.subheader("Financial Health Score")

    if savings_rate >= 30:
        st.success("Excellent – Strong savings discipline")
    elif savings_rate >= 20:
        st.info("Good – On track but can optimize")
    elif savings_rate >= 10:
        st.warning("Risk – Low savings, reduce discretionary spend")
    else:
        st.error("Critical – Immediate spending control needed")
    

   

    st.subheader("Spending Summary")
    st.bar_chart(summary)
    st.subheader("Spending Distribution")
    fig, ax = plt.subplots()
    ax.pie(summary, labels=summary.index, autopct="%1.1f%%", startangle=90)
    ax.axis("equal")
    st.pyplot(fig)
    

    st.subheader("Budget Analysis")
    for category, spent in summary.items():
       budget = budgets.get(category, 0)
       if spent > budget:
           st.warning(f"{category}: ₹{spent} spent (Over budget by ₹{spent-budget})")
       else:
           st.success(f"{category}: ₹{spent} spent (Within budget)")
   
    
    st.subheader("AI Recommendations")
    if summary.get("Entertainment", 0) > budgets["Entertainment"]:
        st.write("👉 Reduce entertainment expenses to improve savings.")
    if summary.get("Food", 0) > budgets["Food"]:
        st.write("👉 Consider home-cooked meals to lower food spending.")
    st.write("👉 Set aside at least 20% of monthly income as savings.")

  




elif page == "Transactions":
     st.header("Manage Transactions")
     
     st.subheader("Transaction History")
     st.dataframe(data)




elif page == "Simulator":
    st.header("Scenario Simulator")

    category = st.selectbox("Select category", summary.index)
    adjustment = st.number_input("Reduce spending by (₹)", min_value=0, step=100)

    original_spent = summary[category]
    new_spent = max(original_spent - adjustment, 0)

    new_total_spent = total_spent - adjustment
    new_savings = monthly_income - new_total_spent
    new_savings_rate = (new_savings / monthly_income) * 100

    st.metric("New Savings", f"₹{new_savings}")
    st.metric("New Savings Rate", f"{new_savings_rate:.1f}%")

    if new_savings_rate >= savings_rate:
        st.success("This change improves your financial health 👍")

    st.subheader("Goal-Based Planning")

    goal_amount = st.number_input("Target Savings (₹)", value=50000)
    months = st.number_input("Time Horizon (months)", value=12)

    required_monthly = goal_amount / months

    st.write(f"You need to save ₹{required_monthly:.0f} per month.")

    if savings >= required_monthly:
        st.success("You are on track to reach your goal 🎯")
    else:
        st.warning("Increase savings or extend your timeline")

