import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import time
import random
from datetime import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
from m1_pesanan import baca_pesanan, Array, LinkedList
from m2_antrean import ke_postfix, hitung, AntreanDenganUndo, NaiveQueue, CircularQueue
from m3_laporan import insertion_sort, merge_sort, linear_search, binary_search

BG = "#eef1f5"
PINK = "#294967"
PINK_DARK = "#1b3046"
PINK_HOVER = "#244363"
PINK_LIGHT = "#e4e9ef"
WHITE = "#FFFFFF"
TEXT = "#263442"
MUTED = "#68798a"
BORDER = "#c4cbd3"

data_pesanan = []
array_pesanan = Array()
linked_list_pesanan = LinkedList()
menu_aktif = None
BATAS_TAMPIL = 50
antrean_undo = AntreanDenganUndo(kapasitas=5)
antrean_naif = NaiveQueue()
antrean_circular = CircularQueue(kapasitas=200000)

root = tk.Tk()
root.title("2EZ4U Food Delivery")
root.geometry("1200x750")
root.minsize(950, 600)
root.configure(bg=BG)

header = tk.Frame(root, bg=PINK_DARK, height=58)
header.pack(fill="x")
header.pack_propagate(False)
tk.Label(header, text="2EZ4U Food Delivery", font=("Segoe UI", 17, "bold"), bg=PINK_DARK, fg=WHITE).pack(side="left", padx=20, pady=10)

body = tk.Frame(root, bg=BG)
body.pack(fill="both", expand=True)

sidebar = tk.Frame(
    body,
    bg=PINK_LIGHT,
    width=300
)
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)
sidebar_canvas = tk.Canvas(
    sidebar,
    bg=PINK_LIGHT,
    highlightthickness=0,
    width=280
)
sidebar_canvas.pack(side="left", fill="both", expand=True)

sidebar_scrollbar = ttk.Scrollbar(
    sidebar,
    orient="vertical",
    command=sidebar_canvas.yview
)
sidebar_scrollbar.pack(side="right", fill="y")
sidebar_canvas.configure(
    yscrollcommand=sidebar_scrollbar.set
)

menu_frame = tk.Frame(
    sidebar_canvas,
    bg=PINK_LIGHT
)
window_menu = sidebar_canvas.create_window(
    (0, 0),
    window=menu_frame,
    anchor="nw"
)

# Memperbarui area scroll ketika isi menu berubah
def perbarui_scroll_sidebar(event=None):
    sidebar_canvas.configure(
        scrollregion=sidebar_canvas.bbox("all")
    )

def sesuaikan_lebar_sidebar(event):
    sidebar_canvas.itemconfigure(
        window_menu,
        width=event.width
    )

menu_frame.bind(
    "<Configure>",
    perbarui_scroll_sidebar
)
sidebar_canvas.bind(
    "<Configure>",
    sesuaikan_lebar_sidebar
)

def scroll_sidebar(event):
    sidebar_canvas.yview_scroll(
        int(-1 * (event.delta / 120)),
        "units"
    )

def aktifkan_scroll(event):
    sidebar_canvas.bind_all(
        "<MouseWheel>",
        scroll_sidebar
    )

def nonaktifkan_scroll(event):
    sidebar_canvas.unbind_all("<MouseWheel>")

sidebar_canvas.bind("<Enter>", aktifkan_scroll)
sidebar_canvas.bind("<Leave>", nonaktifkan_scroll)

# ===== AREA KONTEN + COMMAND GLOBAL =====
content_shell = tk.Frame(body, bg=WHITE)
content_shell.pack(side="left", fill="both", expand=True)

content = tk.Frame(content_shell, bg=WHITE)
content.pack(side="top", fill="both", expand=True)

command_frame = tk.Frame(content_shell, bg=WHITE, bd=1, relief="solid")
command_frame.pack(side="bottom", fill="x", padx=6, pady=(0, 4))

tk.Label(
    command_frame,
    text="COMMAND",
    font=("Segoe UI", 8, "bold"),
    bg=WHITE,
    fg=TEXT,
    anchor="w"
).pack(fill="x", padx=5, pady=(2, 0))

command_log = tk.Text(
    command_frame,
    height=3,
    font=("Consolas", 8),
    bg=WHITE,
    fg=TEXT,
    relief="flat",
    wrap="none",
    state="disabled"
)
command_log.pack(side="left", fill="x", expand=True, padx=(5, 0), pady=(0, 3))
command_scroll = ttk.Scrollbar(
    command_frame, orient="vertical", command=command_log.yview
)
command_scroll.pack(side="right", fill="y", padx=(0, 4), pady=(0, 3))
command_log.configure(yscrollcommand=command_scroll.set)

MAX_COMMAND_LOG = 200

def catat_command(nama_operasi, modul, durasi_ms):
    """Tambahkan operasi dan waktu eksekusinya ke panel COMMAND global."""
    baris = f"{nama_operasi:<18} -> {modul:<18} {durasi_ms:.2f} ms"
    command_log.configure(state="normal")
    if not command_log.get("1.0", "end-1c").strip():
        command_log.insert("end", "Nama operasi       Modul              Waktu\n")
    command_log.insert("end", baris + "\n")
    jumlah_baris = int(command_log.index("end-1c").split(".")[0])
    if jumlah_baris > MAX_COMMAND_LOG + 1:
        command_log.delete("2.0", f"{jumlah_baris - MAX_COMMAND_LOG + 1}.0")
    command_log.see("end")
    command_log.configure(state="disabled")

def _modul_dari_halaman():
    """Tebak modul dari judul halaman yang sedang tampil."""
    teks = []
    for widget in content.winfo_children():
        if isinstance(widget, tk.Label):
            try:
                teks.append(str(widget.cget("text")).lower())
            except tk.TclError:
                pass
    gabung = " ".join(teks)
    if "linked list" in gabung:
        return "M1 - linked list"
    if "array" in gabung or "load / muat" in gabung or "data pesanan" in gabung:
        return "M1 - array"
    if "queue" in gabung or "antrean" in gabung:
        return "M2 - queue"
    if "stack" in gabung or "postfix" in gabung or "undo" in gabung or "redo" in gabung:
        return "M2 - stack"
    if "search" in gabung or "pencarian" in gabung or "sort" in gabung or "urut" in gabung:
        return "M3 - laporan"
    return "UI - aplikasi"

def _nama_command(teks):
    """Ubah label tombol menjadi nama operasi yang ringkas."""
    label = str(teks or "operation").strip().lower()
    mapping = {
        "load": "load",
        "cari": "search",
        "hitung": "evaluate",
        "enqueue": "queue_enqueue",
        "dequeue": "queue_dequeue",
        "undo": "stack_undo",
        "redo": "stack_redo",
        "tambah pesanan": "array_insert",
        "tambah": "insert",
        "hapus pesanan": "array_delete",
        "hapus": "delete",
        "refresh riwayat": "refresh_history",
        "urutkan": "sort",
    }
    if label in mapping:
        return mapping[label]
    if "array - lihat" in label:
        return "array_get"
    if "linked list" in label and "lihat" in label:
        return "linked_list_get"
    return "_".join(label.replace("-", " ").split())[:24] or "operation"

_tk_button_asli = tk.Button
def _jalankan_dengan_command_log(callback, label_tombol="operation"):
    """Jalankan aksi tombol dan catat durasinya pada panel global."""
    mulai_log = time.perf_counter()
    try:
        return callback()
    finally:
        durasi_log = (time.perf_counter() - mulai_log) * 1000
        catat_command(
            _nama_command(label_tombol),
            _modul_dari_halaman(),
            durasi_log
        )


def _button_dengan_command_log(*args, **kwargs):
    callback = kwargs.get("command")
    label_tombol = kwargs.get("text", "operation")
    if callback is not None and not kwargs.pop("_tanpa_command_log", False):
        kwargs["command"] = lambda: _jalankan_dengan_command_log(
            callback, label_tombol
        )
    return _tk_button_asli(*args, **kwargs)

tk.Button = _button_dengan_command_log
catat_command("application_start", "UI - aplikasi", 0.00)

# ===== JUDUL KELOMPOK MENU =====
def judul_menu(teks):
    tk.Label(
        menu_frame,
        text=teks,
        font=("Segoe UI", 9, "bold"),
        bg=PINK_LIGHT,
        fg=MUTED
    ).pack(anchor="w", padx=12, pady=(12, 4))

# ===== FUNGSI TOMBOL MENU =====
def buat_menu(teks, perintah):
    tombol = tk.Button(
        menu_frame,
        text=teks,
        font=("Segoe UI", 9),
        bg=WHITE,
        fg=TEXT,
        activebackground=PINK,
        activeforeground=WHITE,
        relief="flat",
        anchor="w",
        padx=10,
        pady=6,
        cursor="hand2",
        command=perintah
    )
    tombol.pack(fill="x", padx=8, pady=2)
    return tombol

def muat_data():
    global data_pesanan, array_pesanan, linked_list_pesanan

    try:
        data_csv = baca_pesanan()

        array_pesanan = Array()
        for pesanan in data_csv:
            array_pesanan.tambah(pesanan)

        linked_list_pesanan = LinkedList()
        for pesanan in data_csv:
            linked_list_pesanan.tambah_reguler(pesanan)

        data_pesanan = array_pesanan.lihat()

        bersihkan_konten()

        tk.Label(
            content,
            text="Load / Muat Ulang",
            font=("Segoe UI", 16, "bold"),
            bg=WHITE,
            fg=PINK_DARK
        ).pack(anchor="w", padx=20, pady=(20, 15))

        tk.Button(
            content,
            text="Load",
            font=("Segoe UI", 10, "bold"),
            bg=PINK_DARK,
            fg="white",
            activebackground=PINK,
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=8,
            command=muat_data
        ).pack(anchor="w", padx=20, pady=(0, 15))

        kolom = (
            "id", "pelanggan", "warung", "menu",
            "harga", "jumlah", "status"
        )

        tabel = ttk.Treeview(
            content,
            columns=kolom,
            show="headings"
        )

        judul_kolom = {
            "id": "ID Pesanan",
            "pelanggan": "Pelanggan",
            "warung": "Warung",
            "menu": "Menu",
            "harga": "Harga",
            "jumlah": "Jumlah",
            "status": "Status"
        }

        for kolom_id, judul in judul_kolom.items():
            tabel.heading(kolom_id, text=judul)
            tabel.column(
                kolom_id,
                width=120,
                anchor="center"
            )

        for pesanan in data_csv:
            tabel.insert(
                "",
                tk.END,
                values=(
                    pesanan[0],
                    pesanan[1],
                    pesanan[2],
                    pesanan[3],
                    pesanan[4],
                    pesanan[5],
                    pesanan[8]
                )
            )

        tabel.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 20)
        )

    except Exception as error:
        messagebox.showerror(
            "Gagal Memuat Data",
            f"Data pesanan gagal dimuat.\n\nDetail: {error}"
        )

def tampilkan_pesanan_array():
    bersihkan_konten()

    tk.Label(
        content,
        text="Array: Lihat Pesanan",
        font=("Segoe UI", 18, "bold"),
        bg=WHITE,
        fg=PINK_DARK
    ).pack(anchor="w", padx=20, pady=(20, 5))

    tk.Label(
        content,
        text="Menampilkan data pesanan yang tersimpan dalam Array.",
        font=("Segoe UI", 10),
        bg=WHITE,
        fg=MUTED
    ).pack(anchor="w", padx=20, pady=(0, 12))

    if not data_pesanan:
        tk.Label(
            content,
            text="Belum ada data. Tekan Load terlebih dahulu.",
            font=("Segoe UI", 11),
            bg=WHITE,
            fg=TEXT
        ).pack(anchor="w", padx=20, pady=10)
        return

    info = tk.Label(
        content,
        text=f"Total data: {len(data_pesanan)} | "
             f"Maksimal tampilan: {BATAS_TAMPIL} pesanan",
        font=("Segoe UI", 10, "bold"),
        bg=WHITE,
        fg=PINK
    )
    info.pack(anchor="w", padx=20, pady=(0, 8))


    form_detail = tk.Frame(content, bg=WHITE)
    form_detail.pack(fill="x", padx=20, pady=(0, 12))

    tk.Label(
        form_detail,
        text="Nomor urut pesanan:",
        font=("Segoe UI", 10, "bold"),
        bg=WHITE,
        fg=TEXT
    ).pack(side="left", padx=(0, 8))

    input_nomor = tk.Entry(
        form_detail,
        font=("Segoe UI", 10),
        width=12
    )
    input_nomor.pack(side="left", ipady=4)

    hasil_detail = tk.Label(
        content,
        text="Masukkan nomor urut untuk melihat detail pesanan.",
        font=("Consolas", 10),
        bg=WHITE,
        fg=TEXT,
        justify="left",
        anchor="w"
    )
    hasil_detail.pack(fill="x", padx=20, pady=(0, 12))

    tk.Button(
        form_detail,
        text="Lihat Detail",
        font=("Segoe UI", 9, "bold"),
        bg=PINK,
        fg=WHITE,
        activebackground=PINK_HOVER,
        activeforeground=WHITE,
        relief="flat",
        cursor="hand2",
        command=lambda: lihat_detail_pesanan(
            input_nomor, hasil_detail
        )
    ).pack(side="left", padx=8)

    frame_tabel = tk.Frame(content, bg=WHITE)
    frame_tabel.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    kolom = (
        "oid", "customer", "warung",
        "menu", "harga", "status"
    )

    tabel = ttk.Treeview(
        frame_tabel,
        columns=kolom,
        show="headings"
    )

    judul_kolom = {
        "oid": "ID Pesanan",
        "customer": "Pelanggan",
        "warung": "Warung",
        "menu": "Menu",
        "harga": "Harga",
        "status": "Status"
    }

    lebar_kolom = {
        "oid": 110,
        "customer": 180,
        "warung": 130,
        "menu": 140,
        "harga": 100,
        "status": 100
    }

    for kolom_id in kolom:
        tabel.heading(kolom_id, text=judul_kolom[kolom_id])
        tabel.column(
            kolom_id,
            width=lebar_kolom[kolom_id],
            anchor="w"
        )

    scrollbar = ttk.Scrollbar(
        frame_tabel,
        orient="vertical",
        command=tabel.yview
    )
    tabel.configure(yscrollcommand=scrollbar.set)

    tabel.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    for pesanan in data_pesanan[:BATAS_TAMPIL]:
        tabel.insert(
            "",
            "end",
            values=(
                pesanan[0],
                pesanan[1],
                pesanan[2],
                pesanan[3],
                pesanan[4],
                pesanan[8]
            )
        )
