import pandas as pd
from gensim.models import Word2Vec
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Load the Excel and CSV files
df = pd.read_excel('word2vec/tk 4 TI.xlsx', header=None)
df2 = pd.read_csv('siakad/polinema_alumni.csv', header=None)

nama = df[0].tolist()
namaa = df2[0].tolist()

# Prepare Word2Vec training data
# Since names are short, we'll split them into words (or even characters for Word2Vec)
all_names = [name.split() for name in nama + namaa]  # Splitting names into words

# Train a Word2Vec model based on the names (or you can load a pre-trained model)
word2vec_model = Word2Vec(sentences=all_names, vector_size=100, window=5, min_count=1, workers=4)

# Define the Word2Vec similarity function
def word2vec_similarity(nama, namaa):
    hasil = {}

    for nama1 in nama:
        nama_termirip = "No Match"
        pekerjaan = "No Data"
        tempat_kerja = "No Data"
        highest_similarity = 0  # Track the highest cosine similarity

        # Calculate the Word2Vec vector for nama1
        vector1 = np.mean([word2vec_model.wv[word] for word in nama1.split() if word in word2vec_model.wv], axis=0)

        # Skip if vector1 is invalid (empty or NaN)
        if vector1 is None or np.isnan(vector1).any():
            continue

        for i, nama2 in enumerate(namaa):
            # Calculate the Word2Vec vector for nama2
            vector2 = np.mean([word2vec_model.wv[word] for word in nama2.split() if word in word2vec_model.wv], axis=0)

            # Calculate cosine similarity between the two vectors
            similarity = cosine_similarity([vector1], [vector2])[0][0]

            # If this is the highest similarity, save the result
            if similarity > highest_similarity:
                highest_similarity = similarity
                nama_termirip = nama2

                # Extract current_company and current_title
                if len(df2.columns) >= 3:
                    tempat_kerja = df2.iloc[i, 1]  # current_company
                    pekerjaan = df2.iloc[i, 2]  # current_title

        # Store the result in the dictionary
        hasil[nama1] = (nama_termirip, pekerjaan, tempat_kerja)

    return hasil

# Calculate the Word2Vec similarity and store the results in a dictionary
hasil_dict = word2vec_similarity(nama, namaa)

# Check if columns exist and replace the values, otherwise add them as new columns
if df.shape[1] >= 4:
    df[1] = df[0].map(lambda x: hasil_dict.get(x, ("", "", ""))[0])
    df[2] = df[0].map(lambda x: hasil_dict.get(x, ("", "", ""))[1])
    df[3] = df[0].map(lambda x: hasil_dict.get(x, ("", "", ""))[2])
else:
    df['Nama LinkedIn'] = df[0].map(lambda x: hasil_dict.get(x, ("", "", ""))[0])
    df['Pekerjaan'] = df[0].map(lambda x: hasil_dict.get(x, ("", "", ""))[1])
    df['Tempat Kerja'] = df[0].map(lambda x: hasil_dict.get(x, ("", "", ""))[2])

# Set column headers if needed
if len(df.columns) == 4:
    df.columns = ['Nama Mahasiswa', 'Nama LinkedIn', 'Pekerjaan', 'Tempat Kerja']

# Save the updated DataFrame back to Excel
df.to_excel('word2vec/tk 4 TI.xlsx', index=False)
