import streamlit as st
import pandas as pd

# Function to perform word-level analysis
def analyze_words(list1, list2):
    # Splitting each phrase in the first list into individual words
    list1_with_words = {phrase: ", ".join(phrase.split()) for phrase in list1}

    # Checking if each word from the split phrases is present in the second list
    results_split_words_updated = {
        phrase: {
            "Split Words": split_words,
            "Status": ", ".join([word for word in phrase.split() if word not in map(str.lower, list2.split())])
        }
        for phrase, split_words in list1_with_words.items()
    }

    # Converting the updated results into a DataFrame
    results_split_words_updated_df = pd.DataFrame([
        {"Phrase": phrase, "Split Words": data["Split Words"], "Status": data["Status"]}
        for phrase, data in results_split_words_updated.items()
    ])

    return results_split_words_updated_df

# Streamlit app
st.title("Word Presence Analysis")

st.write("Upload two text files: One for the first list and one for the second list.")

# File uploaders for the two lists
file1 = st.file_uploader("Upload the first list (line by line)", type=["txt"])
file2 = st.file_uploader("Upload the second list (space-separated)", type=["txt"])

if file1 and file2:
    # Reading the uploaded files
    list1 = [line.strip() for line in file1.read().decode("utf-8").splitlines() if line.strip()]
    list2 = file2.read().decode("utf-8").strip()

    # Perform analysis
    result_df = analyze_words(list1, list2)

    # Display results
    st.write("### Analysis Results")
    st.dataframe(result_df)

    # Option to download the results
    st.download_button(
        label="Download Results as CSV",
        data=result_df.to_csv(index=False),
        file_name="word_presence_analysis.csv",
        mime="text/csv"
    )
else:
    st.write("Please upload both files to proceed.")