def lihat_detail_pesanan(input_nomor, hasil_detail):
    if not data_pesanan:
        messagebox.showwarning(
            "Data Kosong",
            "Tekan Load terlebih dahulu."
        )
        return

    nomor = input_nomor.get().strip()

    if not nomor.isdigit():
        messagebox.showwarning(
            "Input Tidak Valid",
            "Masukkan nomor urut berupa angka."
        )
        return

    indeks = int(nomor)

    if indeks < 1 or indeks > array_pesanan.size:
        messagebox.showwarning(
            "Pesanan Tidak Ditemukan",
            f"Masukkan nomor 1 sampai {array_pesanan.size}."
        )
        return

    pesanan = array_pesanan.lihat(indeks - 1)

    hasil_detail.config(
        text=(
            f"ID Pesanan   : {pesanan[0]}\n"
            f"Pelanggan    : {pesanan[1]}\n"
            f"Warung       : {pesanan[2]}\n"
            f"Menu         : {pesanan[3]}\n"
            f"Harga        : Rp{pesanan[4]}\n"
            f"Jumlah       : {pesanan[5]}\n"
            f"Waktu Masuk  : {format_waktu_detik(pesanan[6])}\n"
            f"Waktu Selesai: {format_waktu_detik(pesanan[7]) or '-'}\n"
            f"Status       : {pesanan[8]}"
        )
    )

def buat_id_pesanan():
    nomor_terbesar = 0
    for pesanan in data_pesanan:
        try:
            nomor = int(pesanan[0].replace("O-", ""))
            if nomor > nomor_terbesar:
                nomor_terbesar = nomor
        except (ValueError, IndexError):
            continue
    return f"O-{nomor_terbesar + 1:06d}"


def _form_tambah_pesanan(struktur, jenis):
    """Form tambah pesanan bersama untuk Array dan Linked List."""
    global data_pesanan

    is_array = struktur == "Array"
    koleksi = array_pesanan if is_array else linked_list_pesanan
    posisi_teks = {"Reguler": "belakang", "Prioritas": "tengah", "VIP": "depan"}[jenis]
    bersihkan_konten()

    tk.Label(content, text=f"{struktur}: Tambah Pesanan {jenis}",
             font=("Segoe UI", 18, "bold"), bg=WHITE, fg=PINK_DARK).pack(
                 anchor="w", padx=20, pady=(20, 5))
    tk.Label(content,
             text=f"Pesanan {jenis.lower()} akan ditempatkan di bagian {('paling ' if jenis != 'Prioritas' else '')}{posisi_teks} {struktur}.",
             font=("Segoe UI", 10), bg=WHITE, fg=MUTED).pack(
                 anchor="w", padx=20, pady=(0, 15))

    form = tk.Frame(content, bg=WHITE)
    form.pack(fill="x", padx=20)
    kolom = [("Nama pelanggan", "customer"), ("Nama warung", "warung"),
             ("Nama menu", "menu"), ("Harga (Rp)", "harga"), ("Jumlah", "jumlah")]
    input_data = {}
    for label_teks, nama_kolom in kolom:
        baris = tk.Frame(form, bg=WHITE)
        baris.pack(fill="x", pady=6)
        tk.Label(baris, text=label_teks, font=("Segoe UI", 10), bg=WHITE,
                 fg=TEXT, width=18, anchor="w").pack(side="left")
        entry = tk.Entry(baris, font=("Segoe UI", 10), width=35)
        entry.pack(side="left", ipady=4)
        input_data[nama_kolom] = entry

    def simpan():
        global data_pesanan
        if not data_pesanan:
            messagebox.showwarning("Data Belum Dimuat", "Tekan Load terlebih dahulu sebelum menambah pesanan.")
            return

        nilai = {k: entry.get().strip() for k, entry in input_data.items()}
        if not all(nilai.values()):
            messagebox.showwarning("Data Belum Lengkap", "Semua kolom harus diisi.")
            return
        try:
            harga, jumlah = int(nilai["harga"]), int(nilai["jumlah"])
            if harga <= 0 or jumlah <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Input Tidak Valid", "Harga dan jumlah harus berupa bilangan bulat positif.")
            return

        pesanan = [buat_id_pesanan(), nilai["customer"], nilai["warung"], nilai["menu"],
                str(harga), str(jumlah), "0", "", "PENDING"]

        ukuran_awal = koleksi.size

        getattr(koleksi, {
            "Reguler": "tambah_reguler",
            "Prioritas": "tambah_prioritas",
            "VIP": "tambah_vip"
        }[jenis])(pesanan)

        # Catat aksi tambah ke stack Undo
        antrean_undo.enqueue(pesanan)

        data_pesanan = koleksi.lihat()


        if jenis == "Prioritas" and is_array:
            posisi = ukuran_awal // 2
            if koleksi.size != ukuran_awal + 1 or koleksi.lihat(posisi) != pesanan:
                messagebox.showerror("Gagal", "Pesanan prioritas tidak masuk ke posisi yang diharapkan.")
                return
            pesan = f"Pesanan {pesanan[0]} berhasil ditambahkan!\nPosisi sisip: indeks {posisi}."
        elif jenis == "VIP":
            if koleksi.size != ukuran_awal + 1 or (is_array and koleksi.lihat(0) != pesanan):
                messagebox.showerror("Gagal", "Pesanan VIP gagal ditambahkan pada posisi yang diharapkan.")
                return
            pesan = (f"Pesanan VIP {pesanan[0]} berhasil ditempatkan di depan Array."
                     if is_array else f"Pesanan VIP {pesanan[0]} berhasil ditambahkan.")
        else:
            tempat = "belakang" if jenis == "Reguler" else "tengah"
            pesan = f"Pesanan {pesanan[0]} berhasil ditambahkan ke {tempat} {struktur}."

        messagebox.showinfo("Berhasil", pesan)
        (tampilkan_pesanan_array if is_array else tampilkan_pesanan_linked_list)()

    tk.Button(content, text=f"Tambah Pesanan {jenis}", font=("Segoe UI", 10, "bold"),
              bg=PINK, fg=WHITE, activebackground=PINK_HOVER, activeforeground=WHITE,
              relief="flat", cursor="hand2", command=simpan).pack(
                  anchor="w", padx=20, pady=18)


def tambah_pesanan_reguler():
    _form_tambah_pesanan("Array", "Reguler")


def tambah_pesanan_prioritas():
    _form_tambah_pesanan("Array", "Prioritas")


def tambah_pesanan_vip():
    _form_tambah_pesanan("Array", "VIP")


def tampilkan_stack_postfix():
    bersihkan_konten()

    tk.Label(
        content,
        text="Stack: hitung struk lewat postfix",
        font=("Segoe UI", 12, "bold"),
        bg=WHITE,
        fg="#263442"
    ).pack(anchor="w", padx=12, pady=(8, 2))

    tk.Label(
        content,
        text="Struk ditulis infix, lalu dihitung dua tahap dengan stack: tahap 1 infix menjadi postfix, tahap 2 postfix dievaluasi.",
        font=("Segoe UI", 8),
        bg=WHITE,
        fg=TEXT
    ).pack(anchor="w", padx=12, pady=(0, 7))

    tk.Label(
        content,
        text="Struk belanja (infix)",
        font=("Segoe UI", 8, "bold"),
        bg=WHITE,
        fg=TEXT
    ).pack(anchor="w", padx=12)

    baris_input = tk.Frame(content, bg=WHITE)
    baris_input.pack(fill="x", padx=12, pady=(3, 4))

    input_ekspresi = tk.Entry(
        baris_input,
        font=("Consolas", 9),
        relief="solid",
        bd=1
    )
    input_ekspresi.pack(
        side="left",
        fill="x",
        expand=True,
        ipady=2
    )
    input_ekspresi.insert(
        0, "(3 * 12000) + (2 * 8500) - 5000"
    )

    tombol_hitung = tk.Button(
        baris_input,
        text="HITUNG",
        font=("Segoe UI", 8, "bold"),
        bg="#294967",
        fg=WHITE,
        activebackground="#1b3046",
        activeforeground=WHITE,
        relief="flat",
        cursor="hand2",
        width=12
    )
    tombol_hitung.pack(side="left", padx=(10, 0), ipady=2)

    tk.Label(
        content,
        text="angka, +, -, *, / dan tanda kurung; 3 x Rp12.000 dan 2 x Rp8.500, potongan Rp5.000",
        font=("Segoe UI", 7),
        bg=WHITE,
        fg=MUTED
    ).pack(anchor="w", padx=12, pady=(0, 5))

    hasil = tk.Text(
        content,
        height=3,
        font=("Consolas", 8),
        bg=WHITE,
        fg=TEXT,
        relief="flat",
        wrap="word"
    )
    hasil.pack(fill="x", padx=12, pady=(2, 4))
    hasil.insert(
        "end",
        "Struk : (3 * 12000) + (2 * 8500) - 5000\n"
        "Postfix: 3 12000 * 2 8500 * + 5000 -\n"
        "TOTAL : Rp 48.000"
    )
    hasil.config(state="disabled")

    frame_tabel = tk.Frame(content, bg=WHITE)
    frame_tabel.pack(
        fill="both",
        expand=True,
        padx=12,
        pady=(0, 4)
    )

    kolom = ("langkah", "token", "tindakan", "stack", "output")

    tabel = ttk.Treeview(
        frame_tabel,
        columns=kolom,
        show="headings"
    )

    judul = {
        "langkah": "langkah",
        "token": "token",
        "tindakan": "tindakan",
        "stack": "stack",
        "output": "output"
    }

    lebar = {
        "langkah": 55,
        "token": 45,
        "tindakan": 210,
        "stack": 75,
        "output": 105
    }

    for nama in kolom:
        tabel.heading(nama, text=judul[nama])
        tabel.column(
            nama,
            width=lebar[nama],
            minwidth=40,
            anchor="w",
            stretch=(nama == "tindakan")
        )

    scroll_y = ttk.Scrollbar(
        frame_tabel,
        orient="vertical",
        command=tabel.yview
    )
    tabel.configure(yscrollcommand=scroll_y.set)

    tabel.pack(side="left", fill="both", expand=True)
    scroll_y.pack(side="right", fill="y")

    catatan = tk.Label(
        content,
        text=(
            "Baris 1.x adalah tahap konversi, baris 2.x tahap evaluasi. "
            "Tahap 1 menahan operator di stack sampai gilirannya tiba. "
            "Tahap 2 menumpuk angka, dan setiap operator mengambil dua nilai teratas. "
            "Operan kanan selalu keluar lebih dulu."
        ),
        font=("Segoe UI", 7),
        bg="#eef1f5",
        fg=TEXT,
        justify="left",
        wraplength=850,
        anchor="w",
        padx=5,
        pady=4
    )
    catatan.pack(fill="x", padx=12, pady=(0, 5))

    def proses_hitung():
        ekspresi = input_ekspresi.get().strip()

        if not ekspresi:
            messagebox.showwarning(
                "Input Kosong",
                "Masukkan ekspresi struk terlebih dahulu."
            )
            return

        try:
            postfix = ke_postfix(ekspresi)
            total = hitung(postfix)

            hasil.config(state="normal")
            hasil.delete("1.0", "end")
            hasil.insert(
                "end",
                f"Struk : {ekspresi}\n"
                f"Postfix: {postfix}\n"
                f"TOTAL : Rp {total:,.0f}".replace(",", ".")
            )
            hasil.config(state="disabled")

            for item in tabel.get_children():
                tabel.delete(item)

            tokens = ekspresi.replace("(", " ( ").replace(")", " ) ").split()
            stack = []
            output = []
            nomor = 0
            prioritas = {"+": 1, "-": 1, "*": 2, "/": 2}
            operator = set(prioritas)

            def tambah_baris(tahap, token, tindakan):
                nonlocal nomor
                nomor += 1
                tabel.insert(
                    "",
                    "end",
                    values=(
                        tahap,
                        token,
                        tindakan,
                        " ".join(stack) if stack else "kosong",
                        " ".join(output) if output else "kosong"
                    )
                )

            for token in tokens:
                tahap = f"1.{nomor + 1}"

                if token.isdigit():
                    output.append(token)
                    tambah_baris(tahap, token, "operand, langsung ke output")

                elif token == "(":
                    stack.append(token)
                    tambah_baris(tahap, token, "push ( ke stack")

                elif token == ")":
                    while stack and stack[-1] != "(":
                        output.append(stack.pop())
                    if stack and stack[-1] == "(":
                        stack.pop()
                    tambah_baris(tahap, token, "pop sampai (, lalu buang (")

                elif token in operator:
                    while (
                        stack
                        and stack[-1] != "("
                        and prioritas[stack[-1]] >= prioritas[token]
                    ):
                        output.append(stack.pop())

                    stack.append(token)
                    tambah_baris(tahap, token, "push operator ke stack")

            while stack:
                output.append(stack.pop())
                tambah_baris(
                    f"1.{nomor + 1}",
                    "akhir",
                    "pop sisa operator"
                )

            stack = []
            nomor_evaluasi = 0

            for token in postfix.split():
                nomor_evaluasi += 1
                tahap = f"2.{nomor_evaluasi}"

                if token.isdigit():
                    stack.append(int(token))
                    tabel.insert(
                        "",
                        "end",
                        values=(
                            tahap, token, f"operand, push {token}",
                            " ".join(map(str, stack)), ""
                        )
                    )
                else:
                    b = stack.pop()
                    a = stack.pop()

                    if token == "+":
                        nilai = a + b
                    elif token == "-":
                        nilai = a - b
                    elif token == "*":
                        nilai = a * b
                    else:
                        nilai = a / b

                    stack.append(nilai)

                    tabel.insert(
                        "",
                        "end",
                        values=(
                            tahap, token,
                            f"pop {a} dan {b}, hitung {a} {token} {b}",
                            " ".join(map(str, stack)),
                            str(nilai)
                        )
                    )

            if tabel.get_children():
                tabel.see(tabel.get_children()[-1])

        except (ValueError, ZeroDivisionError, IndexError) as error:
            messagebox.showerror(
                "Ekspresi Tidak Valid",
                str(error)
            )

    tombol_hitung.config(command=lambda: _jalankan_dengan_command_log(proses_hitung, "HITUNG"))


