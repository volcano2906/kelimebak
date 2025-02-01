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

# Function to update/normalize the Difficulty column
def update_difficulty(diff):
    try:
        diff = float(diff)
    except:
        return None
    if 0 <= diff <= 20:
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
        # Assign 250 if conversion fails or rank is empty/null
        rank = 250.0

    # Apply the normalization rules for rank
    if 1 <= rank <= 10:
        return 4
    elif 11 <= rank <= 30:
        return 3
    elif 31 <= rank <= 249:
        return 2
    else:
        return 1

st.title("Word Presence Analysis with Normalized Difficulty and Rank")

st.write(
    """
    ### Instructions
    1. **Paste your table data (Excel format):**  
       Copy and paste your Excel table data (typically tab-separated) into the text area below.  
       The table must contain the following columns:  
       `Keyword, Volume, Difficulty, Chance, KEI, Results, Rank`
    2. **Enter the second list:**  
       This should be a string of words separated by commas or spaces.
    """
)

# Text area for copy-pasting the table data (Excel-style, tab-separated)
table_input = st.text_area("Paste your Excel table data", height=200)

# Text area for the second list
list2_input = st.text_area("Enter the second list (comma or space-separated)", height=100)

if table_input and list2_input:
    # Attempt to read the pasted table as TSV from the text area
    try:
        table_io = io.StringIO(table_input)
        # Using tab separator since Excel copy-paste is typically tab-separated
        df_table = pd.read_csv(table_io, sep="\t")
    except Exception as e:
        st.error(f"Error reading table data: {e}")
        st.stop()

    # Required columns for the table
    required_columns = ["Keyword", "Volume", "Difficulty", "Chance", "KEI", "Results", "Rank"]

    # Check if all required columns exist in the pasted table
    if not all(col in df_table.columns for col in required_columns):
        st.error(f"The pasted table must contain the following columns: {', '.join(required_columns)}")
    else:
        # Create new columns for Normalized Difficulty and Normalized Rank
        df_table["Normalized Difficulty"] = df_table["Difficulty"].apply(update_difficulty)
        df_table["Normalized Rank"] = df_table["Rank"].apply(update_rank)
        
        st.write("### Table Preview (with Normalized Columns)")
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

        # Download button for the analysis results CSV
        st.download_button(
            label="Download Analysis Results as CSV",
            data=analysis_df.to_csv(index=False, encoding="utf-8"),
            file_name="word_presence_analysis.csv",
            mime="text/csv"
        )
else:
    st.write("Please paste your table and provide the second list to proceed.")
