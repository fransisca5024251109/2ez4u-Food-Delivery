from m1_pesanan import baca_pesanan

def ambil_kunci(pesanan, kunci):
    if kunci == "oid":
        return pesanan[0]
    elif kunci == "harga":
        return int(pesanan[4])
    elif kunci == "selesai":
        return pesanan[7]
    else:
        raise ValueError("Kunci harus oid, harga, atau selesai")
    
def insertion_sort(A, kunci):
    perbandingan = 0
    pemindahan = 0

    for i in range(1, len(A)):
        nilai = A[i]
        j = i - 1

        while j >= 0:
            perbandingan += 1

            if ambil_kunci(A[j], kunci) > ambil_kunci(nilai, kunci):
                A[j + 1] = A[j]
                pemindahan += 1
                j -= 1
            else:
                break

        A[j + 1] = nilai
        pemindahan += 1

    return perbandingan, pemindahan


def merge_sort(A, kunci):
    perbandingan = 0
    pemindahan = 0

    def urutkan(kiri, kanan):
        nonlocal perbandingan, pemindahan

        if kanan - kiri <= 1:
            return

        tengah = (kiri + kanan) // 2

        urutkan(kiri, tengah)
        urutkan(tengah, kanan)

        hasil = []
        i = kiri
        j = tengah

        while i < tengah and j < kanan:
            perbandingan += 1

            if ambil_kunci(A[i], kunci) <= ambil_kunci(A[j], kunci):
                hasil.append(A[i])
                i += 1
            else:
                hasil.append(A[j])
                j += 1

            pemindahan += 1

        while i < tengah:
            hasil.append(A[i])
            i += 1
            pemindahan += 1

        while j < kanan:
            hasil.append(A[j])
            j += 1
            pemindahan += 1

        for posisi in range(len(hasil)):
            A[kiri + posisi] = hasil[posisi]

    urutkan(0, len(A))

    return perbandingan, pemindahan

def linear_search(A, target):
    perbandingan = 0

    for i in range(len(A)):
        perbandingan += 1

        if A[i][0] == target:
            return i, perbandingan

    return -1, perbandingan


def binary_search(A, target):
    kiri = 0
    kanan = len(A) - 1
    perbandingan = 0

    while kiri <= kanan:
        tengah = (kiri + kanan) // 2
        perbandingan += 1

        if A[tengah][0] == target:
            return tengah, perbandingan
        elif A[tengah][0] < target:
            kiri = tengah + 1
        else:
            kanan = tengah - 1

    return -1, perbandingan
