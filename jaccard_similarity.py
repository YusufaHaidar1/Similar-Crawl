import pandas as pd

def jaccard_similarity(profil_nama, nama_siakad):
    # Your existing jaccard_similarity function remains the same
    set1 = set(profil_nama.lower().split())
    set2 = set(nama_siakad.lower().split())
    
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    
    similarity = len(intersection) / len(union)
    
    return similarity

# Read the CSV file
df = pd.read_csv('D:/POLINEMA/Skripsi/Similar&Crawl/polinema_alumni_20_01_2025_2004.csv')

# Example: Compare one profile name against all names in CSV
profil_nama = "Yusufa Haidar"  # Your test name

# Calculate similarity for each name in the CSV
results = []
for index, row in df.iterrows():
    nama_siakad = row['name']
    similarity = jaccard_similarity(profil_nama, nama_siakad)
    results.append({
        'nama_siakad': nama_siakad,
        'similarity_score': similarity
    })

# Convert results to DataFrame for better viewing
results_df = pd.DataFrame(results)
# Sort by similarity score in descending order
results_df = results_df.sort_values('similarity_score', ascending=False)

print("Results for:", profil_nama)
print(results_df)