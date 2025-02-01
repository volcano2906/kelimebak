import streamlit as st
import pandas as pd
import io

# Function to update/normalize Difficulty based on the provided rules
def update_difficulity(diff):
    try:
        diff = float(diff)
    except:
        return diff  # If conversion fails, return original value
    if diff >= 0 and diff <= 20: 
        return 1
    elif diff >= 21 and diff <= 30: 
        return 2
    elif diff > 31 and diff <= 40: 
        return 4
    elif diff > 61 and diff <= 70:
        return 8 
    elif diff > 71 and diff <= 100:
        return 12 
    else:
        return 1.0

# Function to perform word-level analysis on the keywords
def analyze_words(keywords, list2):
    # For each keyword, split into individual words and join them with a comma for display
    keywords_with_words = {phrase: ", ".join(phrase.split()) for phrase in keywords}
    
    # Normalize the second list (handles patterns like "english,american,")
    list2_normalized = [word.strip().lower() for word in list2.replace(",", " ").split() if word.strip()]
    
    # Build the analysis: for each keyword, list its words and append those not in the normalized list
    results = {
        phrase: {
            "Split Words": keywords_with_words[phrase],
            "Status": ",".join([word for word in phrase.split() if word.lower() not in list2_normalized])
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

st.title("Word Presence Analysis and Difficulty Normalization")

st.write(
    """
    ### Instructions
    1. **Paste your table data (Excel format):**  
       Copy and paste your Excel table data (typically tab-separated) into the text area below.  
       The table must contain the following columns:  
       `Keyword, Volume, Difficulty, Chance, KEI, Results, Rank`
    2. **Enter the second list:**  
       Provide a string of words (separated by commas or spaces) to be used in the word analysis.
    """
)

# Text area for paste of Excel table data (expected to be tab-separated)
table_input = st.text_area("Paste your Excel table data", height=200)

# Text area for the second list of words
list2_input = st.text_area("Enter the second list (comma or space-separated)", height=100)

if table_input and list2_input:
    # Attempt to read the pasted table as TSV
    try:
        table_io = io.StringIO(table_input)
        df_table = pd.read_csv(table_io, sep="\t")
    except Exception as e:
        st.error(f"Error reading table data: {e}")
        st.stop()

    # Required columns for the table
    required_columns = ["Keyword", "Volume", "Difficulty", "Chance", "KEI", "Results", "Rank"]
    if not all(col in df_table.columns for col in required_columns):
        st.error(f"The pasted table must contain the following columns: {', '.join(required_columns)}")
    else:
        st.write("### Table Preview (Before Normalization)")
        st.dataframe(df_table.head())

        # Create a new column for normalized Difficulty
        df_table["Normalized Difficulty"] = df_table["Difficulty"].apply(update_difficulity)

        st.write("### Table Preview (After Normalization)")
        st.dataframe(df_table.head())

        # Extract keywords from the table for analysis
        keywords = df_table["Keyword"].dropna().tolist()
        char_count = len(list2_input)
        st.write(f"### Character Count in Second List: {char_count}")

        # Perform the word-level analysis using the 'Keyword' column
        analysis_df = analyze_words(keywords, list2_input)
        st.write("### Analysis Results")
        st.dataframe(analysis_df)

        # Merge the analysis results with the original table (using the Keyword column)
        merged_df = pd.merge(df_table, analysis_df, left_on="Keyword", right_on="Phrase", how="left")
        merged_df.drop(columns=["Phrase"], inplace=True)  # Remove duplicate column

        st.write("### Merged Table with Analysis and Normalized Difficulty")
        st.dataframe(merged_df.head())

        # Download button for the merged results as a CSV file
        st.download_button(
            label="Download Merged Results as CSV",
            data=merged_df.to_csv(index=False, encoding="utf-8"),
            file_name="merged_word_presence_analysis.csv",
            mime="text/csv"
        )
else:
    st.write("Please paste your table and provide the second list to proceed.")
