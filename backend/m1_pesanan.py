import csv


class Array:
    def __init__(self, kapasitas_awal=4):
        self.kapasitas = max(1, kapasitas_awal)
        self.data = [None] * self.kapasitas
        self.jumlah = 0

    def _perbesar_jika_penuh(self):
        if self.jumlah == self.kapasitas:
            kapasitas_baru = self.kapasitas * 2
            data_baru = [None] * kapasitas_baru
            for i in range(self.jumlah):
                data_baru[i] = self.data[i]
            self.data = data_baru
            self.kapasitas = kapasitas_baru

    def append(self, nilai):
        self._perbesar_jika_penuh()
        self.data[self.jumlah] = nilai
        self.jumlah += 1

    def get(self, indeks):
        if indeks < 0 or indeks >= self.jumlah:
            return None
        return self.data[indeks]

    def insert(self, indeks, nilai):
        if indeks < 0 or indeks > self.jumlah:
            return False
        self._perbesar_jika_penuh()
        for i in range(self.jumlah, indeks, -1):
            self.data[i] = self.data[i - 1]
        self.data[indeks] = nilai
        self.jumlah += 1
        return True

    def hapus(self, indeks):
        if indeks < 0 or indeks >= self.jumlah:
            return None
        nilai = self.data[indeks]
        for i in range(indeks, self.jumlah - 1):
            self.data[i] = self.data[i + 1]
        self.jumlah -= 1
        self.data[self.jumlah] = None
        return nilai

    def tambah_reguler(self, pesanan):
        self.append(pesanan)

    def tambah_prioritas(self, pesanan):
        return self.insert(self.jumlah // 2, pesanan)

    def tambah_vip(self, pesanan):
        return self.insert(0, pesanan)


class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.jumlah = 0

    def append(self, data):
        node = Node(data)
        if self.head is None:
            self.head = node
            self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self.jumlah += 1

    def get(self, indeks):
        if indeks < 0 or indeks >= self.jumlah:
            return None
        node = self.head
        for _ in range(indeks):
            node = node.next
        return node.data

    def insert(self, indeks, data):
        if indeks < 0 or indeks > self.jumlah:
            return False
        node = Node(data)
        if indeks == 0:
            node.next = self.head
            self.head = node
            if self.jumlah == 0:
                self.tail = node
        elif indeks == self.jumlah:
            self.tail.next = node
            self.tail = node
        else:
            sebelumnya = self.head
            for _ in range(indeks - 1):
                sebelumnya = sebelumnya.next
            node.next = sebelumnya.next
            sebelumnya.next = node
        self.jumlah += 1
        return True

    def hapus(self, indeks):
        if indeks < 0 or indeks >= self.jumlah:
            return None
        if indeks == 0:
            node_dihapus = self.head
            self.head = self.head.next
            if self.jumlah == 1:
                self.tail = None
        else:
            sebelumnya = self.head
            for _ in range(indeks - 1):
                sebelumnya = sebelumnya.next
            node_dihapus = sebelumnya.next
            sebelumnya.next = node_dihapus.next
            if indeks == self.jumlah - 1:
                self.tail = sebelumnya
        self.jumlah -= 1
        return node_dihapus.data

    def tambah_reguler(self, pesanan):
        self.append(pesanan)

    def tambah_prioritas(self, pesanan):
        return self.insert(self.jumlah // 2, pesanan)

    def tambah_vip(self, pesanan):
        return self.insert(0, pesanan)


def muat_pesanan(nama_file):
    array = Array()
    linked = LinkedList()
    with open(nama_file, "r", encoding="utf-8-sig", newline="") as file:
        pembaca = csv.reader(file)
        next(pembaca, None)
        for baris in pembaca:
            if baris:
                pesanan = tuple(baris)
                array.append(pesanan)
                linked.append(pesanan)
    return array, linked


def buat_pesanan(oid, pelanggan, resto, menu, harga, prioritas):
    return (oid, pelanggan, resto, menu, str(harga), str(prioritas), "", "", "ANTRE")


def format_pesanan(pesanan):
    if pesanan is None:
        return "Pesanan tidak ditemukan."
    kolom = ("oid", "pelanggan", "resto", "menu", "harga", "prioritas",
             "t_masuk_detik", "t_selesai_detik", "status")
    hasil = []
    for i in range(len(pesanan)):
        label = kolom[i] if i < len(kolom) else "kolom_" + str(i)
        hasil.append(label + ": " + str(pesanan[i]))
    return "\n".join(hasil)


def cek_konsistensi(array, linked):
    if array.jumlah != linked.jumlah:
        return False, "Jumlah elemen kedua struktur berbeda."
    for i in range(array.jumlah):
        if array.get(i) != linked.get(i):
            return False, "Data berbeda pada indeks " + str(i)
    return True, "Kedua struktur konsisten."
