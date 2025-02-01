import streamlit as st
import pandas as pd
import io

# Function to perform word-level analysis on the keywords
def analyze_words(keywords, combined_text):
    # For each keyword, split into individual words and join them with a comma for display
    keywords_with_words = {phrase: ", ".join(phrase.split()) for phrase in keywords}

    # Normalize the combined text (handling patterns like "english,american,")
    combined_normalized = [word.strip().lower() for word in combined_text.replace(",", " ").split() if word.strip()]

    # Build the analysis: for each phrase, list its words and append those not found in the combined list
    results = {
        phrase: {
            "Split Words": keywords_with_words[phrase],
            "Status": ",".join([word for word in phrase.split() if word.lower() not in combined_normalized])
        }
        for phrase in keywords_with_words
    }

    # Convert the results dictionary into a DataFrame for display
    results_df = pd.DataFrame([
        {"Phrase": phrase,
         "Split Words": data["Split Words"],
         "Status": data["Status"]}
        for phrase, data in results.items()
    ])

    return results_df

# Function to update/normalize the Difficulty column
def update_difficulty(diff):
    try:
        diff = float(diff)
    except:
        return None
    if 0 <= diff <= 10:
        return 0.4
    elif 11 <= diff <= 20:
        return 1
    elif 21 <= diff <= 30:
        return 2
    elif 31 <= diff <= 40:
        return 4
    elif 61 < diff <= 70:
        return 8
    elif 71 < diff <= 100:
        return 12
    else:
        return 1.0

# Function to update/normalize the Rank column.
# If rank is empty or null, we assign 250 before applying normalization rules.
def update_rank(rank):
    try:
        rank = float(rank)
    except:
        rank = 250.0  # Assign 250 if conversion fails or rank is empty/null

    if 1 <= rank <= 10:
        return 4
    elif 11 <= rank <= 30:
        return 3
    elif 31 <= rank <= 249:
        return 2
    else:
        return 1

# Function to update/normalize the Results column into a Calculated Result
def update_result(res):
    try:
        res = float(res)
    except:
        return 1
    if 1 <= res <= 50:
        return 3
    elif 51 <= res <= 100:
        return 2
    elif 101 <= res <= 249:
        return 1.5
    else:
        return 1

# Function to calculate the Final Score based on the formula:
# (Volume / Normalized Difficulty) * Normalized Rank * Calculated Result
def calculate_final_score(row):
    try:
        volume = float(row["Volume"])
    except:
        volume = 0
    nd = row["Normalized Difficulty"]
    nr = row["Normalized Rank"]
    cr = row["Calculated Result"]
    try:
        final_score = (volume / nd) * nr * cr
    except Exception:
        final_score = 0
    return final_score

st.title("Word Presence Analysis with Normalized Columns and Final Score")

st.write(
    """
    ### Instructions
    1. **Paste your table data (Excel format):**  
       Copy and paste your Excel table data (typically tab-separated) into the text area below.  
       The table must contain the following columns:  
       `Keyword, Volume, Difficulty, Chance, KEI, Results, Rank`
    2. **Provide the word lists in the three fields below:**  
       - **First Field:** (Max 30 characters)  
       - **Second Field:** (Max 30 characters)  
       - **Third Field:** (Comma or space-separated, Max 100 characters)  
       All words from these three fields will be combined for analysis.
    """
)

# Text area for copy-pasting the table data (Excel-style, tab-separated)
table_input = st.text_area("Paste your Excel table data", height=200)

# Three separate text fields for word lists
first_field  = st.text_input("Enter first text (max 30 characters)", max_chars=30)
second_field = st.text_input("Enter second text (max 30 characters)", max_chars=30)
third_field  = st.text_input("Enter third text (comma or space-separated, max 100 characters)", max_chars=100)

# Combine the three fields into one string for analysis
combined_text = f"{first_field} {second_field} {third_field}".strip()

if table_input and combined_text:
    try:
        table_io = io.StringIO(table_input)
        # Read the pasted table as TSV (Excel copy-paste is typically tab-separated)
        df_table = pd.read_csv(table_io, sep="\t")
    except Exception as e:
        st.error(f"Error reading table data: {e}")
        st.stop()

    # Required columns for the table
    required_columns = ["Keyword", "Volume", "Difficulty", "Chance", "KEI", "Results", "Rank"]

    if not all(col in df_table.columns for col in required_columns):
        st.error(f"The pasted table must contain the following columns: {', '.join(required_columns)}")
    else:
        # Create new columns for Normalized Difficulty, Normalized Rank, and Calculated Result
        df_table["Normalized Difficulty"] = df_table["Difficulty"].apply(update_difficulty)
        df_table["Normalized Rank"] = df_table["Rank"].apply(update_rank)
        df_table["Calculated Result"] = df_table["Results"].apply(update_result)
        
        # Calculate the Final Score column
        df_table["Final Score"] = df_table.apply(calculate_final_score, axis=1)
        
        # Remove the Chance and KEI columns
        df_table = df_table.drop(columns=["Chance", "KEI"])
        
        # Sort the DataFrame by Final Score in descending order
        df_table = df_table.sort_values(by="Final Score", ascending=False)
        
        st.write("### Table Preview (with Normalized Columns)")
        st.dataframe(df_table)

        # Extract the list of keywords from the table
        keywords = df_table["Keyword"].dropna().tolist()

        # Display the combined text (for debugging/information)
        st.write(f"### Combined Word List: {combined_text}")
        
        # Perform the word analysis using the combined text
        analysis_df = analyze_words(keywords, combined_text)

        st.write("### Analysis Results")
        st.dataframe(analysis_df)

        # Download button for the analysis results CSV
        st.download_button(
            label="Download Analysis Results as CSV",
            data=analysis_df.to_csv(index=False, encoding="utf-8"),
            file_name="word_presence_analysis.csv",
            mime="text/csv"
        )
else:
    st.write("Please paste your table data and provide input in the three word fields to proceed.")
