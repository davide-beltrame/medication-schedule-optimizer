import pandas as pd
import re

def normalize_text(txt: str) -> str:
    """
    Convert to lower case, remove parentheses and their contents,
    remove punctuation except spaces, and collapse multiple spaces.
    This helps unify variations like 'Fluciclovine (18F)' vs 'Fluciclovine (18f)'.
    """
    # Lower case
    txt = txt.lower()
    # Remove any parentheses and their contents
    txt = re.sub(r"\(.*?\)", "", txt)
    # Remove punctuation except spaces (keep alphanumeric, space)
    txt = re.sub(r"[^a-z0-9\s]", " ", txt)
    # Collapse multiple spaces
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt

def clean_interaction_desc(description: str, drug_a: str, drug_b: str) -> str:
    """
    Remove references to drug_a and drug_b (in any normalized form) from description.
    We do the actual removal on normalized strings, but return a 'cleaned' version
    that's good enough for pattern analysis.
    """
    # Normalize drug names
    norm_drug_a = normalize_text(drug_a)
    norm_drug_b = normalize_text(drug_b)
    
    # Also normalize the description for searching
    norm_desc = normalize_text(description)

    # Build regex patterns for the normalized drug names
    # \b ensures we match whole words
    pattern_a = re.compile(r"\b" + re.escape(norm_drug_a) + r"\b", re.IGNORECASE)
    pattern_b = re.compile(r"\b" + re.escape(norm_drug_b) + r"\b", re.IGNORECASE)

    # Remove them from the normalized description
    cleaned_desc = pattern_a.sub("", norm_desc)
    cleaned_desc = pattern_b.sub("", cleaned_desc)
    
    # Collapse extra spaces again
    cleaned_desc = re.sub(r"\s+", " ", cleaned_desc).strip()

    return cleaned_desc

def load_data(drug_data_path: str, interactions_path: str):
    """
    Load and return the drug and interactions datasets with normalized drug names.
    """
    df_drug = pd.read_csv(drug_data_path)
    df_interactions = pd.read_csv(interactions_path)

    # Normalize drug names
    df_drug['Drug Name'] = df_drug['Drug Name'].str.title()
    df_interactions['Drug 1'] = df_interactions['Drug 1'].str.title()
    df_interactions['Drug 2'] = df_interactions['Drug 2'].str.title()

    return df_drug, df_interactions

def basic_dataset_info(df_drug: pd.DataFrame, df_interactions: pd.DataFrame) -> None:
    """
    Print basic overview of both datasets: size, unique drug counts, overlap, etc.
    """
    print("\n--- BASIC DATASET STATS ---")
    print(f"drug_data_1.csv -> rows: {len(df_drug)}, columns: {len(df_drug.columns)}")
    print(f"interactions_text.csv -> rows: {len(df_interactions)}, columns: {len(df_interactions.columns)}")

    # Unique drug counts and overlap
    drug_data_drugs = set(df_drug['Drug Name'].unique())
    interaction_drugs = set(df_interactions['Drug 1']).union(set(df_interactions['Drug 2']))

    print("\nUnique drugs in drug_data_1.csv:", len(drug_data_drugs))
    print("Unique drugs in interactions_text.csv:", len(interaction_drugs))

    common_drugs = drug_data_drugs.intersection(interaction_drugs)
    print("Number of drugs present in both datasets:", len(common_drugs))

    # Number of unique interaction descriptions
    unique_descriptions = df_interactions['Interaction Description'].unique()
    print("\nNumber of unique interaction descriptions in interactions_text.csv:", len(unique_descriptions))

def analyze_interactions(df_interactions: pd.DataFrame) -> None:
    all_interaction_counts = {}
    for _, row in df_interactions.iterrows():
        desc = row['Interaction Description']
        d1, d2 = row['Drug 1'], row['Drug 2']
        cleaned = clean_interaction_desc(desc, d1, d2)
        all_interaction_counts[cleaned] = all_interaction_counts.get(cleaned, 0) + 1

    print("\nNumber of unique interactions (ignoring drug names):", len(all_interaction_counts))
    
    # Sort and print top interactions
    sorted_all = dict(sorted(all_interaction_counts.items(), key=lambda x: x[1], reverse=True))
    print("\nTop unique cleaned interactions in all rows:")
    for interaction, count in sorted_all.items():
        print(f'  "{interaction}" -> {count} occurrences')

def interaction_description_stats(df_interactions: pd.DataFrame) -> None:
    """
    Print some basic length statistics of the 'Interaction Description' column.
    """
    desc_lengths = df_interactions['Interaction Description'].astype(str).apply(len)
    print("\nInteraction Description Length Stats:")
    print("  Average length:", desc_lengths.mean())
    print("  Max length:", desc_lengths.max())
    print("  Min length:", desc_lengths.min())

