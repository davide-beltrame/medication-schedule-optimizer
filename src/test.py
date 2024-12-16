import pandas as pd

df = pd.read_excel("data/interactions.xlsx")
df.to_csv("data/interactions.csv", index=False)