import csv

def baca_pesanan():
    pesanan = []
    with open("data/pesanan.csv", "r", encoding="utf-8") as file:
        reader = csv.reader(file)

        next(reader, None)

        for row in reader:
            pesanan.append(row)

    return pesanan

class Array:
    def __init__(self, kapasitas_awal=10):
        self.data = [None] * kapasitas_awal
        self.size = 0
        self.capacity = kapasitas_awal

    def tambah(self, pesanan):
        # Kalau array sudah penuh, kapasitas digandakan
        if self.size == self.capacity:
            self.capacity *= 2

            data_baru = [None] * self.capacity

            for i in range(self.size):
                data_baru[i] = self.data[i]

            self.data = data_baru

        self.data[self.size] = pesanan
        self.size += 1
        
    def tambah_reguler(self, pesanan):
        self.tambah(pesanan)
        
    def tambah_prioritas(self, pesanan):
        posisi = self.size // 2
        if self.size == self.capacity:
            self.capacity *= 2

            data_baru = [None] * self.capacity

            for i in range(self.size):
                data_baru[i] = self.data[i]

            self.data = data_baru

        for i in range(self.size, posisi, -1):
            self.data[i] = self.data[i - 1]

        self.data[posisi] = pesanan
        self.size += 1
    
    def tambah_vip(self, pesanan):
        if self.size == self.capacity:
            self.capacity *= 2

            data_baru = [None] * self.capacity

            for i in range(self.size):
                data_baru[i] = self.data[i]

            self.data = data_baru

        for i in range(self.size, 0, -1):
            self.data[i] = self.data[i - 1]

        self.data[0] = pesanan
        self.size += 1
    
    def lihat(self, index=None):
        if index is None:
            hasil = []

            for i in range(self.size):
                hasil.append(self.data[i])

            return hasil

        if index < 0 or index >= self.size:
            return None

        return self.data[index]
    
    def hapus(self, index):
        if index < 0 or index >= self.size:
            return False

        for i in range(index, self.size - 1):
            self.data[i] = self.data[i + 1]

        self.size -= 1
        self.data[self.size] = None

        return True

class Node:
    def __init__(self, value):
        self.value = value
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def tambah_belakang(self, pesanan):
        node_baru = Node(pesanan)

        if self.head is None:
            self.head = node_baru
            self.tail = node_baru
        else:
            self.tail.next = node_baru
            self.tail = node_baru

        self.size += 1
        
    def tambah_reguler(self, pesanan):
        self.tambah_belakang(pesanan)
    
    def tambah_prioritas(self, pesanan):
        node_baru = Node(pesanan)
        if self.head is None:
            self.head = node_baru
            self.tail = node_baru
            self.size += 1
            return

        posisi = self.size // 2

        if posisi == 0:
            node_baru.next = self.head
            self.head = node_baru
            self.size += 1
            return

        current = self.head

        for i in range(posisi - 1):
            current = current.next

        node_baru.next = current.next
        current.next = node_baru

        self.size += 1
    
    def tambah_vip(self, pesanan):
        node_baru = Node(pesanan)

        node_baru.next = self.head
        self.head = node_baru

        if self.tail is None:
            self.tail = node_baru

        self.size += 1
        
    def lihat(self, index=None):
        if index is None:
            hasil = []
            current = self.head

            while current is not None:
                hasil.append(current.value)
                current = current.next

            return hasil

        if index < 0 or index >= self.size:
            return None

        current = self.head

        for i in range(index):
            current = current.next

        return current.value
    
    def hapus(self, index):
        if index < 0 or index >= self.size:
            return False

        if index == 0:
            self.head = self.head.next

            if self.head is None:
                self.tail = None

        else:
            current = self.head

            for i in range(index - 1):
                current = current.next

            current.next = current.next.next

            if index == self.size - 1:
                self.tail = current

        self.size -= 1
        return True