def tampilkan_stack_undo():
    bersihkan_konten()

    tk.Label(
        content,
        text="Stack: Undo Aksi Antrean",
        font=("Segoe UI", 12, "bold"),
        bg=WHITE,
        fg=PINK_DARK
    ).pack(anchor="w", padx=12, pady=(8, 2))

    tk.Label(
        content,
        text="Batalkan aksi terakhir yang masih tercatat pada stack undo.",
        font=("Segoe UI", 8),
        bg=WHITE,
        fg=MUTED
    ).pack(anchor="w", padx=12, pady=(0, 10))

    tombol = tk.Frame(content, bg=WHITE)
    tombol.pack(anchor="w", padx=12, pady=(0, 10))

    frame_tabel = tk.Frame(content, bg=WHITE)
    frame_tabel.pack(
        fill="both",
        expand=True,
        padx=12,
        pady=(0, 8)
    )

    kolom = ("nomor", "oid", "pelanggan", "resto", "menu")

    tabel = ttk.Treeview(
        frame_tabel,
        columns=kolom,
        show="headings",
        height=10
    )

    tabel.heading("nomor", text="#")
    tabel.heading("oid", text="oid")
    tabel.heading("pelanggan", text="pelanggan")
    tabel.heading("resto", text="resto")
    tabel.heading("menu", text="menu")

    tabel.column("nomor", width=35, anchor="center")
    tabel.column("oid", width=100, anchor="center")
    tabel.column("pelanggan", width=130, anchor="center")
    tabel.column("resto", width=120, anchor="center")
    tabel.column("menu", width=120, anchor="center")

    scrollbar_y = ttk.Scrollbar(
        frame_tabel,
        orient="vertical",
        command=tabel.yview
    )
    scrollbar_x = ttk.Scrollbar(
        frame_tabel,
        orient="horizontal",
        command=tabel.xview
    )

    tabel.configure(
        yscrollcommand=scrollbar_y.set,
        xscrollcommand=scrollbar_x.set
    )

    tabel.grid(row=0, column=0, sticky="nsew")
    scrollbar_y.grid(row=0, column=1, sticky="ns")
    scrollbar_x.grid(row=1, column=0, sticky="ew")

    frame_tabel.grid_rowconfigure(0, weight=1)
    frame_tabel.grid_columnconfigure(0, weight=1)

    status = tk.Label(
        content,
        text="",
        font=("Segoe UI", 9),
        bg=WHITE,
        fg=TEXT,
        anchor="w"
    )
    status.pack(fill="x", padx=12, pady=(0, 8))

    def perbarui_tampilan(pesan=""):
        for item in tabel.get_children():
            tabel.delete(item)

        riwayat = antrean_undo.history()
        
        for nomor, aksi in enumerate(riwayat, start=1):
            oid = "-"
            pelanggan = "-"
            resto = "-"
            menu = "-"

            if isinstance(aksi, (tuple, list)) and len(aksi) >= 2:
                pesanan = aksi[1]

                # Format aksi ENQUEUE: ("ENQUEUE", pesanan)
                if isinstance(pesanan, (tuple, list)) and len(pesanan) >= 4:
                    oid = pesanan[0]
                    pelanggan = pesanan[1]
                    resto = pesanan[2]
                    menu = pesanan[3]

                # Format aksi DEQUEUE: ("DEQUEUE", [pesanan])
                elif isinstance(pesanan, (tuple, list)) and len(pesanan) > 0:
                    data = pesanan[0]

                    if isinstance(data, (tuple, list)) and len(data) >= 4:
                        oid = data[0]
                        pelanggan = data[1]
                        resto = data[2]
                        menu = data[3]

            tabel.insert(
                "",
                "end",
                values=(nomor, oid, pelanggan, resto, menu)
            )



        status.config(
            text=f"Total aksi yang dapat dibatalkan: {len(riwayat)}"
        )


    def proses_undo():
        riwayat = antrean_undo.history()

        if not riwayat:
            messagebox.showinfo(
                "Undo Kosong",
                "Tidak ada aksi yang dapat dibatalkan."
            )
            perbarui_tampilan("Undo tidak dijalankan: stack kosong.")
            return

        try:
            hasil_undo = antrean_undo.undo_last()
        except (IndexError, ValueError) as error:
            messagebox.showerror("Undo Gagal", str(error))
            perbarui_tampilan("Undo gagal.")
            return

        perbarui_tampilan(
            f"Undo berhasil. Hasil: {hasil_undo}"
        )

        messagebox.showinfo(
            "Undo Berhasil",
            f"Aksi terakhir berhasil dibatalkan.\nHasil: {hasil_undo}"
        )

    tk.Button(
        tombol,
        text="UNDO",
        font=("Segoe UI", 9, "bold"),
        bg=PINK,
        fg=WHITE,
        activebackground=PINK_HOVER,
        activeforeground=WHITE,
        relief="flat",
        cursor="hand2",
        command=proses_undo
    ).pack(side="left", padx=(0, 8))

    tk.Button(
        tombol,
        text="Refresh Riwayat",
        font=("Segoe UI", 9, "bold"),
        bg=PINK_LIGHT,
        fg=PINK_DARK,
        activebackground=BORDER,
        relief="flat",
        cursor="hand2",
        command=lambda: perbarui_tampilan()
    ).pack(side="left")

    perbarui_tampilan()


def tampilkan_stack_redo():
    bersihkan_konten()

    tk.Label(
        content,
        text="Stack: Redo Aksi Antrean",
        font=("Segoe UI", 12, "bold"),
        bg=WHITE,
        fg=PINK_DARK
    ).pack(anchor="w", padx=12, pady=(8, 2))

    tk.Label(
        content,
        text="Ulangi aksi antrean yang sebelumnya dibatalkan melalui Undo.",
        font=("Segoe UI", 8),
        bg=WHITE,
        fg=MUTED
    ).pack(anchor="w", padx=12, pady=(0, 10))

    tombol = tk.Frame(content, bg=WHITE)
    tombol.pack(anchor="w", padx=12, pady=(0, 8))


    tk.Label(
        content,
        text="Data Antrean",
        font=("Segoe UI", 9, "bold"),
        bg=WHITE,
        fg=TEXT
    ).pack(anchor="w", padx=12, pady=(0, 4))

    frame_tabel = tk.Frame(content, bg=WHITE)
    frame_tabel.pack(
        fill="both",
        expand=True,
        padx=12,
        pady=(0, 8)
    )

    kolom = ("nomor", "oid", "pelanggan", "resto", "menu")

    tabel = ttk.Treeview(
        frame_tabel,
        columns=kolom,
        show="headings",
        height=10
    )

    tabel.heading("nomor", text="#")
    tabel.heading("oid", text="oid")
    tabel.heading("pelanggan", text="pelanggan")
    tabel.heading("resto", text="resto")
    tabel.heading("menu", text="menu")

    tabel.column("nomor", width=35, anchor="center")
    tabel.column("oid", width=100, anchor="center")
    tabel.column("pelanggan", width=130, anchor="center")
    tabel.column("resto", width=120, anchor="center")
    tabel.column("menu", width=120, anchor="center")

    scrollbar_y = ttk.Scrollbar(
        frame_tabel,
        orient="vertical",
        command=tabel.yview
    )

    scrollbar_x = ttk.Scrollbar(
        frame_tabel,
        orient="horizontal",
        command=tabel.xview
    )

    tabel.configure(
        yscrollcommand=scrollbar_y.set,
        xscrollcommand=scrollbar_x.set
    )

    tabel.grid(row=0, column=0, sticky="nsew")
    scrollbar_y.grid(row=0, column=1, sticky="ns")
    scrollbar_x.grid(row=1, column=0, sticky="ew")

    frame_tabel.grid_rowconfigure(0, weight=1)
    frame_tabel.grid_columnconfigure(0, weight=1)

    status = tk.Label(
        content,
        text="",
        font=("Segoe UI", 9),
        bg=WHITE,
        fg=TEXT,
        anchor="w"
    )
    status.pack(fill="x", padx=12, pady=(0, 8))

    keterangan = tk.Label(
        content,
        text=(
            "Redo mengulangi aksi yang sebelumnya dibatalkan "
            "melalui Undo. Jika belum ada Undo, tidak ada aksi "
            "yang dapat diulang."
        ),
        font=("Segoe UI", 8),
        bg="#eef1f5",
        fg=TEXT,
        anchor="w",
        justify="left",
        padx=8,
        pady=6,
        wraplength=750
    )
    keterangan.pack(fill="x", padx=12, pady=(0, 8))

    def perbarui_tampilan(pesan=""):
        for item in tabel.get_children():
            tabel.delete(item)

        riwayat_redo = antrean_undo.redo_stack.data.copy()

        for nomor, aksi in enumerate(reversed(riwayat_redo), start=1):
            oid = "-"
            pelanggan = "-"
            resto = "-"
            menu = "-"

            if isinstance(aksi, (tuple, list)) and len(aksi) >= 2:
                pesanan = aksi[1]

                if isinstance(pesanan, (tuple, list)) and len(pesanan) >= 4:
                    oid = str(pesanan[0])
                    pelanggan = str(pesanan[1])
                    resto = str(pesanan[2])
                    menu = str(pesanan[3])

                elif isinstance(pesanan, (tuple, list)) and len(pesanan) > 0:
                    data = pesanan[0]

                    if isinstance(data, (tuple, list)) and len(data) >= 4:
                        oid = str(data[0])
                        pelanggan = str(data[1])
                        resto = str(data[2])
                        menu = str(data[3])

            tabel.insert(
                "",
                "end",
                values=(nomor, oid, pelanggan, resto, menu)
            )


        status.config(
            text=(
                "Total aksi yang dapat diulang: "
                f"{len(riwayat_redo)}"
            )
        )


    def proses_redo():
        try:
            hasil = antrean_undo.redo_last()
        except (IndexError, ValueError) as error:
            messagebox.showerror("Redo Gagal", str(error))
            perbarui_tampilan("Redo gagal.")
            return

        if hasil is None:
            perbarui_tampilan(
                "Redo tidak dijalankan: stack redo kosong."
            )
            messagebox.showinfo(
                "Redo Kosong",
                "Tidak ada aksi yang dapat diulang. "
                "Lakukan Undo terlebih dahulu."
            )
            return

        perbarui_tampilan(f"Redo berhasil. Hasil: {hasil}")

        messagebox.showinfo(
            "Redo Berhasil",
            f"Aksi berhasil diulang.\nHasil: {hasil}"
        )

    tk.Button(
        tombol,
        text="REDO",
        font=("Segoe UI", 9, "bold"),
        bg=PINK,
        fg=WHITE,
        activebackground=PINK_HOVER,
        activeforeground=WHITE,
        relief="flat",
        cursor="hand2",
        command=proses_redo
    ).pack(side="left", padx=(0, 8))

    tk.Button(
        tombol,
        text="Refresh Riwayat",
        font=("Segoe UI", 9, "bold"),
        bg=PINK_LIGHT,
        fg=PINK_DARK,
        activebackground=BORDER,
        relief="flat",
        cursor="hand2",
        command=lambda: perbarui_tampilan()
    ).pack(side="left")

    perbarui_tampilan()

