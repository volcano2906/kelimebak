import streamlit as st
import pandas as pd
import io
import itertools
from collections import defaultdict

##############################
# Part 1: Data Processing Code
##############################

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
# If rank is empty or null, assign 250 before applying normalization rules.
def update_rank(rank):
    try:
        rank = float(rank)
    except:
        rank = 250.0
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

##############################
# Part 2: Optimization Functions
##############################

def calculate_effective_points(keyword_list):
    """Calculate effective points per keyword and new keyword combinations based on total point."""
    def keyword_score(keyword, base_points):
        words = keyword.split()
        if len(words) == 1:
            return base_points  # Exact match (single word)
        return sum(base_points / (i + 1) for i in range(len(words) - 1))
    
    return [(kw, points, keyword_score(kw, points), keyword_score(kw, points), keyword_score(kw, points) * (1/3))
            for kw, points in keyword_list]

def sort_keywords_by_total_points(keyword_list):
    """Sort keywords by total calculated points instead of per character efficiency."""
    return sorted(keyword_list, key=lambda x: x[1], reverse=True)

def normalize_word(word):
    """Normalize words to handle singular/plural variations"""
    return word.rstrip('s')

def expand_keywords(keyword_list, max_length=29):
    """Generate potential keyword combinations based on existing keywords and calculate their adjusted points."""
    expanded_keywords = set(keyword_list)
    keyword_map = {kw: points for kw, points in keyword_list}
    
    for kw1, points1 in keyword_list:
        for kw2, points2 in keyword_list:
            if kw1 != kw2:
                words1 = kw1.split()
                words2 = kw2.split()
                combined = words1 + [w for w in words2 if w not in words1]  # Ordered expansion
                new_kw = " ".join(combined)
                if new_kw not in keyword_map and len(new_kw) <= max_length:
                    distance = abs(len(words1) - len(words2))
                    new_points = points1 + (points2 / (distance + 1))
                    expanded_keywords.add((new_kw, new_points))
    
    return list(expanded_keywords)

def construct_best_phrase(field_limit, keywords, multiplier, used_words, used_keywords):
    """Constructs the highest scoring phrase dynamically by combining keywords."""
    field = []
    total_points = 0
    remaining_chars = field_limit
    
    sorted_keywords = sort_keywords_by_total_points(keywords)
    while remaining_chars > 0 and sorted_keywords:
        best_keyword = sorted_keywords.pop(0)
        kw, base_points, f1_points, f2_points, f3_points = best_keyword
        words = kw.split()
        normalized_words = {normalize_word(word) for word in words}
        
        if kw not in used_keywords and not normalized_words.intersection(used_words):
            if remaining_chars - len(kw) >= 0:
                field.append(kw)
                total_points += base_points * field_limit * multiplier
                used_keywords.add(kw)
                used_words.update(normalized_words)
                remaining_chars -= len(kw) + 1  # +1 for space
    
    return field, total_points, used_keywords, field_limit - remaining_chars

def fill_field_with_word_breaking(field_limit, keywords, used_words, used_keywords, stop_words):
    """Fill field 3, allowing keyword breaking while ensuring no duplicate words or stop words."""
    field = []
    total_points = 0
    remaining_chars = field_limit
    
    for kw, base_points, f1_points, f2_points, f3_points in keywords:
        if kw in used_keywords:
            continue  # Skip already used full keywords
        words = kw.split()
        for word in words:
            normalized_word = normalize_word(word)
            if normalized_word not in used_words and normalized_word not in stop_words and remaining_chars >= len(word):
                field.append(word)
                total_points += f3_points  # Full points if the word is used
                used_words.add(normalized_word)
                remaining_chars -= len(word) + 1  # +1 for comma or space
    return field, total_points, used_keywords, field_limit - remaining_chars

