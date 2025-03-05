import streamlit as st
import pandas as pd
import fnv_c
import xxhash
import ctypes

def to_int64(number):
    return ctypes.c_longlong(number).value

def fnv1_64(string):
    if isinstance(string, str):
        string = string.encode("utf-8")
    return to_int64(fnv_c.fnv0_64(string))

def hash_64_int_signed(text):
    h = xxhash.xxh64(text).intdigest()
    return to_int64(h)

def process_file(uploaded_file, optimization_id, split_ratio):
    df = pd.read_csv(uploaded_file)

    url_column_candidates = [c for c in df.columns if 'url' in c.lower()]

    
    if not len(url_column_candidates) :
        st.error("Error: The uploaded CSV must have exactly one column named 'URL'.")
        return None
    
    column_to_use_for_url = url_column_candidates[0]

    module_id_hash = hash_64_int_signed(optimization_id)
    
    df["in_variant_group"] = df[column_to_use_for_url].apply(lambda url: abs(fnv1_64(url) ^ module_id_hash) % 100 < split_ratio)
    
    return df

def main():
    st.title("URL Split-Testing Identifier")
    
    uploaded_file = st.file_uploader("Upload a CSV file containing a single column named 'URL'", type=["csv"])
    
    optimization_id = st.text_input("Enter Optimization ID")
    split_ratio = st.number_input("Enter Split Ratio (%)", min_value=0, max_value=100, value=50, step=10)
    
    if uploaded_file is not None:
        df_result = process_file(uploaded_file, optimization_id, split_ratio)
        
        if df_result is not None:
            st.write("Processed Data Preview:")
            st.dataframe(df_result.head(20))
            
            csv = df_result.to_csv(index=False).encode('utf-8')
            st.download_button("Download Processed CSV", data=csv, file_name="url_list_with_split.csv", mime="text/csv")

if __name__ == "__main__":
    main()