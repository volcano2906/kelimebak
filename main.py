import streamlit as st
import pandas as pd

# Function to perform word-level analysis
def analyze_words(list1, list2):
    # Splitting each phrase in the first list into individual words
    list1_with_words = {phrase: ", ".join(phrase.split()) for phrase in list1}

    # Cleaning and normalizing the second list (handles patterns like 'english,american,')
    list2_normalized = [word.strip().lower() for word in list2.replace(",", " ").split() if word.strip()]

    # Checking if each word from the split phrases is present in the second list
    results_split_words_updated = {
        phrase: {
            "Split Words": split_words,
            "Status": ",".join([word for word in phrase.split() if word.lower() not in list2_normalized])
        }
        for phrase, split_words in list1_with_words.items()
    }

    # Converting the updated results into a DataFrame
    results_split_words_updated_df = pd.DataFrame([
        {"Phrase": phrase.encode("utf-8").decode("utf-8"), 
         "Split Words": data["Split Words"].encode("utf-8").decode("utf-8"), 
         "Status": data["Status"].encode("utf-8").decode("utf-8")}
        for phrase, data in results_split_words_updated.items()
    ])

    return results_split_words_updated_df

# Streamlit app
st.title("Word Presence Analysis")

st.write("Enter the two lists below:")

# Text inputs for the two lists
list1_input = st.text_area("Enter the first list (comma or line-separated)", height=200)
list2_input = st.text_area("Enter the second list (comma or space-separated)", height=100)

if list1_input and list2_input:
    # Processing the input for list1 (supports both comma and line separation)
    list1 = [item.strip() for line in list1_input.splitlines() for item in line.split(",") if item.strip()]
    list2 = list2_input.strip()

    # Count characters in the second list
    char_count = len(list2)
    st.write(f"### Character Count in Second List: {char_count}")

    # Perform analysis
    result_df = analyze_words(list1, list2)

    # Display results
    st.write("### Analysis Results")
    st.dataframe(result_df)

    # Option to download the results
    st.download_button(
        label="Download Results as CSV",
        data=result_df.to_csv(index=False, encoding="utf-8"),
        file_name="word_presence_analysis.csv",
        mime="text/csv"
    )
else:
    st.write("Please provide both lists to proceed.")
