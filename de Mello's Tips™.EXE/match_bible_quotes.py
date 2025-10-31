import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# Load your files
tips_df = pd.read_csv("Final_Enriched_de_Mello_s_Tips_Metadata.csv")
kjv_df = pd.read_csv("KJV.csv")

# Create reference column (e.g., "John 3:16")
kjv_df["Reference"] = kjv_df["Book"] + " " + kjv_df["Chapter"].astype(str) + ":" + kjv_df["Verse"].astype(str)
kjv_df = kjv_df[["Text", "Reference"]].rename(columns={"Text": "Bible Verse"})

# Load the embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Encode Bible verses and tips
bible_embeddings = model.encode(kjv_df["Bible Verse"].tolist(), show_progress_bar=True)
tip_embeddings = model.encode(tips_df["Quote"].tolist(), show_progress_bar=True)

# Match each quote to the closest Bible verse
matched_verses = []
matched_refs = []

for tip_vec in tip_embeddings:
    sims = cosine_similarity([tip_vec], bible_embeddings)[0]
    best_idx = sims.argmax()
    matched_verses.append(kjv_df.iloc[best_idx]["Bible Verse"])
    matched_refs.append(kjv_df.iloc[best_idx]["Reference"])

# Add results to DataFrame
tips_df["Related Bible Passage (KJV)"] = matched_verses
tips_df["KJV Reference"] = matched_refs

# Save to new CSV
tips_df.to_csv("Final_Tips_With_KJV_Matches.csv", index=False)
print("✅ Done! File saved as Final_Tips_With_KJV_Matches.csv")
