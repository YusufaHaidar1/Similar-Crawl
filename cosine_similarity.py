from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Example names
name1 = "Muhammad Rafly Fajaruddin Tsani"
name2 = "M. Rafly Fajaruddin Tsani"

# Initialize the vectorizer
vectorizer = TfidfVectorizer()

# Convert the names into vector form
tfidf_matrix = vectorizer.fit_transform([name1, name2])

# Calculate cosine similarity
cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])

# Output the result
print(f"Cosine Similarity: {cosine_sim[0][0]}")