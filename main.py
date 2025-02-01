import streamlit as st
import pandas as pd
import io

# Function to perform word-level analysis on the keywords
def analyze_words(keywords, list2):
    # For each keyword, split into individual words and join them with a comma for display
    keywords_with_words = {phrase: ", ".join(phrase.split()) for phrase in keywords}

    # Normalize the second list (handling patterns like "english,american,")
    list2_normalized = [word.strip().lower() for word in list2.replace(",", " ").split() if word.strip()]

    # Build the analysis: for each phrase, list its words and append those not in the normalized list
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

st.title("Word Presence Analysis")

st.write(
    """
    ### Instructions
    1. **Paste your table data:**  
       Please paste your table data (CSV format) with the following columns in the text area below:  
       `Keyword, Volume, Difficulty, Chance, KEI, Results, Rank`
    2. **Enter the second list:**  
       This should be a string of words separated by commas or spaces.
    """
)

# Text area for copy-pasting the table data
table_input = st.text_area("Paste your table data (CSV format)", height=200)

# Text input for the second list
list2_input = st.text_area("Enter the second list (comma or space-separated)", height=100)

if table_input and list2_input:
    # Attempt to read the pasted table as CSV from the text area
    try:
        table_io = io.StringIO(table_input)
        df_table = pd.read_csv(table_io)
    except Exception as e:
        st.error(f"Error reading table data: {e}")
        st.stop()

    # Required columns for the table
    required_columns = ["Keyword", "Volume", "Difficulty", "Chance", "KEI", "Results", "Rank"]

    # Check if all required columns exist in the pasted table
    if not all(col in df_table.columns for col in required_columns):
        st.error(f"The pasted table must contain the following columns: {', '.join(required_columns)}")
    else:
        st.write("### Table Preview")
        st.dataframe(df_table.head())

        # Extract the list of keywords from the table
        keywords = df_table["Keyword"].dropna().tolist()

        # Count characters in the second list and display it
        char_count = len(list2_input)
        st.write(f"### Character Count in Second List: {char_count}")

        # Perform the word analysis using the 'Keyword' column
        analysis_df = analyze_words(keywords, list2_input)

        # Display the analysis results
        st.write("### Analysis Results")
        st.dataframe(analysis_df)

        # Download button for the results CSV
        st.download_button(
            label="Download Analysis Results as CSV",
            data=analysis_df.to_csv(index=False, encoding="utf-8"),
            file_name="word_presence_analysis.csv",
            mime="text/csv"
        )
else:
    st.write("Please paste your table and provide the second list to proceed.")
