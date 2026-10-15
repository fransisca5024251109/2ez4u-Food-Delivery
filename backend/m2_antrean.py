import re
class Stack:
    def __init__(self):
        self.data = []

    def push(self, item):
        self.data.append(item)

    def pop(self):
        if self.is_empty():
            return None
        return self.data.pop()

    def peek(self):
        if self.is_empty():
            return None
        return self.data[-1]

    def is_empty(self):
        return len(self.data) == 0
       
def prioritas(operator):
    if operator == "+" or operator == "-":
        return 1
    elif operator == "*" or operator == "/":
        return 2
    return 0


def ke_postfix(ekspresi):
    tokens = re.findall(r"\d+|[()+\-*/]|\S", ekspresi)

    # Memastikan semua karakter yang digunakan valid
    ekspresi_bersih = re.sub(r"\s+", "", ekspresi)
    if "".join(tokens) != ekspresi_bersih:
        raise ValueError("Ekspresi mengandung karakter tidak valid.")

    output = []
    operator_stack = Stack()
    operator = {"+", "-", "*", "/"}

    for token in tokens:
        if token.isdigit():
            output.append(token)

        elif token == "(":
            operator_stack.push(token)

        elif token == ")":
            ditemukan_buka = False

            while not operator_stack.is_empty():
                atas = operator_stack.pop()

                if atas == "(":
                    ditemukan_buka = True
                    break

                output.append(atas)

            if not ditemukan_buka:
                raise ValueError("Tanda kurung tidak berpasangan.")

        elif token in operator:
            while (
                not operator_stack.is_empty()
                and operator_stack.peek() != "("
                and prioritas(operator_stack.peek()) >= prioritas(token)
            ):
                output.append(operator_stack.pop())

            operator_stack.push(token)

        else:
            raise ValueError(f"Token tidak valid: {token}")

    while not operator_stack.is_empty():
        atas = operator_stack.pop()

        if atas == "(":
            raise ValueError("Tanda kurung tidak berpasangan.")

        output.append(atas)

    # Validasi urutan operand dan operator
    jumlah_operand = 0

    for token in output:
        if token.isdigit():
            jumlah_operand += 1
        else:
            if jumlah_operand < 2:
                raise ValueError("Susunan ekspresi tidak valid.")
            jumlah_operand -= 1

    if jumlah_operand != 1:
        raise ValueError("Susunan ekspresi tidak valid.")

    return " ".join(output)


def hitung(postfix):
    angka_stack = Stack()
    tokens = postfix.split()
    operator = {"+", "-", "*", "/"}

    if not tokens:
        raise ValueError("Ekspresi postfix kosong.")

    for token in tokens:
        if token.isdigit():
            angka_stack.push(int(token))

        elif token in operator:
            if len(angka_stack.data) < 2:
                raise ValueError("Susunan postfix tidak valid.")

            b = angka_stack.pop()
            a = angka_stack.pop()

            if token == "+":
                hasil = a + b
            elif token == "-":
                hasil = a - b
            elif token == "*":
                hasil = a * b
            else:
                if b == 0:
                    raise ZeroDivisionError("Tidak bisa membagi dengan nol.")
                hasil = a / b

            angka_stack.push(hasil)

        else:
            raise ValueError(f"Token postfix tidak valid: {token}")

    if len(angka_stack.data) != 1:
        raise ValueError("Susunan postfix tidak valid.")

    return angka_stack.pop()


class NaiveQueue:
    def __init__(self):
        self.data = []
        self.total_shifts = 0

    def enqueue(self, item):
        self.data.append(item)

    def dequeue(self):
        if len(self.data) == 0:
            return None

        item = self.data.pop(0)
        self.total_shifts += len(self.data)
        return item

    def is_empty(self):
        return len(self.data) == 0

    def size(self):
        return len(self.data)


