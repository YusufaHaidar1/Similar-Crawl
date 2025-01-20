def jaccard_similarity(profil_nama, nama_siakad):
    # Langkah 1 : Memecah nama menjadi beberapa kata berdasarkan spasi
    set1 = set(profil_nama.lower().split())
    set2 = set(nama_siakad.lower().split())
    
    # Langkah 2 : Mengambil Intersection / Kata yang sama diantara 2 set / himpunan
    intersection = set1.intersection(set2)
    
    # Langkah 3 : Mengambil Union / Gabungan kata dari kedua set / himpunan
    union = set1.union(set2)
    
    # Langkah 4 : Melakukan perhitungan jaccard
    similarity = len(intersection) / len(union)
    
    return similarity

# Contoh Data
profil_nama = "Yusufa Haidar"
nama_siakad = "Yusufa Haidar"

print(f"Himpunan Profil Nama: {set(profil_nama.lower().split())}")  
print(f"Himpunan Nama Siakad: {set(nama_siakad.lower().split())}")  
print(f"Intersection: {set(profil_nama.lower().split()).intersection(set(nama_siakad.lower().split()))}")  
print(f"Union: {set(profil_nama.lower().split()).union(set(nama_siakad.lower().split()))}")  
print(f"Similarity: {jaccard_similarity(profil_nama, nama_siakad)}") 