def bersihkan_konten():
    for widget in content.winfo_children():
        widget.destroy()

def tambah_pesanan_reguler_linked_list():
    _form_tambah_pesanan("Linked List", "Reguler")


def tambah_pesanan_prioritas_linked_list():
    _form_tambah_pesanan("Linked List", "Prioritas")


def tambah_pesanan_vip_linked_list():
    _form_tambah_pesanan("Linked List", "VIP")


# ===== LINKED LIST - HAPUS PESANAN =====
def hapus_pesanan_linked_list():
    bersihkan_konten()

    tk.Label(
        content,
        text="Linked List: Hapus Pesanan",
        font=("Segoe UI", 18, "bold"),
        bg=WHITE,
        fg=PINK_DARK
    ).pack(anchor="w", padx=20, pady=(20, 5))

    tk.Label(
        content,
        text="Masukkan indeks pesanan yang ingin dihapus (dimulai dari 0).",
        font=("Segoe UI", 10),
        bg=WHITE,
        fg=MUTED
    ).pack(anchor="w", padx=20, pady=(0, 15))

    tk.Label(
        content,
        text=f"Total pesanan: {linked_list_pesanan.size}",
        font=("Segoe UI", 10, "bold"),
        bg=WHITE,
        fg=PINK
    ).pack(anchor="w", padx=20, pady=(0, 10))

    form = tk.Frame(content, bg=WHITE)
    form.pack(fill="x", padx=20)

    tk.Label(
        form,
        text="Indeks pesanan",
        font=("Segoe UI", 10),
        bg=WHITE,
        fg=TEXT,
        width=18,
        anchor="w"
    ).pack(side="left")

    input_indeks = tk.Entry(form, font=("Segoe UI", 10), width=20)
    input_indeks.pack(side="left", ipady=4)

    def proses_hapus():
        if linked_list_pesanan.size == 0:
            messagebox.showwarning(
                "Linked List Kosong",
                "Tidak ada pesanan yang dapat dihapus."
            )
            return

        try:
            indeks = int(input_indeks.get().strip())
        except ValueError:
            messagebox.showwarning(
                "Input Tidak Valid",
                "Indeks harus berupa bilangan bulat."
            )
            return

        pesanan = linked_list_pesanan.lihat(indeks)

        if pesanan is None:
            messagebox.showwarning(
                "Indeks Tidak Valid",
                f"Masukkan indeks 0 sampai {linked_list_pesanan.size - 1}."
            )
            return

        konfirmasi = messagebox.askyesno(
            "Konfirmasi Hapus",
            f"Yakin menghapus pesanan ini?\n\n"
            f"ID: {pesanan[0]}\n"
            f"Pelanggan: {pesanan[1]}\n"
            f"Menu: {pesanan[3]}"
        )

        if not konfirmasi:
            return

        berhasil = linked_list_pesanan.hapus(indeks)

        if berhasil:
            messagebox.showinfo(
                "Berhasil",
                f"Pesanan {pesanan[0]} berhasil dihapus."
            )
            tampilkan_pesanan_linked_list()
        else:
            messagebox.showerror(
                "Gagal",
                "Pesanan gagal dihapus."
            )

    tk.Button(
        content,
        text="Hapus Pesanan",
        font=("Segoe UI", 10, "bold"),
        bg=PINK,
        fg=WHITE,
        activebackground=PINK_HOVER,
        activeforeground=WHITE,
        relief="flat",
        cursor="hand2",
        command=proses_hapus
    ).pack(anchor="w", padx=20, pady=18)

def hapus_pesanan_array():
    bersihkan_konten()

    tk.Label(
        content,
        text="Array: Hapus Pesanan",
        font=("Segoe UI", 18, "bold"),
        bg=WHITE,
        fg=PINK_DARK
    ).pack(anchor="w", padx=20, pady=(20, 5))

    tk.Label(
        content,
        text="Masukkan indeks pesanan yang ingin dihapus. Indeks dimulai dari 0.",
        font=("Segoe UI", 10),
        bg=WHITE,
        fg=MUTED
    ).pack(anchor="w", padx=20, pady=(0, 15))

    form = tk.Frame(content, bg=WHITE)
    form.pack(fill="x", padx=20)

    tk.Label(
        form,
        text="Indeks pesanan",
        font=("Segoe UI", 10),
        bg=WHITE,
        fg=TEXT,
        width=18,
        anchor="w"
    ).pack(side="left")

    input_indeks = tk.Entry(
        form,
        font=("Segoe UI", 10),
        width=20
    )
    input_indeks.pack(side="left", ipady=4)

    def proses_hapus():
        global data_pesanan

        if not data_pesanan:
            messagebox.showwarning(
                "Data Belum Dimuat",
                "Tekan Load terlebih dahulu sebelum menghapus pesanan."
            )
            return

        indeks = input_indeks.get().strip()

        try:
            indeks = int(indeks)
        except ValueError:
            messagebox.showwarning(
                "Input Tidak Valid",
                "Indeks harus berupa bilangan bulat."
            )
            return

        if indeks < 0 or indeks >= array_pesanan.size:
            messagebox.showwarning(
                "Indeks Tidak Valid",
                f"Masukkan indeks antara 0 sampai {array_pesanan.size - 1}."
            )
            return

        pesanan_dihapus = array_pesanan.lihat(indeks)

        konfirmasi = messagebox.askyesno(
            "Konfirmasi Hapus",
            f"Yakin ingin menghapus pesanan berikut?\n\n"
            f"ID: {pesanan_dihapus[0]}\n"
            f"Pelanggan: {pesanan_dihapus[1]}\n"
            f"Menu: {pesanan_dihapus[3]}"
        )

        if not konfirmasi:
            return

        berhasil = array_pesanan.hapus(indeks)

        if berhasil:
            data_pesanan = array_pesanan.lihat()

            print("BERHASIL: Pesanan berhasil dihapus dari Array.")
            print("Indeks yang dihapus:", indeks)
            print("ID pesanan dihapus:", pesanan_dihapus[0])
            print("Jumlah pesanan sekarang:", array_pesanan.size)

            messagebox.showinfo(
                "Berhasil",
                f"Pesanan {pesanan_dihapus[0]} berhasil dihapus."
            )

            tampilkan_pesanan_array()
        else:
            messagebox.showerror(
                "Gagal",
                "Pesanan gagal dihapus."
            )

    tk.Button(
        content,
        text="Hapus Pesanan",
        font=("Segoe UI", 10, "bold"),
        bg=PINK,
        fg=WHITE,
        activebackground=PINK_HOVER,
        activeforeground=WHITE,
        relief="flat",
        cursor="hand2",
        command=proses_hapus
    ).pack(anchor="w", padx=20, pady=18)

def tampilkan_pesanan_linked_list():
    bersihkan_konten()

    tk.Label(
        content,
        text="Linked List: Lihat Pesanan",
        font=("Segoe UI", 18, "bold"),
        bg=WHITE,
        fg=PINK_DARK
    ).pack(anchor="w", padx=20, pady=(20, 5))

    tk.Label(
        content,
        text="Pilih salah satu pesanan untuk melihat detail lengkapnya.",
        font=("Segoe UI", 10),
        bg=WHITE,
        fg=MUTED
    ).pack(anchor="w", padx=20, pady=(0, 10))


    form_detail = tk.Frame(content, bg=WHITE)
    form_detail.pack(fill="x", padx=20, pady=(10, 12))

    tk.Label(
        form_detail,
        text="Nomor urut pesanan:",
        font=("Segoe UI", 10, "bold"),
        bg=WHITE,
        fg=TEXT
    ).pack(side="left", padx=(0, 8))

    input_nomor = tk.Entry(
        form_detail,
        font=("Segoe UI", 10),
        width=12
    )
    input_nomor.pack(side="left", ipady=4)

    hasil_detail = tk.Label(
        content,
        text="Masukkan nomor urut untuk melihat detail pesanan.",
        font=("Consolas", 10),
        bg=WHITE,
        fg=TEXT,
        justify="left",
        anchor="w"
    )
    hasil_detail.pack(fill="x", padx=20, pady=(0, 12))

    def lihat_detail_linked_list():
        nomor = input_nomor.get().strip()

        try:
            indeks = int(nomor)
        except ValueError:
            messagebox.showwarning(
                "Input Tidak Valid",
                "Nomor urut harus berupa bilangan bulat."
            )
            return

        pesanan = linked_list_pesanan.lihat(indeks)

        if pesanan is None:
            messagebox.showwarning(
                "Pesanan Tidak Ditemukan",
                f"Masukkan indeks antara 0 sampai "
                f"{linked_list_pesanan.size - 1}."
            )
            return

        hasil_detail.config(
            text=(
                f"Indeks         : {indeks}\n"
                f"ID Pesanan     : {pesanan[0]}\n"
                f"Nama Pelanggan : {pesanan[1]}\n"
                f"Nama Warung    : {pesanan[2]}\n"
                f"Nama Menu      : {pesanan[3]}\n"
                f"Harga          : Rp{pesanan[4]}\n"
                f"Jumlah         : {pesanan[5]}\n"
                f"Waktu Masuk    : {format_waktu_detik(pesanan[6])}\n"
                f"Waktu Selesai  : {format_waktu_detik(pesanan[7]) or '-'}\n"
                f"Status         : {pesanan[8]}"
            ),
            fg=TEXT
        )

    tk.Button(
        form_detail,
        text="Lihat Detail",
        font=("Segoe UI", 9, "bold"),
        bg=PINK,
        fg=WHITE,
        activebackground=PINK_HOVER,
        activeforeground=WHITE,
        relief="flat",
        cursor="hand2",
        command=lihat_detail_linked_list
    ).pack(side="left", padx=8)

    if linked_list_pesanan.size == 0:
        tk.Label(
            content,
            text="Belum ada data. Tekan Load terlebih dahulu.",
            font=("Segoe UI", 11),
            bg=WHITE,
            fg=TEXT
        ).pack(anchor="w", padx=20, pady=10)
        return

    semua_pesanan = linked_list_pesanan.lihat()

    tk.Label(
        content,
        text=(
            f"Total pesanan: {linked_list_pesanan.size} | "
            f"Menampilkan maksimal {BATAS_TAMPIL} pesanan"
        ),
        font=("Segoe UI", 10, "bold"),
        bg=WHITE,
        fg=TEXT
    ).pack(anchor="w", padx=20, pady=(0, 8))

    area_tabel = tk.Frame(content, bg=WHITE)
    area_tabel.pack(fill="both", expand=True, padx=20)

    kolom = (
        "indeks", "id", "customer", "warung",
        "menu", "harga", "jumlah", "status"
    )

    tabel = ttk.Treeview(
        area_tabel,
        columns=kolom,
        show="headings",
        height=12
    )

    judul_kolom = {
        "indeks": "Indeks",
        "id": "ID Pesanan",
        "customer": "Pelanggan",
        "warung": "Warung",
        "menu": "Menu",
        "harga": "Harga",
        "jumlah": "Jumlah",
        "status": "Status"
    }

    lebar_kolom = {
        "indeks": 55,
        "id": 105,
        "customer": 150,
        "warung": 130,
        "menu": 130,
        "harga": 85,
        "jumlah": 65,
        "status": 85
    }

    for nama_kolom in kolom:
        tabel.heading(
            nama_kolom,
            text=judul_kolom[nama_kolom]
        )
        tabel.column(
            nama_kolom,
            width=lebar_kolom[nama_kolom],
            anchor="w"
        )

    scrollbar = ttk.Scrollbar(
        area_tabel,
        orient="vertical",
        command=tabel.yview
    )
    tabel.configure(yscrollcommand=scrollbar.set)

    tabel.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    for i, pesanan in enumerate(semua_pesanan[:BATAS_TAMPIL]):
        tabel.insert(
            "",
            "end",
            iid=str(i),
            values=(
                i,
                pesanan[0],
                pesanan[1],
                pesanan[2],
                pesanan[3],
                pesanan[4],
                pesanan[5],
                pesanan[8]
            )
        )


