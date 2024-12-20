import pandas as pd

def main():
    # Paths to the datasets (adjust if needed)
    drug_data_path = "data/drug_data_1.csv"
    interactions_path = "data/interactions_text.csv"

    # Load datasets
    df_drug = pd.read_csv(drug_data_path)
    df_interactions = pd.read_csv(interactions_path)

    # Basic info
    #print("\n--- DRUG DATASET INFO ---")
    #print("Number of rows:", len(df_drug))
    # print("Number of columns:", len(df_drug.columns))
    #print("Columns:", df_drug.columns.tolist())
    #print(df_drug.head(3))

    # print("\n--- INTERACTIONS DATASET INFO ---")
    # print("Number of rows:", len(df_interactions))
    # print("Number of columns:", len(df_interactions.columns))
    # print("Columns:", df_interactions.columns.tolist())
    # print(df_interactions.head(3))

    # Normalize drug names to a consistent case for analysis
    # Assume 'Drug Name' in df_drug, and 'Drug 1', 'Drug 2' in df_interactions
    df_drug['Drug Name'] = df_drug['Drug Name'].str.title()
    df_interactions['Drug 1'] = df_interactions['Drug 1'].str.title()
    df_interactions['Drug 2'] = df_interactions['Drug 2'].str.title()

    # Unique drugs in drug_data_1
    drug_data_drugs = set(df_drug['Drug Name'].unique())
    print("\nUnique drugs in drug_data_1.csv:", len(drug_data_drugs))

    # Unique drugs in interactions_text
    interaction_drugs = set(df_interactions['Drug 1'].unique()).union(set(df_interactions['Drug 2'].unique()))
    print("Unique drugs in interactions_text.csv:", len(interaction_drugs))

    # Intersection of drugs in both datasets
    common_drugs = drug_data_drugs.intersection(interaction_drugs)
    print("Number of drugs present in both datasets:", len(common_drugs))

    # Count unique interaction descriptions
    unique_interactions = df_interactions['Interaction Description'].unique()
    print("\nNumber of unique interaction descriptions in interactions_text.csv:", len(unique_interactions))

    # Assuming df_interactions is your large DataFrame
    processed_interactions = set()  # Use a set to store unique interactions

    # Loop through the first 100 rows
    for index, row in df_interactions.head(100).iterrows():
        description = row['Interaction Description']
        drug_1 = row['Drug 1']
        drug_2 = row['Drug 2']
        
        # Remove drug names from the Interaction Description
        cleaned_interaction = description.replace(drug_1, "").replace(drug_2, "").strip()
        
        # Add the cleaned interaction to the set
        processed_interactions.add(cleaned_interaction)

    # Convert set to list or print the unique interactions
    unique_interactions = list(processed_interactions)
    for i in unique_interactions:
        print(i)
    
    print("Number of unique interactions (ignoring drug names) in interactions_text.csv:", len(unique_interactions))

    # Dizionario per contare le interazioni pulite
    interaction_counts = {}

    # Itera sulle prime 100 righe
    for _, row in df_interactions.head(100).iterrows():
        description = row['Interaction Description']
        drug_1 = row['Drug 1']
        drug_2 = row['Drug 2']
        
        # Pulizia: rimuove i nomi dei farmaci dalla descrizione
        cleaned_interaction = description.replace(drug_1, "").replace(drug_2, "").strip()
        
        # Conta le occorrenze delle interazioni pulite
        if cleaned_interaction in interaction_counts:
            interaction_counts[cleaned_interaction] += 1
        else:
            interaction_counts[cleaned_interaction] = 1

    # Stampa il numero totale di interazioni uniche
    print("\nNumber of unique interactions (ignoring drug names):", len(interaction_counts))


    # Some basic stats about interaction descriptions (optional)
    # e.g., average length of interaction descriptions
    desc_lengths = df_interactions['Interaction Description'].apply(lambda x: len(str(x)))
    print("Average length of interaction descriptions:", desc_lengths.mean())
    print("Max length of interaction descriptions:", desc_lengths.max())
    print("Min length of interaction descriptions:", desc_lengths.min())

    # Create a merged dataset containing only common drugs
    # For simplicity, let's assume we just want to see the common drugs from df_drug that appear in df_interactions.
    # We know df_interactions doesn't have a single 'Drug Name' column, but we have 'Drug 1' and 'Drug 2'.
    # To merge, we can create a dataframe of all unique drugs from df_interactions and merge with df_drug on 'Drug Name'.

    interaction_unique_drugs = pd.DataFrame(list(interaction_drugs), columns=['Drug Name'])
    merged_df = pd.merge(df_drug, interaction_unique_drugs, on='Drug Name', how='inner')

    print("\n--- MERGED DATA INFO ---")
    print("Number of rows in merged dataset:", len(merged_df))
    print("Number of columns in merged dataset:", len(merged_df.columns))
    print("Merged dataframe columns:", merged_df.columns.tolist())
    print(merged_df.head(3))

    # Print some stats about the merged dataset
    # For example, distribution of Drug Classes among common drugs
    if 'Drug Class' in merged_df.columns:
        class_counts = merged_df['Drug Class'].value_counts()
        print("\nDistribution of Drug Classes in merged dataset:")
        print(class_counts.head(10))

    # You can add more insights as needed, for example:
    # - How many drugs in merged_df are OTC vs Prescription?
    if 'Availability' in merged_df.columns:
        availability_counts = merged_df['Availability'].value_counts()
        print("\nAvailability distribution in merged dataset:")
        print(availability_counts)

    # Number of unique interactions in the drug_data dataset 
    num_unique_interactions = df_drug['Interactions'].nunique()
    print(f"Number of unique descriptions in  drug_data_1.csv under 'Interactions': {num_unique_interactions}") 
    
    
    # This EDA is just a starting point. You can add more descriptive statistics, 
    # plot histograms or value counts, and perform other exploration to understand the data better.

    print("\nEDA complete. Insights above are meant to help understand our tool and data alignment.")


if __name__ == "__main__":
    main()
