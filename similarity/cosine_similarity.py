import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

df = pd.read_excel('cosine/tk 4 TI.xlsx', header=None)
df2 = pd.read_csv('siakad/polinema_alumni.csv', header=None)

nama = df[0].tolist()
namaa = df2[0].tolist()

def cosine_nama(nama, namaa):
  hasil = {}
  vectorizer = CountVectorizer().fit(nama + namaa)

  for nama1 in nama:
    nama_termirip = []
    pekerjaan = []
    tempat_kerja = []
    threshold = 0.5

    for i, nama2 in enumerate(namaa):
      vectors = vectorizer.transform([nama1, nama2])
      similarity = cosine_similarity(vectors)[0][1]

      if similarity > threshold:
        threshold = similarity
        nama_termirip = nama2

        # Assuming df2 has columns: [name, current_company, current_title, graduation_year]
        if len(df2.columns) >= 3:
          tempat_kerja = df2.iloc[i, 1]  # current_company
          pekerjaan = df2.iloc[i, 2] 
        # hasil.append((nama1, nama_termirip, pekerjaan, tempat_kerja))
        hasil[nama1] = (nama_termirip, pekerjaan, tempat_kerja)
  return hasil

hasil = cosine_nama(nama, namaa)
hasil_dict = dict(hasil)
if df.shape[1] >= 4:
  df[1] = df[0].map(lambda x: hasil_dict.get(x, ("", "", ""))[0])
  df[2] = df[0].map(lambda x: hasil_dict.get(x, ("", "", ""))[1])
  df[3] = df[0].map(lambda x: hasil_dict.get(x, ("", "", ""))[2])
else : 
  df['Nama LinkedIn'] = df[0].map(lambda x: hasil_dict.get(x, ("", "", ""))[0])
  df['Pekerjaan'] = df[0].map(lambda x: hasil_dict.get(x, ("", "", ""))[1])
  df['Tempat Kerja'] = df[0].map(lambda x: hasil_dict.get(x, ("", "", ""))[2])  

# Set column headers if you want them
if len(df.columns) == 4:
    df.columns = ['Nama Mahasiswa', 'Nama LinkedIn', 'Pekerjaan', 'Tempat Kerja']
df.to_excel('cosine/tk 4 TI.xlsx', index=False)