def tampilkan_queue_enqueue():
    bersihkan_konten()

    tk.Label(
        content,
        text="Queue: Pesanan Baru Masuk ke Belakang",
        font=("Segoe UI", 12, "bold"),
        bg=WHITE,
        fg=PINK_DARK
    ).pack(anchor="w", padx=12, pady=(8, 2))

    tk.Label(
        content,
        text=(
            "Menambah pesanan di ujung belakang kedua antrean "
            "sekaligus, yaitu Naive Queue dan Circular Queue."
        ),
        font=("Segoe UI", 8),
        bg=WHITE,
        fg=MUTED,
        wraplength=850,
        justify="left"
    ).pack(anchor="w", padx=12, pady=(0, 10))

    frame_input = tk.Frame(content, bg=WHITE)
    frame_input.pack(fill="x", padx=12, pady=(0, 8))

    frame_tombol = tk.Frame(content, bg=WHITE)
    frame_tombol.pack(anchor="w", padx=12, pady=(0, 8))

    tk.Label(
        frame_input,
        text="Nama pelanggan",
        font=("Segoe UI", 9, "bold"),
        bg=WHITE,
        fg=TEXT
    ).pack(side="left", padx=(0, 8))

    input_pelanggan = tk.Entry(
        frame_input,
        font=("Segoe UI", 9),
        width=25
    )
    input_pelanggan.pack(side="left", padx=(0, 8))

    status = tk.Label(
        content,
        text="",
        font=("Segoe UI", 9),
        bg=WHITE,
        fg=TEXT,
        anchor="w",
        justify="left"
    )
    status.pack(fill="x", padx=12, pady=(0, 8))

    frame_tabel = tk.Frame(content, bg=WHITE)
    frame_tabel.pack(
        fill="both",
        expand=True,
        padx=12,
        pady=(0, 8)
    )

    kolom = (
        "oid", "pelanggan", "resto", "menu", "harga",
        "prioritas", "masuk", "selesai", "status"
    )

    tabel = ttk.Treeview(
        frame_tabel,
        columns=kolom,
        show="headings",
        height=10
    )

    judul_kolom = {
        "oid": "oid",
        "pelanggan": "pelanggan",
        "resto": "resto",
        "menu": "menu",
        "harga": "harga",
        "prioritas": "prioritas",
        "masuk": "masuk",
        "selesai": "selesai",
        "status": "status"
    }

    lebar_kolom = {
        "oid": 100,
        "pelanggan": 130,
        "resto": 120,
        "menu": 120,
        "harga": 85,
        "prioritas": 75,
        "masuk": 100,
        "selesai": 100,
        "status": 90
    }

    for nama in kolom:
        tabel.heading(nama, text=judul_kolom[nama])
        tabel.column(
            nama,
            width=lebar_kolom[nama],
            anchor="center"
        )

    scrollbar_y = ttk.Scrollbar(
        frame_tabel,
        orient="vertical",
        command=tabel.yview
    )
    scrollbar_x = ttk.Scrollbar(
        frame_tabel,
        orient="horizontal",
        command=tabel.xview
    )

    tabel.configure(
        yscrollcommand=scrollbar_y.set,
        xscrollcommand=scrollbar_x.set
    )

    tabel.grid(row=0, column=0, sticky="nsew")
    scrollbar_y.grid(row=0, column=1, sticky="ns")
    scrollbar_x.grid(row=1, column=0, sticky="ew")

    frame_tabel.grid_rowconfigure(0, weight=1)
    frame_tabel.grid_columnconfigure(0, weight=1)


    def isi_tabel():
        for item in tabel.get_children():
            tabel.delete(item)

        for pesanan in antrean_naif.data:
            tabel.insert(
                "",
                "end",
                values=(
                    pesanan[0],
                    pesanan[1],
                    pesanan[2],
                    pesanan[3],
                    pesanan[4],
                    pesanan[5],
                    format_waktu_detik(pesanan[6]),
                    format_waktu_detik(pesanan[7])
                    if pesanan[7] not in ("", None, 0, "0")
                    else "-",
                    pesanan[8]
                )
            )

        status.config(
            text=(
                f"Panjang sekarang: Naive {antrean_naif.size()}, "
                f"Circular {antrean_circular.size()} "
                f"| Kapasitas Circular: {antrean_circular.kapasitas}"
            )
        )

    def proses_enqueue():
        nama = input_pelanggan.get().strip()

        if not nama:
            messagebox.showwarning(
                "Input Kosong",
                "Masukkan nama pelanggan terlebih dahulu."
            )
            return

        if not data_pesanan:
            messagebox.showwarning(
                "Data Kosong",
                "Data pesanan belum tersedia."
            )
            return

        if antrean_circular.size() >= antrean_circular.kapasitas:
            messagebox.showwarning(
                "Antrean Penuh",
                "Antrean Circular penuh. Pesanan tidak ditambahkan."
            )
            return

        kandidat = [
            p for p in data_pesanan
            if len(p) >= 9
            and all(str(p[i]).strip() for i in (2, 3, 4, 5))
        ]

        if not kandidat:
            messagebox.showwarning(
                "Data Tidak Valid",
                "Tidak ada data contoh pesanan yang lengkap."
            )
            return

        template = random.choice(kandidat)

        semua_pesanan = list(data_pesanan) + list(antrean_naif.data)

        for i in range(antrean_circular.count):
            posisi = (
                antrean_circular.front + i
            ) % antrean_circular.kapasitas

            pesanan = antrean_circular.data[posisi]

            if pesanan is not None:
                semua_pesanan.append(pesanan)

        nomor_terbesar = 200000

        for pesanan in semua_pesanan:
            try:
                nomor = int(str(pesanan[0]).split("-")[-1])
                nomor_terbesar = max(nomor_terbesar, nomor)
            except (ValueError, IndexError, TypeError):
                continue

        oid_baru = f"O-{nomor_terbesar + 1:06d}"

        sekarang = datetime.now()
        waktu_masuk = (
            sekarang.hour * 3600
            + sekarang.minute * 60
            + sekarang.second
        )

        pesanan_baru = [
            oid_baru,
            nama,
            template[2],
            template[3],
            template[4],
            template[5],
            waktu_masuk,
            "",
            "ANTRE"
        ]

        mulai = time.perf_counter()

        berhasil = antrean_circular.enqueue(pesanan_baru)

        if not berhasil:
            messagebox.showwarning(
                "Antrean Penuh",
                "Pesanan gagal ditambahkan."
            )
            return

        antrean_naif.enqueue(pesanan_baru)

        selesai = time.perf_counter()
        durasi_ms = (selesai - mulai) * 1000

        jumlah = f"{antrean_naif.size():,}".replace(",", ".")

        isi_tabel()
        input_pelanggan.delete(0, tk.END)

        hasil = (
            f"queue_enqueue {nama}\n"
            f"{jumlah} pesanan berada di kedua antrean\n"
            f"{oid_baru} masuk paling belakang "
            f"[M2-queue] {durasi_ms:.2f}ms"
        )

        status.config(
            text=hasil
            + f"\nPanjang: Naive {antrean_naif.size()}, "
            + f"Circular {antrean_circular.size()}"
        )

    tk.Button(
        frame_tombol,
        text="Enqueue",
        font=("Segoe UI", 9, "bold"),
        bg=PINK,
        fg=WHITE,
        activebackground=PINK_HOVER,
        activeforeground=WHITE,
        relief="flat",
        cursor="hand2",
        command=proses_enqueue
    ).pack(side="left")

    isi_tabel()


    def proses_enqueue():
        nama = input_pelanggan.get().strip()

        if not nama:
            messagebox.showwarning(
                "Input Kosong",
                "Masukkan nama pelanggan terlebih dahulu."
            )
            return

        if not data_pesanan:
            messagebox.showwarning(
                "Data Kosong",
                "Data pesanan belum tersedia. Muat data CSV terlebih dahulu."
            )
            return

        kandidat = [
            p for p in data_pesanan
            if len(p) >= 9
            and p[2] != ""
            and p[3] != ""
            and p[4] != ""
            and p[5] != ""
        ]

        if not kandidat:
            messagebox.showwarning(
                "Data Tidak Valid",
                "Tidak ditemukan data yang bisa dijadikan contoh pesanan."
            )
            return

        template = random.choice(kandidat)

        semua_pesanan = list(data_pesanan)

        semua_pesanan.extend(antrean_naif.data)

        for i in range(antrean_circular.count):
            posisi = (antrean_circular.front + i) % antrean_circular.kapasitas
            pesanan = antrean_circular.data[posisi]

            if pesanan is not None:
                semua_pesanan.append(pesanan)

        nomor_terbesar = 200000

        for pesanan in semua_pesanan:
            if not pesanan or len(pesanan) < 1:
                continue

            oid = str(pesanan[0])

            try:
                nomor = int(oid.split("-")[-1])
                nomor_terbesar = max(nomor_terbesar, nomor)
            except (ValueError, IndexError):
                continue

        oid_baru = f"O-{nomor_terbesar + 1:06d}"

        sekarang = datetime.now()
        waktu_masuk = (
            sekarang.hour * 3600
            + sekarang.minute * 60
            + sekarang.second
        )

        pesanan_baru = [
            oid_baru,       # ID pesanan
            nama,           # Nama pelanggan baru
            template[2],    # Restoran
            template[3],    # Menu
            template[4],    # Harga
            template[5],    # Prioritas
            waktu_masuk,    # Waktu masuk
            "",             # Waktu selesai (belum selesai)
            "ANTRE"         # Status
        ]

        ukuran_sebelum = antrean_naif.size()
        mulai = time.perf_counter()

        berhasil = antrean_circular.enqueue(pesanan_baru)

        if not berhasil:
            messagebox.showwarning(
                "Antrean Penuh",
                "Antrean Circular penuh. Pesanan tidak ditambahkan."
            )
            return

        antrean_naif.enqueue(pesanan_baru)

        selesai = time.perf_counter()
        durasi_ms = (selesai - mulai) * 1000

        ukuran_sesudah = antrean_naif.size()
        jumlah = f"{ukuran_sesudah:,}".replace(",", ".")

        isi_tabel()
        input_pelanggan.delete(0, tk.END)


