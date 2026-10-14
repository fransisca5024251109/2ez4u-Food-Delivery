import csv
import time

BATAS_INSERTION_SORT = 20000

def muat_laporan(nama_file="data/pesanan.csv"):
    daftar_pesanan = []

    with open(nama_file, "r", encoding="utf-8-sig", newline="") as file:
        pembaca = csv.DictReader(file)

        for baris in pembaca:
            daftar_pesanan.append(baris)

    return daftar_pesanan


def nilai_kunci(pesanan, kunci):
    nilai = pesanan.get(kunci, "")

    if kunci == "harga":
        try:
            return float(nilai)
        except (TypeError, ValueError):
            return 0.0

    return str(nilai).lower()



def insertion_sort(data, kunci="t_selesai_detik"):
    if len(data) > BATAS_INSERTION_SORT:
        raise ValueError(
            "Insertion Sort dibatasi maksimal {} baris. "
            "Gunakan Merge Sort untuk data yang lebih besar.".format(
                BATAS_INSERTION_SORT
            )
        )

    perbandingan = 0
    mulai = time.perf_counter()

    # Mengurutkan list secara in-place.
    # Data dengan nilai kunci yang sama tetap mempertahankan urutan awal.
    for i in range(1, len(data)):
        item = data[i]
        nilai_item = nilai_kunci(item, kunci)
        j = i - 1

        while j >= 0:
            perbandingan += 1

            if nilai_kunci(data[j], kunci) > nilai_item:
                data[j + 1] = data[j]
                j -= 1
            else:
                break

        data[j + 1] = item

    waktu_ms = (time.perf_counter() - mulai) * 1000

    return {
        "data": data,
        "jumlah_data": len(data),
        "perbandingan": perbandingan,
        "waktu_ms": waktu_ms,
        "algoritma": "Insertion Sort",
        "kunci": kunci,
    }


def _gabung(kiri, kanan, kunci, penghitung):
    hasil = []
    i = 0
    j = 0

    while i < len(kiri) and j < len(kanan):
        penghitung[0] += 1

        if nilai_kunci(kiri[i], kunci) <= nilai_kunci(kanan[j], kunci):
            hasil.append(kiri[i])
            i += 1
        else:
            hasil.append(kanan[j])
            j += 1

    while i < len(kiri):
        hasil.append(kiri[i])
        i += 1

    while j < len(kanan):
        hasil.append(kanan[j])
        j += 1

    return hasil


def _merge_sort(data, kunci, penghitung):
    if len(data) <= 1:
        return data[:]

    tengah = len(data) // 2
    kiri = _merge_sort(data[:tengah], kunci, penghitung)
    kanan = _merge_sort(data[tengah:], kunci, penghitung)

    return _gabung(kiri, kanan, kunci, penghitung)


def merge_sort(data, kunci="t_selesai_detik"):
    penghitung = [0]
    mulai = time.perf_counter()

    hasil = _merge_sort(data, kunci, penghitung)

    waktu_ms = (time.perf_counter() - mulai) * 1000

    return {
        "data": hasil,
        "jumlah_data": len(hasil),
        "perbandingan": penghitung[0],
        "waktu_ms": waktu_ms,
        "algoritma": "Merge Sort",
        "kunci": kunci,
    }


def linear_search(data, target, kunci="oid"):
    mulai = time.perf_counter()
    perbandingan = 0
    indeks_ditemukan = -1

    target_teks = str(target).strip().lower()

    for i in range(len(data)):
        perbandingan += 1

        nilai = str(data[i].get(kunci, "")).strip().lower()

        if nilai == target_teks:
            indeks_ditemukan = i
            break

    waktu_ms = (time.perf_counter() - mulai) * 1000

    return {
        "indeks": indeks_ditemukan,
        "data": data[indeks_ditemukan] if indeks_ditemukan >= 0 else None,
        "ditemukan": indeks_ditemukan >= 0,
        "perbandingan": perbandingan,
        "waktu_ms": waktu_ms,
        "algoritma": "Linear Search",
        "target": target,
    }


def binary_search(data_terurut, target, kunci="oid"):
    mulai = time.perf_counter()
    perbandingan = 0
    kiri = 0
    kanan = len(data_terurut) - 1

    target_teks = str(target).strip().lower()
    indeks_ditemukan = -1

    while kiri <= kanan:
        tengah = (kiri + kanan) // 2
        nilai = str(
            data_terurut[tengah].get(kunci, "")
        ).strip().lower()

        perbandingan += 1

        if nilai == target_teks:
            indeks_ditemukan = tengah
            break

        perbandingan += 1

        if nilai < target_teks:
            kiri = tengah + 1
        else:
            kanan = tengah - 1

    waktu_ms = (time.perf_counter() - mulai) * 1000

    return {
        "indeks": indeks_ditemukan,
        "data": (
            data_terurut[indeks_ditemukan]
            if indeks_ditemukan >= 0 else None
        ),
        "ditemukan": indeks_ditemukan >= 0,
        "perbandingan": perbandingan,
        "waktu_ms": waktu_ms,
        "algoritma": "Binary Search",
        "target": target,
    }


def bandingkan_sort(data, kunci="harga", jumlah=None):
    sampel = data

    if jumlah is not None:
        if jumlah < 0:
            raise ValueError("Jumlah data tidak boleh negatif.")
        sampel = data[:jumlah]

    hasil_insertion = insertion_sort(sampel, kunci)
    hasil_merge = merge_sort(sampel, kunci)

    identik = len(hasil_insertion["data"]) == len(hasil_merge["data"])

    if identik:
        for i in range(len(hasil_insertion["data"])):
            if hasil_insertion["data"][i] != hasil_merge["data"][i]:
                identik = False
                break

    return {
        "insertion_sort": hasil_insertion,
        "merge_sort": hasil_merge,
        "hasil_identik": identik,
    }


def siapkan_binary_search(data, kunci="oid"):
    """
    Mengurutkan data berdasarkan kunci terlebih dahulu.
    Waktu sort dilaporkan terpisah dari waktu pencarian.
    """
    hasil_sort = merge_sort(data, kunci)

    return {
        "data": hasil_sort["data"],
        "waktu_sort_ms": hasil_sort["waktu_ms"],
        "perbandingan_sort": hasil_sort["perbandingan"],
        "kunci": kunci,
    }
