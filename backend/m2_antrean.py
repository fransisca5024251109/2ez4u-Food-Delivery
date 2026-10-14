import csv
import time

class Stack:
    def __init__(self):
        self.data = []

    def push(self, nilai):
        self.data.append(nilai)

    def pop(self):
        if self.kosong():
            return None
        return self.data.pop()

    def peek(self):
        if self.kosong():
            return None
        return self.data[-1]

    def kosong(self):
        return len(self.data) == 0

    def ukuran(self):
        return len(self.data)


def pecah_token(ekspresi):
    token = []
    angka = ""

    for karakter in ekspresi:
        if karakter.isdigit() or karakter == ".":
            angka += karakter
        else:
            if angka != "":
                token.append(angka)
                angka = ""

            if karakter in "+-*/()":
                token.append(karakter)
            elif karakter.isspace():
                continue
            else:
                raise ValueError(
                    "Karakter tidak valid: " + karakter
                )

    if angka != "":
        token.append(angka)

    return token


def prioritas(operator):
    if operator == "+" or operator == "-":
        return 1
    if operator == "*" or operator == "/":
        return 2
    return 0


def ke_postfix(ekspresi):
    token = pecah_token(ekspresi)
    stack = Stack()
    hasil = []

    for item in token:
        if item[0].isdigit() or item[0] == ".":
            hasil.append(item)

        elif item == "(":
            stack.push(item)

        elif item == ")":
            ketemu_kurung = False

            while not stack.kosong():
                atas = stack.pop()

                if atas == "(":
                    ketemu_kurung = True
                    break

                hasil.append(atas)

            if not ketemu_kurung:
                raise ValueError("Kurung tidak berpasangan")

        else:
            while (
                not stack.kosong()
                and stack.peek() != "("
                and prioritas(stack.peek()) >= prioritas(item)
            ):
                hasil.append(stack.pop())

            stack.push(item)

    while not stack.kosong():
        atas = stack.pop()

        if atas == "(":
            raise ValueError("Kurung tidak berpasangan")

        hasil.append(atas)

    return hasil


def hitung_postfix(postfix):
    stack = Stack()

    for item in postfix:
        if item not in ("+", "-", "*", "/"):
            stack.push(float(item))

        else:
            operand_kanan = stack.pop()
            operand_kiri = stack.pop()

            if operand_kiri is None or operand_kanan is None:
                raise ValueError("Ekspresi tidak valid")

            if item == "+":
                hasil = operand_kiri + operand_kanan
            elif item == "-":
                hasil = operand_kiri - operand_kanan
            elif item == "*":
                hasil = operand_kiri * operand_kanan
            else:
                if operand_kanan == 0:
                    raise ZeroDivisionError(
                        "Tidak bisa membagi dengan nol"
                    )
                hasil = operand_kiri / operand_kanan

            stack.push(hasil)

    if stack.ukuran() != 1:
        raise ValueError("Ekspresi tidak valid")

    return stack.pop()


def hitung_ekspresi(ekspresi):
    postfix = ke_postfix(ekspresi)
    hasil = hitung_postfix(postfix)
    return postfix, hasil


class AntreanNaif:
    def __init__(self):
        self.data = []
        self.total_geser = 0

    def enqueue(self, nilai):
        self.data.append(nilai)

    def dequeue(self):
        if self.kosong():
            return None

        jumlah = len(self.data) - 1
        nilai = self.data.pop(0)

        self.total_geser += jumlah

        return nilai

    def kosong(self):
        return len(self.data) == 0

    def ukuran(self):
        return len(self.data)

    def lihat_depan(self):
        if self.kosong():
            return None
        return self.data[0]


class AntreanMelingkar:
    def __init__(self, kapasitas=8):
        if kapasitas < 1:
            kapasitas = 1

        self.data = [None] * kapasitas
        self.front = 0
        self.rear = 0
        self.count = 0
        self.total_geser = 0

    def _perbesar(self):
        kapasitas_lama = len(self.data)
        kapasitas_baru = kapasitas_lama * 2
        data_baru = [None] * kapasitas_baru

        for i in range(self.count):
            indeks_lama = (self.front + i) % kapasitas_lama
            data_baru[i] = self.data[indeks_lama]

        self.data = data_baru
        self.front = 0
        self.rear = self.count

    def enqueue(self, nilai):
        if self.count == len(self.data):
            self._perbesar()

        self.data[self.rear] = nilai
        self.rear = (self.rear + 1) % len(self.data)
        self.count += 1

    def dequeue(self):
        if self.kosong():
            return None

        nilai = self.data[self.front]
        self.data[self.front] = None
        self.front = (self.front + 1) % len(self.data)
        self.count -= 1

        return nilai

    def kosong(self):
        return self.count == 0

    def ukuran(self):
        return self.count

    def lihat_depan(self):
        if self.kosong():
            return None
        return self.data[self.front]

    def kapasitas(self):
        return len(self.data)