def format_waktu_detik(nilai):
    try:
        detik = int(float(nilai))
        jam = (detik // 3600) % 24
        menit = (detik % 3600) // 60
        detik_sisa = detik % 60

        return f"{jam:02d}:{menit:02d}:{detik_sisa:02d}"
    except (ValueError, TypeError):
        return str(nilai)

def tampilkan_dequeue_naif():
    bersihkan_konten()

    tk.Label(
        content,
        text="Queue Naif: Ambil dari Depan dengan Menggeser Isi",
        font=("Segoe UI", 12, "bold"),
        bg=WHITE,
        fg=PINK_DARK
    ).pack(anchor="w", padx=12, pady=(8, 2))

    tk.Label(
        content,
        text=(
            "Mengambil indeks 0 lalu menggeser seluruh sisa isi "
            "satu petak ke kiri. Biayanya O(n) setiap kali."
        ),
        font=("Segoe UI", 9),
        bg=WHITE,
        fg=MUTED,
        wraplength=900,
        justify="left"
    ).pack(anchor="w", padx=12, pady=(0, 12))

    frame_input = tk.Frame(content, bg=WHITE)
    frame_input.pack(fill="x", padx=12, pady=(0, 8))

    tk.Label(
        frame_input,
        text="Berapa kali dequeue",
        font=("Segoe UI", 9, "bold"),
        bg=WHITE,
        fg=TEXT
    ).pack(anchor="w")

    frame_kontrol = tk.Frame(frame_input, bg=WHITE)
    frame_kontrol.pack(anchor="w", pady=(4, 2))

    input_jumlah = tk.Entry(
        frame_kontrol,
        font=("Segoe UI", 10),
        width=12
    )
    input_jumlah.insert(0, "2")
    input_jumlah.pack(side="left", padx=(0, 8))

    tk.Button(
        frame_kontrol,
        text="DEQUEUE",
        font=("Segoe UI", 9, "bold"),
        bg=PINK,
        fg=WHITE,
        activebackground=PINK_HOVER,
        activeforeground=WHITE,
        relief="flat",
        cursor="hand2",
        command=lambda: proses_dequeue()
    ).pack(side="left")

    tk.Label(
        frame_input,
        text="Sampai panjang antrean; coba 1 lalu 100 untuk melihat bedanya.",
        font=("Segoe UI", 8),
        bg=WHITE,
        fg=MUTED
    ).pack(anchor="w", pady=(3, 0))

    ringkasan = tk.Label(
        content,
        text="",
        font=("Segoe UI", 9),
        bg=WHITE,
        fg=TEXT,
        justify="left",
        anchor="w",
        wraplength=950
    )
    ringkasan.pack(fill="x", padx=12, pady=(6, 10))

    frame_tabel = tk.Frame(content, bg=WHITE)
    frame_tabel.pack(
        fill="both",
        expand=True,
        padx=12,
        pady=(0, 8)
    )

    kolom = ("oid", "pelanggan", "resto", "menu", "masuk")
    tabel = ttk.Treeview(
        frame_tabel,
        columns=kolom,
        show="headings",
        height=9
    )

    lebar = {
        "oid": 120,
        "pelanggan": 190,
        "resto": 160,
        "menu": 160,
        "masuk": 120
    }

    for nama in kolom:
        tabel.heading(nama, text=nama)
        tabel.column(nama, width=lebar[nama], anchor="w")

    scroll_y = ttk.Scrollbar(
        frame_tabel,
        orient="vertical",
        command=tabel.yview
    )
    scroll_x = ttk.Scrollbar(
        frame_tabel,
        orient="horizontal",
        command=tabel.xview
    )

    tabel.configure(
        yscrollcommand=scroll_y.set,
        xscrollcommand=scroll_x.set
    )

    tabel.grid(row=0, column=0, sticky="nsew")
    scroll_y.grid(row=0, column=1, sticky="ns")
    scroll_x.grid(row=1, column=0, sticky="ew")

    frame_tabel.grid_rowconfigure(0, weight=1)
    frame_tabel.grid_columnconfigure(0, weight=1)

    def tampilkan_tabel():
        for item in tabel.get_children():
            tabel.delete(item)

        for pesanan in antrean_naif.data[:50]:
            tabel.insert(
                "",
                "end",
                values=(
                    pesanan[0],
                    pesanan[1],
                    pesanan[2],
                    pesanan[3],
                    format_waktu_detik(pesanan[6]),
                )
            )

    def proses_dequeue():
        try:
            jumlah = int(input_jumlah.get())
            if jumlah <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning(
                "Input Tidak Valid",
                "Masukkan jumlah dequeue berupa bilangan bulat positif."
            )
            return

        panjang_awal = antrean_naif.size()

        if panjang_awal == 0:
            messagebox.showinfo(
                "Antrean Kosong",
                "Tidak ada pesanan di Naive Queue."
            )
            return

        jumlah_aktual = min(jumlah, panjang_awal)
        geseran_sebelum = antrean_naif.total_shifts
        pesanan_keluar = []

        waktu_mulai = time.perf_counter()

        for _ in range(jumlah_aktual):
            pesanan = antrean_naif.dequeue()
            if pesanan is not None:
                pesanan_keluar.append(pesanan)

        waktu_selesai = time.perf_counter()

        waktu_ms = (waktu_selesai - waktu_mulai) * 1000
        total_geseran = (
            antrean_naif.total_shifts - geseran_sebelum
        )
        rata_rata = total_geseran / len(pesanan_keluar) if pesanan_keluar else 0
        sisa = antrean_naif.size()

        tampilkan_tabel()

        ringkasan.config(
            text=(
                f"{len(pesanan_keluar)} pesanan keluar dari depan antrean naif.\n"
                f"Total {total_geseran:,} elemen digeser, rata-rata "
                f"{rata_rata:,.0f} geseran per dequeue.\n"
                f"Sisa antrean naif {sisa:,}.\n"
                f"Waktu eksekusi: {waktu_ms:.4f} ms."
            )
        )

    tampilkan_tabel()
    ringkasan.config(
        text=(
            f"Panjang antrean naif saat ini: {antrean_naif.size():,}.\n"
            "Tabel menampilkan maksimal 50 pesanan terdepan."
        )
    )


def tampilkan_dequeue_circular():
    bersihkan_konten()

    tk.Label(
        content,
        text="Queue: Dequeue Circular",
        font=("Segoe UI", 12, "bold"),
        bg=WHITE,
        fg=PINK_DARK
    ).pack(anchor="w", padx=12, pady=(8, 2))

    tk.Label(
        content,
        text=(
            "Menghapus pesanan dari bagian depan Circular Queue. "
            "Indeks front bergerak melingkar tanpa menggeser seluruh elemen."
        ),
        font=("Segoe UI", 8),
        bg=WHITE,
        fg=MUTED,
        wraplength=850,
        justify="left"
    ).pack(anchor="w", padx=12, pady=(0, 10))

    frame_input = tk.Frame(content, bg=WHITE)
    frame_input.pack(fill="x", padx=12, pady=(0, 8))

    tk.Label(
        frame_input,
        text="Jumlah dequeue",
        font=("Segoe UI", 9, "bold"),
        bg=WHITE,
        fg=TEXT
    ).pack(side="left", padx=(0, 8))

    input_jumlah = tk.Entry(
        frame_input,
        font=("Segoe UI", 9),
        width=10
    )
    input_jumlah.insert(0, "2")
    input_jumlah.pack(side="left", padx=(0, 8))

    status = tk.Label(
        content,
        text="",
        font=("Segoe UI", 9),
        bg=WHITE,
        fg=TEXT,
        anchor="w",
        justify="left"
    )
    status.pack(fill="x", padx=12, pady=(0, 8))

    frame_tabel = tk.Frame(content, bg=WHITE)
    frame_tabel.pack(
        fill="both",
        expand=True,
        padx=12,
        pady=(0, 8)
    )

    kolom = (
        "oid", "pelanggan", "resto", "menu",
        "harga", "prioritas", "masuk", "status"
    )

    tabel = ttk.Treeview(
        frame_tabel,
        columns=kolom,
        show="headings",
        height=10
    )

    judul_kolom = {
        "oid": "OID",
        "pelanggan": "Pelanggan",
        "resto": "Restoran",
        "menu": "Menu",
        "harga": "Harga",
        "prioritas": "Prioritas",
        "masuk": "Waktu Masuk",
        "status": "Status"
    }

    lebar_kolom = {
        "oid": 100,
        "pelanggan": 130,
        "resto": 120,
        "menu": 120,
        "harga": 85,
        "prioritas": 75,
        "masuk": 100,
        "status": 90
    }

    for nama_kolom in kolom:
        tabel.heading(
            nama_kolom,
            text=judul_kolom[nama_kolom]
        )
        tabel.column(
            nama_kolom,
            width=lebar_kolom[nama_kolom],
            anchor="center"
        )

    scrollbar_y = ttk.Scrollbar(
        frame_tabel,
        orient="vertical",
        command=tabel.yview
    )
    scrollbar_x = ttk.Scrollbar(
        frame_tabel,
        orient="horizontal",
        command=tabel.xview
    )

    tabel.configure(
        yscrollcommand=scrollbar_y.set,
        xscrollcommand=scrollbar_x.set
    )

    tabel.grid(row=0, column=0, sticky="nsew")
    scrollbar_y.grid(row=0, column=1, sticky="ns")
    scrollbar_x.grid(row=1, column=0, sticky="ew")

    frame_tabel.grid_rowconfigure(0, weight=1)
    frame_tabel.grid_columnconfigure(0, weight=1)

    def isi_tabel():
        for item in tabel.get_children():
            tabel.delete(item)

        jumlah_data = antrean_circular.size()
        batas_tampil = min(jumlah_data, 50)

        for i in range(batas_tampil):
            posisi = (
                antrean_circular.front + i
            ) % antrean_circular.kapasitas

            pesanan = antrean_circular.data[posisi]

            if pesanan is None:
                continue

            tabel.insert(
                "",
                "end",
                values=(
                    pesanan[0],
                    pesanan[1],
                    pesanan[2],
                    pesanan[3],
                    pesanan[4],
                    pesanan[5],
                    format_waktu_detik(pesanan[6]),
                    pesanan[8]
                )
            )

        status.config(
            text=(
                f"Panjang Circular Queue: {antrean_circular.size()} "
                f"| Front: {antrean_circular.front} "
                f"| Rear: {antrean_circular.rear} "
                f"| Kapasitas: {antrean_circular.kapasitas}"
            )
        )

    def proses_dequeue():
        teks_jumlah = input_jumlah.get().strip()

        try:
            jumlah = int(teks_jumlah)

            if jumlah <= 0:
                raise ValueError

        except ValueError:
            messagebox.showwarning(
                "Input Tidak Valid",
                "Masukkan bilangan bulat lebih dari 0."
            )
            return

        if antrean_circular.is_empty():
            messagebox.showinfo(
                "Antrean Kosong",
                "Tidak ada pesanan yang dapat dihapus."
            )
            return

        ukuran_awal = antrean_circular.size()
        jumlah_proses = min(jumlah, ukuran_awal)
        pesanan_dihapus = []

        mulai = time.perf_counter()

        for _ in range(jumlah_proses):
            pesanan = antrean_circular.dequeue()

            if pesanan is not None:
                pesanan_dihapus.append(pesanan)

        selesai = time.perf_counter()
        durasi_ms = (selesai - mulai) * 1000

        isi_tabel()

        daftar_oid = ", ".join(
            str(pesanan[0]) for pesanan in pesanan_dihapus
        )

        status.config(
            text=(
                f"Berhasil menghapus {len(pesanan_dihapus)} pesanan "
                f"dari Circular Queue.\n"
                f"OID dihapus: {daftar_oid}\n"
                f"Sisa antrean: {antrean_circular.size()} "
                f"| Waktu proses: {durasi_ms:.4f} ms"
            )
        )

        if jumlah > ukuran_awal:
            messagebox.showinfo(
                "Dequeue Selesai",
                (
                    f"Antrean awal berisi {ukuran_awal} pesanan. "
                    f"Hanya {len(pesanan_dihapus)} pesanan yang dihapus "
                    "karena antrean tidak memiliki cukup data."
                )
            )

    tk.Button(
        frame_input,
        text="Dequeue",
        font=("Segoe UI", 9, "bold"),
        bg=PINK,
        fg=WHITE,
        activebackground=PINK_HOVER,
        activeforeground=WHITE,
        relief="flat",
        cursor="hand2",
        command=proses_dequeue
    ).pack(side="left")

    isi_tabel()


def tampilkan_insertion_sort():
    bersihkan_konten()

    tk.Label(
        content,
        text="Sort: Insertion Sort, O(n²)",
        font=("Segoe UI", 12, "bold"),
        bg=WHITE,
        fg=PINK_DARK
    ).pack(anchor="w", padx=12, pady=(8, 2))

    tk.Label(
        content,
        text=(
            "Setiap elemen digeser mundur sampai menemukan tempatnya. "
            "Sederhana, tetapi biaya pemrosesannya tumbuh kuadratik."
        ),
        font=("Segoe UI", 8),
        bg=WHITE,
        fg=MUTED,
        wraplength=850,
        justify="left"
    ).pack(anchor="w", padx=12, pady=(0, 12))

    frame_input = tk.Frame(content, bg=WHITE)
    frame_input.pack(fill="x", padx=12, pady=(0, 10))

    tk.Label(
        frame_input,
        text="Jumlah baris diurutkan",
        font=("Segoe UI", 9, "bold"),
        bg=WHITE,
        fg=TEXT
    ).grid(row=0, column=0, sticky="w", padx=(0, 8), pady=4)

    input_jumlah = tk.Entry(
        frame_input,
        font=("Segoe UI", 9),
        width=12
    )
    input_jumlah.insert(0, "10")
    input_jumlah.grid(row=0, column=1, sticky="w", padx=(0, 20), pady=4)

    tk.Label(
        frame_input,
        text="Diurutkan menurut",
        font=("Segoe UI", 9, "bold"),
        bg=WHITE,
        fg=TEXT
    ).grid(row=0, column=2, sticky="w", padx=(0, 8), pady=4)

    pilihan_kunci = ttk.Combobox(
        frame_input,
        state="readonly",
        width=15,
        values=["harga", "oid", "selesai"]
    )
    pilihan_kunci.set("harga")
    pilihan_kunci.grid(row=0, column=3, sticky="w", pady=4)

    status = tk.Label(
        content,
        text="Pilih jumlah baris dan kunci, lalu klik URUTKAN.",
        font=("Segoe UI", 9),
        bg=WHITE,
        fg=TEXT,
        anchor="w",
        justify="left"
    )
    status.pack(fill="x", padx=12, pady=(0, 10))

    frame_tabel = tk.Frame(content, bg=WHITE)
    frame_tabel.pack(
        fill="both",
        expand=True,
        padx=12,
        pady=(0, 8)
    )

    kolom = ("oid", "harga", "selesai", "resto", "menu")

    tabel = ttk.Treeview(
        frame_tabel,
        columns=kolom,
        show="headings",
        height=12
    )

    judul = {
        "oid": "OID",
        "harga": "Harga",
        "selesai": "Waktu Selesai",
        "resto": "Restoran",
        "menu": "Menu"
    }

    lebar = {
        "oid": 120,
        "harga": 100,
        "selesai": 130,
        "resto": 160,
        "menu": 160
    }

    for nama_kolom in kolom:
        tabel.heading(nama_kolom, text=judul[nama_kolom])
        tabel.column(
            nama_kolom,
            width=lebar[nama_kolom],
            anchor="center"
        )

    scrollbar_y = ttk.Scrollbar(
        frame_tabel,
        orient="vertical",
        command=tabel.yview
    )
    scrollbar_x = ttk.Scrollbar(
        frame_tabel,
        orient="horizontal",
        command=tabel.xview
    )

    tabel.configure(
        yscrollcommand=scrollbar_y.set,
        xscrollcommand=scrollbar_x.set
    )

    tabel.grid(row=0, column=0, sticky="nsew")
    scrollbar_y.grid(row=0, column=1, sticky="ns")
    scrollbar_x.grid(row=1, column=0, sticky="ew")

    frame_tabel.grid_rowconfigure(0, weight=1)
    frame_tabel.grid_columnconfigure(0, weight=1)

    def proses_sort():
        teks_jumlah = input_jumlah.get().strip()

        try:
            jumlah = int(teks_jumlah)

            if jumlah <= 0:
                raise ValueError

        except ValueError:
            messagebox.showwarning(
                "Input Tidak Valid",
                "Jumlah baris harus berupa bilangan bulat lebih dari 0."
            )
            return

        if not data_pesanan:
            messagebox.showwarning(
                "Data Kosong",
                "Data pesanan belum tersedia."
            )
            return

        jumlah_aktual = min(jumlah, len(data_pesanan))

        data_sort = [
            list(pesanan)
            for pesanan in data_pesanan[:jumlah_aktual]
        ]

        kunci = pilihan_kunci.get()

        mulai = time.perf_counter()

        try:
            perbandingan, pemindahan = insertion_sort(
                data_sort,
                kunci
            )
        except (ValueError, TypeError, IndexError) as error:
            messagebox.showerror(
                "Sorting Gagal",
                f"Terjadi kesalahan saat mengurutkan data:\n{error}"
            )
            return

        selesai = time.perf_counter()
        waktu_ms = (selesai - mulai) * 1000

        for item in tabel.get_children():
            tabel.delete(item)

        for pesanan in data_sort:
            tabel.insert(
                "",
                "end",
                values=(
                    pesanan[0],
                    f"{int(float(pesanan[4])):,}".replace(",", "."),
                    format_waktu_detik(pesanan[7])
                    if pesanan[7] not in ("", None, 0, "0")
                    else "-",
                    pesanan[2],
                    pesanan[3]
                )
            )

        jumlah_teks = f"{jumlah_aktual:,}".replace(",", ".")
        perbandingan_teks = f"{perbandingan:,}".replace(",", ".")
        pemindahan_teks = f"{pemindahan:,}".replace(",", ".")

        status.config(
            text=(
                f"{jumlah_teks} pesanan diurutkan menurut {kunci}.\n"
                f"{perbandingan_teks} perbandingan, "
                f"{pemindahan_teks} pemindahan.\n"
                f"Waktu proses: {waktu_ms:.2f} ms."
            )
        )

    tk.Button(
        frame_input,
        text="URUTKAN",
        font=("Segoe UI", 9, "bold"),
        bg=PINK,
        fg=WHITE,
        activebackground=PINK_HOVER,
        activeforeground=WHITE,
        relief="flat",
        cursor="hand2",
        command=proses_sort
    ).grid(row=0, column=4, padx=(16, 0), pady=4)

    frame_input.grid_columnconfigure(5, weight=1)


def tampilkan_merge_sort():
    bersihkan_konten()

    tk.Label(
        content,
        text="Sort: Merge Sort, O(n log n)",
        font=("Segoe UI", 12, "bold"),
        bg=WHITE,
        fg=PINK_DARK
    ).pack(anchor="w", padx=12, pady=(8, 2))

    tk.Label(
        content,
        text=(
            "Data dibagi menjadi bagian-bagian kecil, lalu setiap bagian "
            "diurutkan dan digabungkan kembali. Lebih efisien untuk "
            "data berukuran besar."
        ),
        font=("Segoe UI", 8),
        bg=WHITE,
        fg=MUTED,
        wraplength=850,
        justify="left"
    ).pack(anchor="w", padx=12, pady=(0, 12))

    frame_input = tk.Frame(content, bg=WHITE)
    frame_input.pack(fill="x", padx=12, pady=(0, 10))

    tk.Label(
        frame_input,
        text="Jumlah baris diurutkan",
        font=("Segoe UI", 9, "bold"),
        bg=WHITE,
        fg=TEXT
    ).grid(row=0, column=0, sticky="w", padx=(0, 8), pady=4)

    input_jumlah = tk.Entry(
        frame_input,
        font=("Segoe UI", 9),
        width=12
    )
    input_jumlah.insert(0, "10")
    input_jumlah.grid(row=0, column=1, sticky="w", padx=(0, 20), pady=4)

    tk.Label(
        frame_input,
        text="Diurutkan menurut",
        font=("Segoe UI", 9, "bold"),
        bg=WHITE,
        fg=TEXT
    ).grid(row=0, column=2, sticky="w", padx=(0, 8), pady=4)

    pilihan_kunci = ttk.Combobox(
        frame_input,
        state="readonly",
        width=15,
        values=["harga", "oid", "selesai"]
    )
    pilihan_kunci.set("harga")
    pilihan_kunci.grid(row=0, column=3, sticky="w", pady=4)

    status = tk.Label(
        content,
        text="Pilih jumlah baris dan kunci, lalu klik URUTKAN.",
        font=("Segoe UI", 9),
        bg=WHITE,
        fg=TEXT,
        anchor="w",
        justify="left"
    )
    status.pack(fill="x", padx=12, pady=(0, 10))

    frame_tabel = tk.Frame(content, bg=WHITE)
    frame_tabel.pack(
        fill="both",
        expand=True,
        padx=12,
        pady=(0, 8)
    )

    kolom = ("oid", "harga", "selesai", "resto", "menu")

    tabel = ttk.Treeview(
        frame_tabel,
        columns=kolom,
        show="headings",
        height=12
    )

    judul = {
        "oid": "OID",
        "harga": "Harga",
        "selesai": "Waktu Selesai",
        "resto": "Restoran",
        "menu": "Menu"
    }

    lebar = {
        "oid": 120,
        "harga": 100,
        "selesai": 130,
        "resto": 160,
        "menu": 160
    }

    for nama_kolom in kolom:
        tabel.heading(nama_kolom, text=judul[nama_kolom])
        tabel.column(
            nama_kolom,
            width=lebar[nama_kolom],
            anchor="center"
        )

    scrollbar_y = ttk.Scrollbar(
        frame_tabel,
        orient="vertical",
        command=tabel.yview
    )
    scrollbar_x = ttk.Scrollbar(
        frame_tabel,
        orient="horizontal",
        command=tabel.xview
    )

    tabel.configure(
        yscrollcommand=scrollbar_y.set,
        xscrollcommand=scrollbar_x.set
    )

    tabel.grid(row=0, column=0, sticky="nsew")
    scrollbar_y.grid(row=0, column=1, sticky="ns")
    scrollbar_x.grid(row=1, column=0, sticky="ew")

    frame_tabel.grid_rowconfigure(0, weight=1)
    frame_tabel.grid_columnconfigure(0, weight=1)

    def proses_sort():
        teks_jumlah = input_jumlah.get().strip()

        try:
            jumlah = int(teks_jumlah)

            if jumlah <= 0:
                raise ValueError

        except ValueError:
            messagebox.showwarning(
                "Input Tidak Valid",
                "Jumlah baris harus berupa bilangan bulat lebih dari 0."
            )
            return

        if not data_pesanan:
            messagebox.showwarning(
                "Data Kosong",
                "Data pesanan belum tersedia."
            )
            return

        jumlah_aktual = min(jumlah, len(data_pesanan))

        data_sort = [
            list(pesanan)
            for pesanan in data_pesanan[:jumlah_aktual]
        ]

        kunci = pilihan_kunci.get()

        mulai = time.perf_counter()

        try:
            perbandingan, pemindahan = merge_sort(
                data_sort,
                kunci
            )
        except (ValueError, TypeError, IndexError) as error:
            messagebox.showerror(
                "Sorting Gagal",
                f"Terjadi kesalahan saat mengurutkan data:\n{error}"
            )
            return

        selesai = time.perf_counter()
        waktu_ms = (selesai - mulai) * 1000

        for item in tabel.get_children():
            tabel.delete(item)

        for pesanan in data_sort:
            try:
                harga = f"{int(float(pesanan[4])):,}".replace(",", ".")
            except (ValueError, TypeError):
                harga = str(pesanan[4])

            tabel.insert(
                "",
                "end",
                values=(
                    pesanan[0],
                    harga,
                    format_waktu_detik(pesanan[7])
                    if pesanan[7] not in ("", None, 0, "0")
                    else "-",
                    pesanan[2],
                    pesanan[3]
                )
            )

        jumlah_teks = f"{jumlah_aktual:,}".replace(",", ".")
        perbandingan_teks = f"{perbandingan:,}".replace(",", ".")
        pemindahan_teks = f"{pemindahan:,}".replace(",", ".")

        status.config(
            text=(
                f"{jumlah_teks} pesanan diurutkan menurut {kunci}.\n"
                f"{perbandingan_teks} perbandingan, "
                f"{pemindahan_teks} pemindahan.\n"
                f"Waktu proses: {waktu_ms:.2f} ms."
            )
        )

    tk.Button(
        frame_input,
        text="URUTKAN",
        font=("Segoe UI", 9, "bold"),
        bg=PINK,
        fg=WHITE,
        activebackground=PINK_HOVER,
        activeforeground=WHITE,
        relief="flat",
        cursor="hand2",
        command=proses_sort
    ).grid(row=0, column=4, padx=(16, 0), pady=4)

    frame_input.grid_columnconfigure(5, weight=1)


def tampilkan_linear_search():
    bersihkan_konten()

    tk.Label(
        content,
        text="Search: Linear Search, O(n)",
        font=("Segoe UI", 12, "bold"),
        bg=WHITE,
        fg=PINK_DARK
    ).pack(anchor="w", padx=12, pady=(8, 2))

    tk.Label(
        content,
        text=(
            "Memeriksa pesanan satu per satu dari depan. "
            "Tidak menuntut data terurut."
        ),
        font=("Segoe UI", 8),
        bg=WHITE,
        fg=MUTED,
        wraplength=850,
        justify="left"
    ).pack(anchor="w", padx=12, pady=(0, 12))

    frame_input = tk.Frame(content, bg=WHITE)
    frame_input.pack(fill="x", padx=12, pady=(0, 10))

    tk.Label(
        frame_input,
        text="Nomor pesanan (OID)",
        font=("Segoe UI", 9, "bold"),
        bg=WHITE,
        fg=TEXT
    ).grid(row=0, column=0, sticky="w", padx=(0, 8), pady=4)

    input_oid = tk.Entry(
        frame_input,
        font=("Segoe UI", 9),
        width=22
    )
    input_oid.grid(row=0, column=1, sticky="w", padx=(0, 16), pady=4)

    status = tk.Label(
        content,
        text="Masukkan OID yang ingin dicari, lalu klik CARI.",
        font=("Segoe UI", 9),
        bg=WHITE,
        fg=TEXT,
        anchor="w",
        justify="left"
    )
    status.pack(fill="x", padx=12, pady=(0, 10))

    frame_tabel = tk.Frame(content, bg=WHITE)
    frame_tabel.pack(
        fill="both",
        expand=True,
        padx=12,
        pady=(0, 8)
    )

    kolom = (
        "oid",
        "pelanggan",
        "resto",
        "menu",
        "harga",
        "prioritas",
        "masuk",
        "selesai",
        "status"
    )

    tabel = ttk.Treeview(
        frame_tabel,
        columns=kolom,
        show="headings",
        height=12
    )

    judul = {
        "oid": "OID",
        "pelanggan": "Pelanggan",
        "resto": "Resto",
        "menu": "Menu",
        "harga": "Harga",
        "prioritas": "Prioritas",
        "masuk": "Masuk",
        "selesai": "Selesai",
        "status": "Status"
    }

    lebar = {
        "oid": 115,
        "pelanggan": 165,
        "resto": 140,
        "menu": 130,
        "harga": 95,
        "prioritas": 85,
        "masuk": 100,
        "selesai": 100,
        "status": 100
    }

    for nama_kolom in kolom:
        tabel.heading(nama_kolom, text=judul[nama_kolom])
        tabel.column(
            nama_kolom,
            width=lebar[nama_kolom],
            anchor="center"
        )

    scrollbar_y = ttk.Scrollbar(
        frame_tabel,
        orient="vertical",
        command=tabel.yview
    )

    scrollbar_x = ttk.Scrollbar(
        frame_tabel,
        orient="horizontal",
        command=tabel.xview
    )

    tabel.configure(
        yscrollcommand=scrollbar_y.set,
        xscrollcommand=scrollbar_x.set
    )

    tabel.grid(row=0, column=0, sticky="nsew")
    scrollbar_y.grid(row=0, column=1, sticky="ns")
    scrollbar_x.grid(row=1, column=0, sticky="ew")

    frame_tabel.grid_rowconfigure(0, weight=1)
    frame_tabel.grid_columnconfigure(0, weight=1)

    def proses_search():
        target = input_oid.get().strip()

        if not target:
            messagebox.showwarning(
                "Input Tidak Valid",
                "Masukkan nomor pesanan (OID) yang ingin dicari."
            )
            return

        if not data_pesanan:
            messagebox.showwarning(
                "Data Kosong",
                "Data pesanan belum tersedia."
            )
            return

        for item in tabel.get_children():
            tabel.delete(item)

        mulai = time.perf_counter()

        try:
            posisi, perbandingan = linear_search(
                data_pesanan,
                target
            )
        except (ValueError, TypeError, IndexError) as error:
            messagebox.showerror(
                "Pencarian Gagal",
                f"Terjadi kesalahan saat mencari data:\n{error}"
            )
            return

        selesai = time.perf_counter()
        waktu_ms = (selesai - mulai) * 1000

        jumlah_teks = f"{perbandingan:,}".replace(",", ".")

        if posisi == -1:
            status.config(
                text=(
                    f"Pesanan dengan OID {target} tidak ditemukan.\n"
                    f"{jumlah_teks} perbandingan."
                )
            )
            return

        pesanan = data_pesanan[posisi]

        try:
            harga = f"{int(float(pesanan[4])):,}".replace(",", ".")
        except (ValueError, TypeError):
            harga = str(pesanan[4])

        waktu_masuk = (
            format_waktu_detik(pesanan[6])
            if pesanan[6] not in ("", None)
            else "-"
        )

        waktu_selesai = (
            format_waktu_detik(pesanan[7])
            if pesanan[7] not in ("", None, 0, "0")
            else "-"
        )

        tabel.insert(
            "",
            "end",
            values=(
                pesanan[0],
                pesanan[1],
                pesanan[2],
                pesanan[3],
                harga,
                pesanan[5],
                waktu_masuk,
                waktu_selesai,
                pesanan[8]
            )
        )

        posisi_teks = f"{posisi:,}".replace(",", ".")
        waktu_teks = f"{waktu_ms:.2f}"

        status.config(
            text=(
                f"Ditemukan pada indeks {posisi_teks}.\n"
                f"{jumlah_teks} perbandingan.\n"
                f"Waktu proses: {waktu_teks} ms."
            )
        )

    tk.Button(
        frame_input,
        text="CARI",
        font=("Segoe UI", 9, "bold"),
        bg=PINK,
        fg=WHITE,
        activebackground=PINK_HOVER,
        activeforeground=WHITE,
        relief="flat",
        cursor="hand2",
        command=proses_search
    ).grid(row=0, column=2, padx=(0, 0), pady=4)

    frame_input.grid_columnconfigure(3, weight=1)


def tampilkan_binary_search():
    bersihkan_konten()

    tk.Label(
        content,
        text="Search: Binary Search, O(log n)",
        font=("Segoe UI", 12, "bold"),
        bg=WHITE,
        fg=PINK_DARK
    ).pack(anchor="w", padx=12, pady=(8, 2))

    tk.Label(
        content,
        text=(
            "Mencari pesanan dengan membagi rentang pencarian menjadi "
            "dua secara berulang. Data harus terurut berdasarkan OID."
        ),
        font=("Segoe UI", 8),
        bg=WHITE,
        fg=MUTED,
        wraplength=850,
        justify="left"
    ).pack(anchor="w", padx=12, pady=(0, 12))

    frame_input = tk.Frame(content, bg=WHITE)
    frame_input.pack(fill="x", padx=12, pady=(0, 10))

    tk.Label(
        frame_input,
        text="Nomor pesanan (OID)",
        font=("Segoe UI", 9, "bold"),
        bg=WHITE,
        fg=TEXT
    ).grid(row=0, column=0, sticky="w", padx=(0, 8), pady=4)

    input_oid = tk.Entry(
        frame_input,
        font=("Segoe UI", 9),
        width=22
    )
    input_oid.grid(row=0, column=1, sticky="w", padx=(0, 16), pady=4)

    status = tk.Label(
        content,
        text="Masukkan OID yang ingin dicari, lalu klik CARI.",
        font=("Segoe UI", 9),
        bg=WHITE,
        fg=TEXT,
        anchor="w",
        justify="left"
    )
    status.pack(fill="x", padx=12, pady=(0, 10))

    frame_tabel = tk.Frame(content, bg=WHITE)
    frame_tabel.pack(
        fill="both",
        expand=True,
        padx=12,
        pady=(0, 8)
    )

    kolom = (
        "oid",
        "pelanggan",
        "resto",
        "menu",
        "harga",
        "prioritas",
        "masuk",
        "selesai",
        "status"
    )

    tabel = ttk.Treeview(
        frame_tabel,
        columns=kolom,
        show="headings",
        height=12
    )

    judul = {
        "oid": "OID",
        "pelanggan": "Pelanggan",
        "resto": "Resto",
        "menu": "Menu",
        "harga": "Harga",
        "prioritas": "Prioritas",
        "masuk": "Masuk",
        "selesai": "Selesai",
        "status": "Status"
    }

    lebar = {
        "oid": 115,
        "pelanggan": 165,
        "resto": 140,
        "menu": 130,
        "harga": 95,
        "prioritas": 85,
        "masuk": 100,
        "selesai": 100,
        "status": 100
    }

    for nama_kolom in kolom:
        tabel.heading(nama_kolom, text=judul[nama_kolom])
        tabel.column(
            nama_kolom,
            width=lebar[nama_kolom],
            anchor="center"
        )

    scrollbar_y = ttk.Scrollbar(
        frame_tabel,
        orient="vertical",
        command=tabel.yview
    )

    scrollbar_x = ttk.Scrollbar(
        frame_tabel,
        orient="horizontal",
        command=tabel.xview
    )

    tabel.configure(
        yscrollcommand=scrollbar_y.set,
        xscrollcommand=scrollbar_x.set
    )

    tabel.grid(row=0, column=0, sticky="nsew")
    scrollbar_y.grid(row=0, column=1, sticky="ns")
    scrollbar_x.grid(row=1, column=0, sticky="ew")

    frame_tabel.grid_rowconfigure(0, weight=1)
    frame_tabel.grid_columnconfigure(0, weight=1)

    def proses_search():
        target = input_oid.get().strip()

        if not target:
            messagebox.showwarning(
                "Input Tidak Valid",
                "Masukkan nomor pesanan (OID) yang ingin dicari."
            )
            return

        if not data_pesanan:
            messagebox.showwarning(
                "Data Kosong",
                "Data pesanan belum tersedia."
            )
            return

        for item in tabel.get_children():
            tabel.delete(item)

        data_urut = [list(pesanan) for pesanan in data_pesanan]
        data_urut.sort(key=lambda pesanan: pesanan[0])

        mulai = time.perf_counter()

        try:
            posisi, perbandingan = binary_search(
                data_urut,
                target
            )
        except (ValueError, TypeError, IndexError) as error:
            messagebox.showerror(
                "Pencarian Gagal",
                f"Terjadi kesalahan saat mencari data:\n{error}"
            )
            return

        selesai = time.perf_counter()
        waktu_ms = (selesai - mulai) * 1000

        jumlah_teks = f"{perbandingan:,}".replace(",", ".")

        if posisi == -1:
            status.config(
                text=(
                    f"Pesanan dengan OID {target} tidak ditemukan.\n"
                    f"{jumlah_teks} perbandingan."
                )
            )
            return

        pesanan = data_urut[posisi]

        try:
            harga = f"{int(float(pesanan[4])):,}".replace(",", ".")
        except (ValueError, TypeError):
            harga = str(pesanan[4])

        waktu_masuk = (
            format_waktu_detik(pesanan[6])
            if pesanan[6] not in ("", None)
            else "-"
        )

        waktu_selesai = (
            format_waktu_detik(pesanan[7])
            if pesanan[7] not in ("", None, 0, "0")
            else "-"
        )

        tabel.insert(
            "",
            "end",
            values=(
                pesanan[0],
                pesanan[1],
                pesanan[2],
                pesanan[3],
                harga,
                pesanan[5],
                waktu_masuk,
                waktu_selesai,
                pesanan[8]
            )
        )

        posisi_teks = f"{posisi:,}".replace(",", ".")

        status.config(
            text=(
                f"Pesanan ditemukan pada indeks {posisi_teks} "
                f"di data terurut.\n"
                f"{jumlah_teks} perbandingan.\n"
                f"Waktu proses: {waktu_ms:.2f} ms."
            )
        )

    tk.Button(
        frame_input,
        text="CARI",
        font=("Segoe UI", 9, "bold"),
        bg=PINK,
        fg=WHITE,
        activebackground=PINK_HOVER,
        activeforeground=WHITE,
        relief="flat",
        cursor="hand2",
        command=proses_search
    ).grid(row=0, column=2, padx=(0, 0), pady=4)

    frame_input.grid_columnconfigure(3, weight=1)

# ===== DAFTAR MENU SIDEBAR =====
judul_menu("DATA")
buat_menu("Load", muat_data)

judul_menu("M1 - DATA PESANAN")
buat_menu("ARRAY - LIHAT PESANAN", tampilkan_pesanan_array)

# Menu berikutnya akan kita aktifkan setelah fitur pertama berhasil.
buat_menu("ARRAY - TAMBAH PESANAN REGULER", tambah_pesanan_reguler)
buat_menu("ARRAY - TAMBAH PESANAN PRIORITAS", tambah_pesanan_prioritas)
buat_menu("ARRAY - TAMBAH PESANAN VIP", tambah_pesanan_vip)
buat_menu("ARRAY - HAPUS PESANAN", hapus_pesanan_array)
buat_menu("LINKED LIST - LIHAT PESANAN", tampilkan_pesanan_linked_list)
buat_menu("LINKEDLIST - TAMBAH REGULER", tambah_pesanan_reguler_linked_list)
buat_menu("LINKEDLIST - TAMBAH PRIORITAS", tambah_pesanan_prioritas_linked_list)
buat_menu("LINKEDLIST - TAMBAH VIP", tambah_pesanan_vip_linked_list)
buat_menu("LINKEDLIST - HAPUS PESANAN", hapus_pesanan_linked_list)

judul_menu("M2 - STACK DAN QUEUE")
buat_menu("STACK - POSTFIX", tampilkan_stack_postfix)
buat_menu("STACK - UNDO", tampilkan_stack_undo)
buat_menu("STACK - REDO", tampilkan_stack_redo)
buat_menu("QUEUE - ENQUEUE", tampilkan_queue_enqueue)
buat_menu("QUEUE - DEQUEUE NAIF", tampilkan_dequeue_naif)
buat_menu("QUEUE - DEQUEUE CIRCULAR", tampilkan_dequeue_circular)

judul_menu("M3 - SORT DAN SEARCH")
buat_menu("SORT - INSERTION SORT", tampilkan_insertion_sort)
buat_menu("SORT - MERGE SORT", tampilkan_merge_sort)
buat_menu("SEARCH - LINEAR SEARCH", tampilkan_linear_search)
buat_menu("SEARCH - BINARY SEARCH", tampilkan_binary_search)

# ===== STYLE TABEL =====
style = ttk.Style()
style.configure(
    "Treeview.Heading",
    font=("Segoe UI", 9, "bold")
)
style.configure(
    "Treeview",
    font=("Segoe UI", 9),
    rowheight=25
)

muat_data()

root.mainloop()