class CircularQueue:
    def __init__(self, kapasitas=5):
        self.data = [None] * kapasitas
        self.kapasitas = kapasitas
        self.front = 0
        self.rear = 0
        self.count = 0

    def enqueue(self, item):
        if self.count == self.kapasitas:
            return False

        self.data[self.rear] = item
        self.rear = (self.rear + 1) % self.kapasitas
        self.count += 1
        return True
    
    def enqueue_front(self, item):
        if self.count == self.kapasitas:
            return False

        self.front = (self.front - 1) % self.kapasitas
        self.data[self.front] = item
        self.count += 1
        return True

    def dequeue(self):
        if self.count == 0:
            return None

        item = self.data[self.front]
        self.data[self.front] = None
        self.front = (self.front + 1) % self.kapasitas
        self.count -= 1
        return item
    
    def dequeue_rear(self):
        if self.count == 0:
            return None

        self.rear = (self.rear - 1) % self.kapasitas
        item = self.data[self.rear]
        self.data[self.rear] = None
        self.count -= 1
        return item

    def is_empty(self):
        return self.count == 0

    def size(self):
        return self.count


class RiwayatAksi:
    def __init__(self):
        self.undo_stack = Stack()
        self.redo_stack = Stack()

    def catat_aksi(self, aksi):
        self.undo_stack.push(aksi)

        # Aksi baru menghapus riwayat redo
        self.redo_stack = Stack()

    def ambil_undo(self):
        if self.undo_stack.is_empty():
            return None

        aksi = self.undo_stack.pop()
        self.redo_stack.push(aksi)
        return aksi

    def ambil_redo(self):
        if self.redo_stack.is_empty():
            return None

        aksi = self.redo_stack.pop()
        self.undo_stack.push(aksi)
        return aksi



class AntreanDenganUndo:
    def __init__(self, kapasitas=10):
        self.antrean = CircularQueue(kapasitas)
        self.undo_stack = Stack()
        self.redo_stack = Stack()

    def enqueue(self, item):
        berhasil = self.antrean.enqueue(item)

        if not berhasil:
            return False

        self.undo_stack.push(("ENQUEUE", item))
        self.redo_stack = Stack()
        return True

    def dequeue(self):
        item = self.antrean.dequeue()

        if item is None:
            return None

        # Simpan pesanan agar bisa dikembalikan saat undo
        self.undo_stack.push(("DEQUEUE", [item]))
        self.redo_stack = Stack()
        return item

    def undo(self):
        if self.undo_stack.is_empty():
            return None

        aksi = self.undo_stack.peek()

        if aksi[0] == "ENQUEUE":
            item = self.antrean.dequeue_rear()

            if item is None:
                return None

            self.undo_stack.pop()
            self.redo_stack.push(aksi)
            return item

        elif aksi[0] == "DEQUEUE":
            daftar_pesanan = aksi[1]

            # Kembalikan ke depan dengan urutan yang benar
            for item in reversed(daftar_pesanan):
                if not self.antrean.enqueue_front(item):
                    return None

            self.undo_stack.pop()
            self.redo_stack.push(aksi)
            return daftar_pesanan

        return None

    def redo(self):
        if self.redo_stack.is_empty():
            return None

        aksi = self.redo_stack.peek()

        if aksi[0] == "ENQUEUE":
            berhasil = self.antrean.enqueue(aksi[1])

            if not berhasil:
                return None

            self.redo_stack.pop()
            self.undo_stack.push(aksi)
            return aksi[1]

        elif aksi[0] == "DEQUEUE":
            jumlah = len(aksi[1])
            daftar_pesanan = []

            for _ in range(jumlah):
                item = self.antrean.dequeue()

                if item is None:
                    # Kembalikan pesanan yang telanjur dikeluarkan
                    for pesanan in reversed(daftar_pesanan):
                        self.antrean.enqueue_front(pesanan)
                    return None

                daftar_pesanan.append(item)

            self.redo_stack.pop()
            self.undo_stack.push(aksi)
            return daftar_pesanan
        
        return None
    
    def undo_last(self):
        return self.undo()

    def redo_last(self):
        return self.redo()

    def history(self):
        return self.undo_stack.data.copy()
