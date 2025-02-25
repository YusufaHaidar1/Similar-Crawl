import pandas as pd

df = pd.read_excel('siakad/tk 4 TI.xlsx', header=None)
df2 = pd.read_csv('siakad/polinema_alumni.csv', header=None)

if df.iloc[0, 0] == 'Nama Mahasiswa':
    df.columns = df.iloc[0]  # Use the first row as the header
    df = df[1:]  # Remove the first row after setting it as the header

nama = df['Nama Mahasiswa'].tolist()
namaa = df2[0].tolist()

def jaccard_similarity(nama, namaa):
  threshold = 0.5
  hasil = {}
  for nama1 in nama:
    nama_termirip = []
    pekerjaan = []
    tempat_kerja = []

    for i, nama2 in enumerate(namaa):
      set1 = set(nama1)
      set2 = set(nama2)
      similarity = len(set1.intersection(set2)) / len(set1.union(set2))

      if similarity > threshold:
        nama_termirip = nama2

        if len(df2.columns) >= 3:
          tempat_kerja = df2.iloc[i, 1] 
          pekerjaan = df2.iloc[i, 2] 
        hasil[nama1] = (nama_termirip, pekerjaan, tempat_kerja)
  return hasil

hasil = jaccard_similarity(nama, namaa)
hasil_dict = dict(hasil)
if 'Nama LinkedIn' in df.columns:
  df['Nama LinkedIn'] = df['Nama Mahasiswa'].map(lambda x: hasil_dict.get(x, ("", "", ""))[0])
  df['Pekerjaan'] = df['Nama Mahasiswa'].map(lambda x: hasil_dict.get(x, ("", "", ""))[1])
  df['Tempat Kerja'] = df['Nama Mahasiswa'].map(lambda x: hasil_dict.get(x, ("", "", ""))[2])
else : 
  df['Nama LinkedIn'] = df['Nama Mahasiswa'].map(lambda x: hasil_dict.get(x, ("", "", ""))[0])
  df['Pekerjaan'] = df['Nama Mahasiswa'].map(lambda x: hasil_dict.get(x, ("", "", ""))[1])
  df['Tempat Kerja'] = df['Nama Mahasiswa'].map(lambda x: hasil_dict.get(x, ("", "", ""))[2])  

# Set column headers if you want them
if df.columns[0] != 'Nama Mahasiswa':
    df.columns = ['Nama Mahasiswa', 'Nama LinkedIn', 'Pekerjaan', 'Tempat Kerja']
df.to_excel('siakad/tk 4 TI.xlsx', index=False)