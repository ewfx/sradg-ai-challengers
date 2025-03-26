# main.py
import streamlit as st
import pandas as pd
from database import create_database, insert_historical_data, fetch_data
from reconciliation import detect_tolerance_breaches
from reasoning import analyze_mismatch

st.set_page_config(page_title="Trading Reconciliation Agent", layout="wide")

def main():
    st.title("Trading Reconciliation Agent")
    
    # Create database (and table) if not already created
    create_database()
    
    # File uploader to allow CSV input
    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write("### Uploaded Data:")
        st.dataframe(df)
        # Insert CSV data into the database
        insert_historical_data(df)
    
    # Header and display for all trades
    st.header("All Trades")
    trade_data = fetch_data()
    if trade_data:
        # Convert list of tuples into a DataFrame
        # Adjust the columns list based on your table schema.
        df_trades = pd.DataFrame(trade_data, columns=["id", "riskdate", "quantity_a", "quantity_b", "tolerance", "comment", "embedding"])
        st.dataframe(df_trades)
    else:
        st.warning("⚠️ No trade data found!")
    
    # Detect mismatches based on tolerance criteria
    st.header("Detected Breaks")
    mismatches = detect_tolerance_breaches()  # This function should query the database and return a list of dicts
    if mismatches:
        for i, mismatch in enumerate(mismatches):
            # Create a unique key for each analysis button using the riskdate and loop index.
            unique_key = f"analyze-{mismatch['riskdate']}-{i}"
            st.write(
                f"⚠️ Trade on {mismatch['riskdate']} - "
                f"Expected: {mismatch['expected']}, Actual: {mismatch['actual']}, "
                f"Tolerance: {mismatch['tolerance']}, Comment: {mismatch['comment']}"
            )
            if st.button("Analyze Trade", key=unique_key):
                reasoning_result = analyze_mismatch(
                    mismatch["riskdate"],
                    mismatch["expected"],
                    mismatch["actual"],
                    mismatch["tolerance"],
                    mismatch["comment"]
                )
                st.write("### LLM Analysis:")
                st.write(reasoning_result)
    else:
        st.success("No tolerance breaches detected!")

if __name__ == "__main__":
    main()