class ManajerAntrean:
    def __init__(self):
        self.naif = AntreanNaif()
        self.melingkar = AntreanMelingkar()
        self.undo_stack = Stack()
        self.redo_stack = Stack()

    def muat_data(self, daftar_pesanan):
        self.naif = AntreanNaif()
        self.melingkar = AntreanMelingkar()

        for pesanan in daftar_pesanan:
            self.naif.enqueue(pesanan)
            self.melingkar.enqueue(pesanan)

        self.undo_stack = Stack()
        self.redo_stack = Stack()

    def enqueue(self, pesanan):
        self.naif.enqueue(pesanan)
        self.melingkar.enqueue(pesanan)

        self.undo_stack.push(("ENQUEUE", pesanan))

        self.redo_stack = Stack()

    def dequeue(self, jumlah=1):
        if jumlah < 1:
            raise ValueError("Jumlah harus minimal 1")

        keluar_naif = []
        keluar_melingkar = []

        for i in range(jumlah):
            if self.naif.kosong() or self.melingkar.kosong():
                break

            keluar_naif.append(self.naif.dequeue())
            keluar_melingkar.append(self.melingkar.dequeue())

        if len(keluar_naif) > 0:
            self.undo_stack.push(
                ("DEQUEUE", keluar_naif)
            )
            self.redo_stack = Stack()

        return keluar_naif, keluar_melingkar

    def undo(self):
        if self.undo_stack.kosong():
            return "Tidak ada aksi untuk dibatalkan"

        aksi = self.undo_stack.pop()
        jenis = aksi[0]
        nilai = aksi[1]

        if jenis == "ENQUEUE":
            terakhir_naif = self.naif.dequeue()
            terakhir_melingkar = self.melingkar.dequeue()

            if (
                terakhir_naif != nilai
                or terakhir_melingkar != nilai
            ):
                raise RuntimeError(
                    "Urutan antrean tidak konsisten"
                )

        elif jenis == "DEQUEUE":
            self.naif.data = nilai + self.naif.data

            antrean_lama = [
                self.melingkar.data[
                    (self.melingkar.front + i)
                    % len(self.melingkar.data)
                ]
                for i in range(self.melingkar.count)
            ]

            antrean_baru = nilai + antrean_lama
            kapasitas = len(self.melingkar.data)

            while kapasitas < len(antrean_baru):
                kapasitas *= 2

            self.melingkar = AntreanMelingkar(kapasitas)

            for pesanan in antrean_baru:
                self.melingkar.enqueue(pesanan)

        self.redo_stack.push(aksi)
        return "Undo berhasil: " + jenis

    def redo(self):
        if self.redo_stack.kosong():
            return "Tidak ada aksi untuk diulang"

        aksi = self.redo_stack.pop()
        jenis = aksi[0]
        nilai = aksi[1]

        if jenis == "ENQUEUE":
            self.naif.enqueue(nilai)
            self.melingkar.enqueue(nilai)

        elif jenis == "DEQUEUE":
            for pesanan in nilai:
                self.naif.dequeue()
                self.melingkar.dequeue()

        self.undo_stack.push(aksi)
        return "Redo berhasil: " + jenis

    def konsisten(self):
        if self.naif.ukuran() != self.melingkar.ukuran():
            return False

        for i in range(self.naif.ukuran()):
            nilai_naif = self.naif.data[i]
            nilai_melingkar = self.melingkar.data[
                (self.melingkar.front + i)
                % len(self.melingkar.data)
            ]

            if nilai_naif != nilai_melingkar:
                return False

        return True


def muat_pesanan_antre(nama_file="data/pesanan.csv"):
    daftar = []

    with open(nama_file, "r", encoding="utf-8-sig", newline="") as file:
        pembaca = csv.DictReader(file)

        for baris in pembaca:
            status = baris.get("status", "").strip().upper()

            if status == "ANTRE":
                daftar.append(baris)

    return daftar


def bandingkan_dequeue(daftar_pesanan, jumlah=1):
    naif = AntreanNaif()
    melingkar = AntreanMelingkar()

    for pesanan in daftar_pesanan:
        naif.enqueue(pesanan)
        melingkar.enqueue(pesanan)

    mulai = time.perf_counter()

    for i in range(jumlah):
        naif.dequeue()

    waktu_naif = (time.perf_counter() - mulai) * 1000

    mulai = time.perf_counter()

    for i in range(jumlah):
        melingkar.dequeue()

    waktu_melingkar = (time.perf_counter() - mulai) * 1000

    return {
        "waktu_naif_ms": waktu_naif,
        "waktu_melingkar_ms": waktu_melingkar,
        "geseran_naif": naif.total_geser,
        "geseran_melingkar": melingkar.total_geser,
    }