def optimize_keyword_placement(keyword_list):
    """Optimize keyword placement across three fields for maximum points."""
    stop_words = {"the", "and", "for", "to", "of", "an", "a", "in", "on", "with", "by", "as", "at", "is"}
    expanded_keywords = expand_keywords(keyword_list, max_length=29)
    sorted_keywords = calculate_effective_points(expanded_keywords)
    used_words = set()
    used_keywords = set()
    
    # Construct best phrase dynamically for Field 1 (multiplier 1)
    field1, points1, used_kw1, length1 = construct_best_phrase(29, sorted_keywords, 1, used_words, used_keywords)
    
    # Construct best phrase dynamically for Field 2 (multiplier 1)
    field2, points2, used_kw2, length2 = construct_best_phrase(29, sorted_keywords, 1, used_words, used_keywords)
    
    # Fill Field 3 (multiplier 1/3, allows word breaking)
    field3, points3, used_kw3, length3 = fill_field_with_word_breaking(100, sorted_keywords, used_words, used_keywords, stop_words)
    points3 *= (1/3)
    
    # Join Field 3 keywords with a comma and ensure the result does not exceed 100 characters.
    field3_str = ",".join(field3)
    if len(field3_str) > 100:
        field3_str = field3_str[:100]
    
    total_points = points1 + points2 + points3
    
    return {
        "Field 1": (" ".join(field1), points1, length1),
        "Field 2": (" ".join(field2), points2, length2),
        "Field 3": (field3_str, points3, len(field3_str)),
        "Total Points": total_points
    }

##############################
# Part 3: Streamlit Interface
##############################

st.title("Word Analysis & Optimized Keyword Placement")

st.write(
    """
    ### Instructions
    1. **Paste your table data (Excel format):**  
       Copy and paste your Excel table data (typically tab-separated) into the text area below.  
       The table must contain the following columns:  
       `Keyword, Volume, Difficulty, Chance, KEI, Results, Rank`
    """
)

# Text area for pasting table data
table_input = st.text_area("Paste your Excel table data", height=200)

if table_input:
    try:
        table_io = io.StringIO(table_input)
        df_table = pd.read_csv(table_io, sep="\t")
    except Exception as e:
        st.error(f"Error reading table data: {e}")
        st.stop()
    
    required_columns = ["Keyword", "Volume", "Difficulty", "Chance", "KEI", "Results", "Rank"]
    if not all(col in df_table.columns for col in required_columns):
        st.error(f"The pasted table must contain the following columns: {', '.join(required_columns)}")
        st.stop()
    else:
        # Normalize and calculate columns
        df_table["Normalized Difficulty"] = df_table["Difficulty"].apply(update_difficulty)
        df_table["Normalized Rank"] = df_table["Rank"].apply(update_rank)
        df_table["Calculated Result"] = df_table["Results"].apply(update_result)
        df_table["Final Score"] = df_table.apply(calculate_final_score, axis=1)
        df_table = df_table.drop(columns=["Chance", "KEI"])
        df_table = df_table.sort_values(by="Final Score", ascending=False)
        
        # Build the keyword list for optimization from the Excel data:
        # Each tuple: (Keyword, Final Score)
        opt_keyword_list = list(zip(df_table["Keyword"].tolist(), df_table["Final Score"].tolist()))
        optimized_fields = optimize_keyword_placement(opt_keyword_list)
        
        # Extract all keywords (for word analysis) from the table
        excel_keywords = df_table["Keyword"].dropna().tolist()
        
        ##############################
        # Display Text Inputs and Optimized Results
        ##############################
        st.subheader("Enter Word Lists")
        
        # First text input and its optimized field (Field 1)
        first_field = st.text_input("Enter first text (max 30 characters)", max_chars=30)
        st.write("**Optimized Field 1:**", optimized_fields.get("Field 1")[0])
        
        # Second text input and its optimized field (Field 2)
        second_field = st.text_input("Enter second text (max 30 characters)", max_chars=30)
        st.write("**Optimized Field 2:**", optimized_fields.get("Field 2")[0])
        
        # Third text input and its optimized field (Field 3)
        third_field = st.text_input("Enter third text (comma or space-separated, max 100 characters)", max_chars=100)
        st.write("**Optimized Field 3:**", optimized_fields.get("Field 3")[0])
        
        # Combine the three fields for word analysis
        combined_text = f"{first_field} {second_field} {third_field}".strip()
        st.write("### Combined Word List for Analysis:", combined_text)
        
        # Perform word analysis on the combined text using keywords from Excel
        analysis_df = analyze_words(excel_keywords, combined_text)
        st.write("### Word Analysis Results")
        st.dataframe(analysis_df)
        st.download_button(
            label="Download Word Analysis CSV",
            data=analysis_df.to_csv(index=False, encoding="utf-8"),
            file_name="word_presence_analysis.csv",
            mime="text/csv"
        )
        
        # Also, display total optimized points
        st.write("**Total Optimized Points:**", optimized_fields.get("Total Points"))
else:
    st.write("Please paste your table data to proceed.")
