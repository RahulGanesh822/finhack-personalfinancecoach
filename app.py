import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Load data
data = pd.read_csv("transactions.csv")
category_budgets = {}
total_budget = 0

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

st.sidebar.header("Monthly Budget Settings")

overall_budget = st.sidebar.number_input(
    "Overall Monthly Budget (₹)",
    min_value=0,
    value=20000,
    step=500
)

if not data.empty:
    summary = data.groupby("Category")["Amount"].sum()

    st.sidebar.subheader("Category Budgets")
    category_budgets = {}

    default_cat_budget = (
        int(overall_budget / len(summary)) if len(summary) > 0 else 0
    )

    for category in summary.index:
        category_budgets[category] = st.sidebar.number_input(
            f"{category} Budget (₹)",
            min_value=0,
            value=default_cat_budget,
            step=500,
            key=f"budget_{category}"
        )

    total_budget = sum(category_budgets.values())


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
overspent_amount = max(0, total_spent - total_budget)



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

    # ------------------------
    # Metrics
    # ------------------------
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Income", f"₹{monthly_income}")
    col2.metric("Total Spent", f"₹{total_spent}")
    col3.metric("Savings", f"₹{savings}")
    col4.metric("Savings Rate", f"{savings_rate:.1f}%")

    # ------------------------
    # Multi-Factor Financial Health Score
    # ------------------------
    # Budget adherence
    total_budget = sum(category_budgets.values())
    overspend_ratio = (total_spent - total_budget) / total_budget

    overspent_amount = max(0, total_spent - total_budget)
    overspend_ratio = overspent_amount / total_budget if total_budget > 0 else 0

    if overspend_ratio == 0:
        budget_score = 1
    elif overspend_ratio <= 0.1:
        budget_score = 0.7
    elif overspend_ratio <= 0.25:
        budget_score = 0.4
    else:
        budget_score = 0.1


    # Emergency fund coverage
    recommended_emergency = 3 * total_spent  # 3 months of expenses
    emergency_score = min(savings / recommended_emergency, 1)

    # Debt ratio (set 1 if no debt for now)
    debt_score = 0.5

    # Savings rate score
    savings_score = savings / monthly_income

    # Weighted health score (0-100)
    health_score = (0.4*savings_score + 0.3*budget_score + 0.2*emergency_score + 0.1*debt_score) * 100

    # Display score with colored feedback
    if health_score >= 75:
        st.success(f"{health_score:.0f} – Excellent")
    elif health_score >= 55:
        st.info(f"{health_score:.0f} – Fair")
    elif health_score >= 35:
        st.warning(f"{health_score:.0f} – Poor")
    else:
        st.error(f"{health_score:.0f} – Critical")

   

    st.subheader("Spending Summary")
    st.bar_chart(summary)
    st.subheader("Spending Distribution")
    fig, ax = plt.subplots()
    ax.pie(summary, labels=summary.index, autopct="%1.1f%%", startangle=90)
    ax.axis("equal")
    st.pyplot(fig)
    summary = data.groupby("Category")["Amount"].sum()
    st.sidebar.header("Monthly Budget Settings")

    overall_budget = st.sidebar.number_input(
     "Overall Monthly Budget (₹)",
    min_value=0,
    value=20000,
    step=500,
    key="overall_budget"
  )

    st.sidebar.subheader("Category Budgets")

    category_budgets = {}
    default_cat_budget = int(overall_budget / len(summary)) if len(summary) > 0 else 0

        
    st.subheader("Budget Analysis")
    for category, spent in summary.items():
       budget = budgets.get(category, 0)
       if spent > budget:
           st.warning(f"{category}: ₹{spent} spent (Over budget by ₹{spent-budget})")
       else:
           st.success(f"{category}: ₹{spent} spent (Within budget)")
   
    
    st.subheader("Recommendations")
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