def merged_drug_info(df_drug: pd.DataFrame, df_interactions: pd.DataFrame) -> None:
    """
    Merge info to see which drugs appear in both dataframes, and print distribution of columns.
    """
    interaction_drugs = set(df_interactions['Drug 1']).union(set(df_interactions['Drug 2']))
    interaction_unique_drugs = pd.DataFrame(list(interaction_drugs), columns=['Drug Name'])
    merged_df = pd.merge(df_drug, interaction_unique_drugs, on='Drug Name', how='inner')

    print("\n--- MERGED DATA INFO ---")
    print("  Number of rows:", len(merged_df))
    print("  Number of columns:", len(merged_df.columns))
    print("  Columns:", merged_df.columns.tolist())
    print(merged_df.head(3))

    # Distribution of Drug Class (top 10)
    if 'Drug Class' in merged_df.columns:
        print("\nDistribution of Drug Classes in merged dataset (top 10):")
        print(merged_df['Drug Class'].value_counts().head(10))

    # Availability distribution
    if 'Availability' in merged_df.columns:
        print("\nAvailability distribution in merged dataset:")
        print(merged_df['Availability'].value_counts())

    # Check unique 'Interactions' field in df_drug
    if 'Interactions' in df_drug.columns:
        num_unique = df_drug['Interactions'].nunique()
        print(f"\nNumber of unique descriptions in 'Interactions' column (drug_data_1.csv): {num_unique}")

def build_merged_csv(
    drug_data_path: str,
    interactions_path: str,
    output_drug_csv: str,
    output_interactions_csv: str
):
    """
    Builds two CSV files:
      1) A filtered 'drug_data' CSV for only the common drugs
      2) A filtered 'interactions' CSV for interactions among those common drugs

    :param drug_data_path: path to the drug_data_1.csv file
    :param interactions_path: path to the interactions_text.csv file
    :param output_drug_csv: path to write the filtered drug data
    :param output_interactions_csv: path to write the filtered interactions
    """

    # 1. Load data
    df_drug = pd.read_csv(drug_data_path)
    df_interactions = pd.read_csv(interactions_path)

    # 2. Normalize columns for consistency (title case)
    df_drug["Drug Name"] = df_drug["Drug Name"].str.title()
    df_interactions["Drug 1"] = df_interactions["Drug 1"].str.title()
    df_interactions["Drug 2"] = df_interactions["Drug 2"].str.title()

    # 3. Identify the set of common drugs
    drug_data_drugs = set(df_drug["Drug Name"].unique())
    interaction_drugs = set(df_interactions["Drug 1"]).union(df_interactions["Drug 2"])
    common_drugs = drug_data_drugs.intersection(interaction_drugs)

    print(f"Found {len(common_drugs)} common drugs between the two datasets.")

    # 4. Subset 'df_drug' to only these common drugs
    df_merged_drug = df_drug[df_drug["Drug Name"].isin(common_drugs)]

    # 5. Subset 'df_interactions' to only pairs that are both in 'common_drugs'
    df_merged_interactions = df_interactions[
        df_interactions["Drug 1"].isin(common_drugs)
        & df_interactions["Drug 2"].isin(common_drugs)
    ]

    print(f"Merged drug data has {len(df_merged_drug)} rows.")
    print(f"Merged interactions data has {len(df_merged_interactions)} rows.")

    # 6. Write to CSV
    df_merged_drug.to_csv(output_drug_csv, index=False)
    df_merged_interactions.to_csv(output_interactions_csv, index=False)

    print(f"Wrote merged drug data to '{output_drug_csv}'.")
    print(f"Wrote merged interaction data to '{output_interactions_csv}'.")

def build_subset_1(drugs_csv, interactions_csv, output_csv="data/subset_1.csv"):
    df_d = pd.read_csv(drugs_csv).head(3)
    df_i = pd.read_csv(interactions_csv)
    chosen_drugs = set(df_d["Drug Name"])
    d_contra = {r["Drug Name"]: r["Contraindications"] for _, r in df_d.iterrows()}
    df_i = df_i[(df_i["Drug 1"].isin(chosen_drugs)) | (df_i["Drug 2"].isin(chosen_drugs))]
    rows = []
    for _, row in df_i.iterrows():
        d1, d2 = row["Drug 1"], row["Drug 2"]
        rows.append({
            "Drug 1": d1,
            "Drug 2": d2,
            "Interaction Description": row["Interaction Description"],
            "Drug 1 Contraindications": d_contra.get(d1, "Unknown"),
            "Drug 2 Contraindications": d_contra.get(d2, "Unknown")
        })
    subset_1 = pd.DataFrame(rows)
    subset_1.to_csv(output_csv, index=False)

    # subset_1 is a DataFrame with the following columns:
    #   - Drug 1
    #   - Drug 2
    #   - Interaction Description
    #   - Drug 1 Contraindications
    #   - Drug 2 Contraindications

    # the drugs in the subset are the ones from the first 3 rows of the drugs_csv file


    return subset_1


if __name__ == "__main__":
    # Adjust paths as needed
    drug_data_path = "data/common_drugs.csv"
    interactions_path = "data/common_interactions.csv"

    df_drug, df_interactions = load_data(drug_data_path, interactions_path)
    #basic_dataset_info(df_drug, df_interactions)
    analyze_interactions(df_interactions)
    #interaction_description_stats(df_interactions)
    #merged_drug_info(df_drug, df_interactions)

#     build_merged_csv(
#     drug_data_path="data/drug_data_1.csv",
#     interactions_path="data/interactions_text.csv",
#     output_drug_csv="data/common_drugs.csv",
#     output_interactions_csv="data/common_interactions.csv"
# )

    subset_df = build_subset_1("data/common_drugs.csv", "data/common_interactions.csv")
    print(subset_df)


    print("\n--- EDA COMPLETE ---\n")