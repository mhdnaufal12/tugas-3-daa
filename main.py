
from pathlib import Path
from functools import lru_cache

# ==========================================
# KONFIGURASI PROGRAM
# ==========================================

BATAS_JARAK = 1

POLA_PENCARIAN = [
    "0000OOOO",
    "3M2I3QM6",
    "4ORAC8CY"
]


# ==========================================
# 1. ALGORITMA LEVENSHTEIN ITERATIF
# ==========================================

def levenshtein(a, b):
    a, b = a.upper(), b.upper()

    if len(a) < len(b):
        a, b = b, a

    sebelumnya = list(range(len(b) + 1))

    for i, ca in enumerate(a, 1):
        sekarang = [i]

        for j, cb in enumerate(b, 1):
            biaya = 0 if ca == cb else 1

            sekarang.append(min(
                sebelumnya[j] + 1,
                sekarang[j - 1] + 1,
                sebelumnya[j - 1] + biaya
            ))

        sebelumnya = sekarang

    return sebelumnya[-1]


# ==========================================
# 2. ALGORITMA LEVENSHTEIN REKURSIF
# ==========================================

def levenshtein_rekursif(a, b):
    a, b = a.upper(), b.upper()

    @lru_cache(maxsize=None)
    def hitung(i, j):
        if i == 0:
            return j

        if j == 0:
            return i

        biaya = 0 if a[i - 1] == b[j - 1] else 1

        return min(
            hitung(i - 1, j) + 1,
            hitung(i, j - 1) + 1,
            hitung(i - 1, j - 1) + biaya
        )

    return hitung(len(a), len(b))


# ==========================================
# 3. STRUKTUR DATA BK-TREE
# ==========================================

class NodeBK:
    def __init__(self, kode):
        self.kode = kode
        self.anak = {}


class BKTree:
    def __init__(self):
        self.root = None

    def tambah(self, kode):
        if self.root is None:
            self.root = NodeBK(kode)
            return

        node = self.root

        while True:
            jarak = levenshtein(kode, node.kode)

            if jarak == 0:
                return

            if jarak not in node.anak:
                node.anak[jarak] = NodeBK(kode)
                return

            node = node.anak[jarak]

    def cari(self, target, batas):
        hasil = []

        def kunjungi(node):
            if node is None:
                return

            jarak = levenshtein(target, node.kode)

            if jarak <= batas:
                hasil.append((node.kode, jarak))

            bawah = jarak - batas
            atas = jarak + batas

            for jarak_cabang, anak in node.anak.items():
                if bawah <= jarak_cabang <= atas:
                    kunjungi(anak)

        if self.root is not None:
            kunjungi(self.root)

        return hasil


# ==========================================
# 4. ALGORITMA MERGE SORT
# ==========================================

def merge_sort(data):
    if len(data) <= 1:
        return data

    tengah = len(data) // 2

    kiri = merge_sort(data[:tengah])
    kanan = merge_sort(data[tengah:])

    hasil = []
    i = j = 0

    while i < len(kiri) and j < len(kanan):
        if (kiri[i][0], kiri[i][1]) <= (kanan[j][0], kanan[j][1]):
            hasil.append(kiri[i])
            i += 1
        else:
            hasil.append(kanan[j])
            j += 1

    hasil.extend(kiri[i:])
    hasil.extend(kanan[j:])

    return hasil


def merge_sort_laporan(data):
    if len(data) <= 1:
        return data

    tengah = len(data) // 2

    kiri = merge_sort_laporan(data[:tengah])
    kanan = merge_sort_laporan(data[tengah:])

    hasil = []
    i = j = 0

    while i < len(kiri) and j < len(kanan):
        if len(kiri[i][2]) >= len(kanan[j][2]):
            hasil.append(kiri[i])
            i += 1
        else:
            hasil.append(kanan[j])
            j += 1

    hasil.extend(kiri[i:])
    hasil.extend(kanan[j:])

    return hasil


# ==========================================
# 5. MEMBACA DATASET
# ==========================================

def baca_dataset():
    lokasi = (
        Path(__file__).resolve().parent
        / "dataset"
        / "case3_referensi_kode_transaksi.txt"
    )

    if not lokasi.exists():
        raise FileNotFoundError(
            f"Dataset tidak ditemukan: {lokasi}"
        )

    with lokasi.open("r", encoding="utf-8-sig") as file:
        data = [
            baris.strip().upper()
            for baris in file
            if baris.strip()
        ]

    if not data:
        raise ValueError("Dataset kosong.")

    return data


# ==========================================
# 6. MEMBUAT INDEKS POSISI DATASET
# ==========================================

def buat_indeks_posisi(data):
    posisi = {}

    for indeks, kode in enumerate(data):
        if kode not in posisi:
            posisi[kode] = []

        posisi[kode].append(indeks)

    return posisi


# ==========================================
# 7. PROSES REKONSILIASI
# ==========================================

def rekonsiliasi(pola, tree, posisi):
    kandidat = tree.cari(pola, BATAS_JARAK)

    hasil = []

    for kode, jarak in kandidat:
        for indeks in posisi[kode]:
            hasil.append((jarak, indeks, kode))

    return merge_sort(hasil)


# ==========================================
# 8. PROGRAM UTAMA
# ==========================================

def main():
    try:
        data = baca_dataset()

    except (FileNotFoundError, ValueError) as error:
        print("Gagal membaca dataset:", error)
        return

    posisi = buat_indeks_posisi(data)

    tree = BKTree()

    for kode in posisi:
        tree.tambah(kode)

    print("=" * 60)
    print("REKONSILIASI FINANSIAL - DIRTY OCR")
    print("=" * 60)

    print("Jumlah data:", len(data))
    print("Jumlah kode unik:", len(posisi))
    print("Batas jarak edit:", BATAS_JARAK)

    laporan = []

    for urutan, pola in enumerate(POLA_PENCARIAN):
        hasil = rekonsiliasi(pola, tree, posisi)
        laporan.append((urutan, pola, hasil))

    # Mengurutkan laporan berdasarkan frekuensi terbesar
    laporan = merge_sort_laporan(laporan)

    print("\n=== HASIL REKONSILIASI KODE TRANSAKSI ===")

    for nomor, (urutan, pola, hasil) in enumerate(
        laporan, start=1
    ):
        print(f"\n{nomor}. Pola: {pola}")

        if not hasil:
            print("Indeks: []")
            print("Distance: []")
            print("Frekuensi: 0")
            continue

        # Indeks ditampilkan mulai dari 1
        indeks = [item[1] + 1 for item in hasil]
        jarak = [item[0] for item in hasil]

        print("Indeks:", indeks)
        print("Distance:", jarak)
        print("Frekuensi:", len(hasil))

    # Pengujian Levenshtein
    print("\n=== PENGUJIAN ALGORITMA ===")

    print(
        "Levenshtein iteratif:",
        levenshtein("4ORAC8CY", "4ORAC8CZ")
    )

    print(
        "Levenshtein rekursif:",
        levenshtein_rekursif("4ORAC8CY", "4ORAC8CZ")
    )

    print("\nProgram selesai.")


if __name__ == "__main__":
    main()
