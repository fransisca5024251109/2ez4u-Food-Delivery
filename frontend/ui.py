import time
import tkinter as tk
from tkinter import ttk, messagebox

from backend.m1_pesanan import (
    muat_pesanan, buat_pesanan, format_pesanan, cek_konsistensi
)
from backend.m2_antrean import (
    ManajerAntrean, hitung_ekspresi, muat_pesanan_antre, bandingkan_dequeue
)
from backend.m3_laporan import (
    muat_laporan, insertion_sort, merge_sort, linear_search, binary_search,
    siapkan_binary_search
)


class FoodDeliveryApp:
    """Satu jendela utama untuk fitur M1, M2, dan M3."""

    BG = "#eef1f5"
    NAVY = "#244363"
    NAVY_DARK = "#1b3046"
    BLUE = "#294967"
    BORDER = "#c4cbd3"
    MUTED = "#68798a"

    def __init__(self, root):
        self.root = root
        self.root.title("2EZ4U Food Delivery")
        self.root.geometry("1020x680")
        self.root.minsize(900, 600)
        self.root.configure(bg=self.BG)

        self.array = None
        self.linked = None
        self.antrean = ManajerAntrean()
        self.data_laporan = []
        self.active_key = None
        self.current_form = {}
        self.log_messages = []

        self._style()
        self._build_shell()
        self.show_home()
        self._log("siap", "Aplikasi siap. Pilih menu di sebelah kiri.")

    def _style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background=self.BG)
        style.configure("TLabel", background=self.BG, foreground="#263442",
                        font=("Arial", 9))
        style.configure("TButton", font=("Arial", 8, "bold"), padding=(5, 5),
                        background="#ffffff", foreground="#283747")
        style.map("TButton",
                  background=[("active", "#dce5ee"), ("pressed", "#c7d5e4")])
        style.configure("Nav.TButton", anchor="w", font=("Arial", 8, "bold"),
                        padding=(5, 5), background="#ffffff")
        style.configure("Section.TLabel", background=self.BG,
                        foreground="#68798a", font=("Arial", 8, "bold"))
        style.configure("Header.TLabel", background=self.NAVY,
                        foreground="white", font=("Arial", 12, "bold"))
        style.configure("Subheader.TLabel", background=self.NAVY,
                        foreground="#dce6f0", font=("Arial", 8))

    def _build_shell(self):
        # Header
        header = tk.Frame(self.root, bg=self.NAVY, height=48)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="2EZ4U Food Delivery", bg=self.NAVY,
                 fg="white", font=("Arial", 13, "bold")).pack(
                     anchor="w", padx=14, pady=(7, 0))
        tk.Label(header, text="MILESTONE 1–3", bg=self.NAVY,
                 fg="#d8e3ee", font=("Arial", 7, "bold")).pack(
                     anchor="w", padx=14)

        # Main split
        main = tk.Frame(self.root, bg=self.BG)
        main.pack(fill="both", expand=True, padx=8, pady=(5, 4))
        main.rowconfigure(0, weight=1)
        main.columnconfigure(1, weight=1)

        # Sidebar with scrolling
        nav_outer = tk.Frame(main, bg="#dfe4ea", width=235,
                             highlightbackground=self.BORDER, highlightthickness=1)
        nav_outer.grid(row=0, column=0, sticky="nsw", padx=(0, 8))
        nav_outer.grid_propagate(False)
        nav_outer.rowconfigure(0, weight=1)
        nav_outer.columnconfigure(0, weight=1)
        self.nav_canvas = tk.Canvas(nav_outer, bg="#e8ecf1", width=220,
                                    highlightthickness=0, borderwidth=0)
        self.nav_canvas.grid(row=0, column=0, sticky="nsew")
        nav_scroll = ttk.Scrollbar(nav_outer, orient="vertical",
                                   command=self.nav_canvas.yview)
        nav_scroll.grid(row=0, column=1, sticky="ns")
        self.nav_canvas.configure(yscrollcommand=nav_scroll.set)
        self.nav_frame = tk.Frame(self.nav_canvas, bg="#e8ecf1")
        self.nav_window = self.nav_canvas.create_window(
            (0, 0), window=self.nav_frame, anchor="nw", width=218)
        self.nav_frame.bind("<Configure>", self._nav_configure)
        self.nav_canvas.bind("<Configure>", self._nav_canvas_configure)

        self._section("DATA")
        self._nav_button("Load", self.load_all_data)

        self._section("M1 - DATA PESANAN")
        self._nav_button("ARRAY - LIHAT PESANAN", lambda: self.show_m1("Array", "Lihat pesanan"))
        self._nav_button("ARRAY - TAMBAH PESANAN REGULER", lambda: self.show_m1("Array", "Tambah Reguler"))
        self._nav_button("ARRAY - TAMBAH PESANAN PRIORITAS", lambda: self.show_m1("Array", "Tambah Prioritas"))
        self._nav_button("ARRAY - TAMBAH PESANAN VIP", lambda: self.show_m1("Array", "Tambah VIP"))
        self._nav_button("ARRAY - HAPUS PESANAN", lambda: self.show_m1("Array", "Hapus pesanan"))
        self._nav_button("LINKEDLIST - LIHAT PESANAN", lambda: self.show_m1("Linked List", "Lihat pesanan"))
        self._nav_button("LINKEDLIST - TAMBAH PESANAN REGULER", lambda: self.show_m1("Linked List", "Tambah Reguler"))
        self._nav_button("LINKEDLIST - TAMBAH PESANAN PRIORITAS", lambda: self.show_m1("Linked List", "Tambah Prioritas"))
        self._nav_button("LINKEDLIST - TAMBAH PESANAN VIP", lambda: self.show_m1("Linked List", "Tambah VIP"))
        self._nav_button("LINKEDLIST - HAPUS PESANAN", lambda: self.show_m1("Linked List", "Hapus pesanan"))

        self._section("M2 - STACK DAN QUEUE")
        self._nav_button("STACK - POSTFIX (MESIN KASIR)", self.show_m2_calculator)
        self._nav_button("STACK - UNDO", self.undo_m2)
        self._nav_button("STACK - REDO", self.redo_m2)
        self._nav_button("QUEUE - ENQUEUE", self.show_m2)
        self._nav_button("QUEUE - DEQUEUE NAIF", self.dequeue_naif)
        self._nav_button("QUEUE - DEQUEUE CIRCULAR", self.dequeue_circular)

        self._section("M3 - SORT DAN SEARCH")
        self._nav_button("SORT - INSERTION SORT", lambda: self.show_m3("Insertion Sort"))
        self._nav_button("SORT - MERGE SORT", lambda: self.show_m3("Merge Sort"))
        self._nav_button("SEARCH - LINEAR SEARCH", lambda: self.show_m3("Linear Search"))
        self._nav_button("SEARCH - BINARY SEARCH", lambda: self.show_m3("Binary Search"))

        # Work area
        work = tk.Frame(main, bg="white", highlightbackground=self.BORDER,
                        highlightthickness=1)
        work.grid(row=0, column=1, sticky="nsew")
        work.rowconfigure(1, weight=1)
        work.columnconfigure(0, weight=1)
        self.work_header = tk.Frame(work, bg="#ffffff", height=88)
        self.work_header.grid(row=0, column=0, sticky="ew")
        self.work_header.grid_propagate(False)
        self.work_body = tk.Frame(work, bg="white")
        self.work_body.grid(row=1, column=0, sticky="nsew")
        self.work_body.rowconfigure(0, weight=1)
        self.work_body.columnconfigure(0, weight=1)

        # Command panel
        log_frame = tk.Frame(self.root, bg=self.BG)
        log_frame.pack(fill="x", padx=8, pady=(0, 3))
        tk.Label(log_frame, text="COMMAND", bg=self.BG, fg=self.MUTED,
                 font=("Arial", 8, "bold")).pack(anchor="w")
        self.log_box = tk.Text(log_frame, height=4, wrap="word",
                               font=("Courier New", 8), bg="white",
                               relief="solid", bd=1, highlightthickness=0)
        self.log_box.pack(fill="x")
        self.log_box.configure(state="disabled")

        self.status_var = tk.StringVar(value="siap")
        status = tk.Frame(self.root, bg=self.NAVY_DARK, height=25)
        status.pack(fill="x", side="bottom")
        status.pack_propagate(False)
        tk.Label(status, textvariable=self.status_var, bg=self.NAVY_DARK,
                 fg="white", font=("Arial", 8)).pack(side="left", padx=10, pady=4)

    def _nav_configure(self, _event=None):
        self.nav_canvas.configure(scrollregion=self.nav_canvas.bbox("all"))

    def _nav_canvas_configure(self, event):
        self.nav_canvas.itemconfigure(self.nav_window, width=event.width)

    def _section(self, title):
        tk.Label(self.nav_frame, text=title, bg="#e8ecf1", fg="#637487",
                 font=("Arial", 8, "bold"), anchor="w").pack(
                     fill="x", padx=6, pady=(7, 2))

    def _nav_button(self, title, command):
        button = ttk.Button(self.nav_frame, text=title, command=command,
                            style="Nav.TButton")
        button.pack(fill="x", padx=5, pady=1)
        return button

    def _clear_work(self):
        for widget in self.work_header.winfo_children():
            widget.destroy()
        for widget in self.work_body.winfo_children():
            widget.destroy()
        self.work_header.configure(height=88)

    def _header(self, title, description=""):
        tk.Label(self.work_header, text=title, bg="white", fg="#202a35",
                 font=("Arial", 11, "bold"), anchor="w").pack(
                     fill="x", padx=14, pady=(10, 2))
        if description:
            tk.Label(self.work_header, text=description, bg="white",
                     fg="#647386", font=("Arial", 8), anchor="w").pack(
                         fill="x", padx=14)

    def _log(self, operation, message):
        line = "{}  ->  {}".format(operation, message)
        self.log_messages.append(line)
        if len(self.log_messages) > 100:
            self.log_messages = self.log_messages[-100:]
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.insert("end", "\n".join(self.log_messages[-12:]))
        self.log_box.see("end")
        self.log_box.configure(state="disabled")
        self.status_var.set(message)

    def _write_output(self, text, clear=True):
        if not hasattr(self, "output") or not self.output.winfo_exists():
            return
        if clear:
            self.output.delete("1.0", "end")
        self.output.insert("end", str(text) + "\n")
        self.output.see("end")

    def _make_output(self, parent=None, height=15):
        parent = parent or self.work_body
        holder = tk.Frame(parent, bg="white")
        holder.pack(fill="both", expand=True, padx=12, pady=10)
        self.output = tk.Text(holder, wrap="word", font=("Courier New", 9),
                              bg="white", relief="solid", bd=1)
        scroll = ttk.Scrollbar(holder, orient="vertical", command=self.output.yview)
        self.output.configure(yscrollcommand=scroll.set)
        self.output.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        return self.output

    def show_home(self):
        self._clear_work()
        self._header("Selamat datang di 2EZ4U Food Delivery",
                     "Pilih fitur melalui menu di sebelah kiri.")
        info = tk.Frame(self.work_body, bg="white")
        info.pack(fill="both", expand=True, padx=14, pady=14)
        tk.Label(info, text="2EZ4U Food Delivery", bg="white",
                 fg=self.NAVY, font=("Arial", 20, "bold")).pack(anchor="w", pady=(12, 6))
        tk.Label(info, text="Milestone yang tersedia: M1 Data Pesanan, M2 Antrean dan Undo, M3 Laporan dan Pencarian.",
                 bg="white", fg="#4d5d6d", wraplength=650, justify="left").pack(anchor="w")
        tk.Label(info, text="Klik Load untuk memuat CSV sebelum menggunakan fitur.", bg="white",
                 fg="#4d5d6d").pack(anchor="w", pady=8)

    def load_all_data(self):
        try:
            self.array, self.linked = muat_pesanan("data/pesanan.csv")
            self.data_laporan = muat_laporan("data/pesanan.csv")
            antre = muat_pesanan_antre("data/pesanan.csv")
            self.antrean.muat_data(antre)
            self._log("load", "M1/M3: {} pesanan; M2: {} pesanan ANTRE".format(
                self.array.jumlah, len(antre)))
            self.show_home()
        except Exception as error:
            messagebox.showerror("Gagal memuat data", str(error))
            self._log("load", "Gagal: {}".format(error))

    def _ensure_m1(self):
        if self.array is None or self.linked is None:
            self.load_all_data()
        if self.array is None or self.linked is None:
            raise RuntimeError("Data belum berhasil dimuat.")

    def show_m1(self, structure, operation):
        try:
            self._ensure_m1()
        except Exception as error:
            messagebox.showerror("Data belum siap", str(error))
            return
        self.active_key = ("m1", structure, operation)
        self._clear_work()
        descriptions = {
            "Lihat pesanan": "get: menampilkan pesanan berdasarkan indeks.",
            "Tambah Reguler": "append: pesanan biasa mengantre di barisan paling belakang.",
            "Tambah Prioritas": "insert: pesanan prioritas masuk ke bagian tengah.",
            "Tambah VIP": "insert di indeks 0: pesanan VIP masuk paling depan.",
            "Hapus pesanan": "hapus: menghapus pesanan berdasarkan indeks.",
        }
        self._header("{}: pesanan {}".format(
            structure, descriptions[operation].split(": ")[1]),
            descriptions[operation])
        form = tk.Frame(self.work_header, bg="white")
        form.pack(fill="x", padx=14, pady=(5, 7))
        self.current_form = {}
        if operation in ("Lihat pesanan", "Hapus pesanan"):
            self._add_field(form, "Indeks", "0", 0)
        else:
            self._add_field(form, "Nama pelanggan", "Pelanggan Baru", 0)
            self._add_field(form, "Restoran", "restoran", 1)
            self._add_field(form, "Menu", "menu", 2)
            self._add_field(form, "Harga", "15000", 3)
            self._add_field(form, "OID", "O-NEW-001", 4)
        ttk.Button(form, text="JALANKAN", command=self.run_m1).grid(
            row=0, column=6, padx=(8, 0), sticky="e")
        self._make_output(height=15)
        self._write_output("Data siap. Pilih parameter lalu jalankan operasi.")
        self._log("M1", "{} - {}".format(structure, operation))

    def _add_field(self, parent, label, default, col):
        frame = tk.Frame(parent, bg="white")
        frame.grid(row=0, column=col, sticky="w", padx=(0, 6))
        tk.Label(frame, text=label, bg="white", fg="#5c6a79",
                 font=("Arial", 8)).pack(anchor="w")
        var = tk.StringVar(value=default)
        ttk.Entry(frame, textvariable=var, width=15).pack(anchor="w", pady=(2, 0))
        self.current_form[label] = var

    def run_m1(self):
        try:
            self._ensure_m1()
            structure, operation = self.active_key[1], self.active_key[2]
            main = self.array if structure == "Array" else self.linked
            other = self.linked if structure == "Array" else self.array
            if operation in ("Lihat pesanan", "Hapus pesanan"):
                index = int(self.current_form["Indeks"].get())
                if index < 0 or index >= main.jumlah:
                    raise ValueError("Indeks di luar jangkauan.")
                start = time.perf_counter()
                if operation == "Lihat pesanan":
                    order = main.get(index)
                else:
                    order = main.hapus(index)
                elapsed = (time.perf_counter() - start) * 1000
                if operation == "Hapus pesanan":
                    other.hapus(index)
                result = "{} indeks {} pada {}\n\n{}".format(
                    operation, index, structure, format_pesanan(order))
            else:
                priority = {"Tambah Reguler": 3, "Tambah Prioritas": 2,
                            "Tambah VIP": 1}[operation]
                name = self.current_form["Nama pelanggan"].get().strip()
                resto = self.current_form["Restoran"].get().strip()
                menu = self.current_form["Menu"].get().strip()
                oid = self.current_form["OID"].get().strip()
                price = int(self.current_form["Harga"].get())
                if not all((name, resto, menu, oid)):
                    raise ValueError("Semua kolom harus diisi.")
                if price < 0:
                    raise ValueError("Harga tidak boleh negatif.")
                order = buat_pesanan(oid, name, resto, menu, price, priority)
                start = time.perf_counter()
                method = {"Tambah Reguler": "tambah_reguler",
                          "Tambah Prioritas": "tambah_prioritas",
                          "Tambah VIP": "tambah_vip"}[operation]
                getattr(main, method)(order)
                elapsed = (time.perf_counter() - start) * 1000
                getattr(other, method)(order)
                result = "{} berhasil pada {}\n\n{}".format(
                    operation, structure, format_pesanan(order))
            result += "\n\nWaktu operasi: {:.4f} ms".format(elapsed)
            result += "\nJumlah Array: {}\nJumlah Linked List: {}".format(
                self.array.jumlah, self.linked.jumlah)
            self._write_output(result)
            self._log("M1", "{} / {}".format(structure, operation),
                      "{:.4f} ms; konsisten={}".format(elapsed,
                                                       cek_konsistensi(self.array, self.linked)[0]))
        except Exception as error:
            messagebox.showerror("Operasi M1 gagal", str(error))

    def show_m2(self):
        self._clear_work()
        self.active_key = ("m2", "queue")
        self._header("Antrean FIFO", "Enqueue menambah ke belakang; Dequeue melayani pesanan paling depan.")
        form = tk.Frame(self.work_header, bg="white")
        form.pack(fill="x", padx=14, pady=(6, 8))
        self.queue_entry = tk.StringVar(value="Pesanan Baru")
        tk.Label(form, text="Nama/OID pesanan", bg="white").grid(row=0, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.queue_entry, width=25).grid(row=1, column=0, padx=(0, 8))
        ttk.Button(form, text="ENQUEUE", command=self.enqueue_m2).grid(row=1, column=1, padx=3)
        ttk.Button(form, text="DEQUEUE", command=self.dequeue_one).grid(row=1, column=2, padx=3)
        ttk.Button(form, text="UNDO", command=self.undo_m2).grid(row=1, column=3, padx=3)
        ttk.Button(form, text="REDO", command=self.redo_m2).grid(row=1, column=4, padx=3)
        ttk.Button(form, text="CEK KONSISTENSI", command=self.check_m2).grid(row=1, column=5, padx=3)
        ttk.Button(form, text="BANDINGKAN WAKTU", command=self.compare_queue).grid(row=1, column=6, padx=3)
        self._make_output()
        self._write_output("M2 siap. Klik Load untuk memuat data ANTRE.")
        self._log("M2", "Antrean FIFO dibuka")

    def show_m2_calculator(self):
        self._clear_work()
        self.active_key = ("m2", "calculator")
        self._header("Kalkulator Stack", "Konversi infix ke postfix dan evaluasi menggunakan Stack.")
        form = tk.Frame(self.work_header, bg="white")
        form.pack(fill="x", padx=14, pady=(6, 8))
        self.expr_var = tk.StringVar(value="(3 * 12000) + (2 * 8500) - 5000")
        tk.Label(form, text="Ekspresi matematika", bg="white").grid(row=0, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.expr_var, width=50).grid(row=1, column=0, padx=(0, 8))
        ttk.Button(form, text="HITUNG", command=self.calculate_m2).grid(row=1, column=1)
        self._make_output()
        self._write_output("Contoh hasil yang diharapkan: 48000.0")
        self._log("M2", "Kalkulator Stack dibuka")

    def enqueue_m2(self):
        try:
            if self.array is None:
                self.load_all_data()
            value = self.queue_entry.get().strip()
            if not value:
                raise ValueError("Masukkan nama atau OID pesanan.")
            self.antrean.enqueue(value)
            self._write_output("Enqueue berhasil: {}\nJumlah antrean: {}\nKonsisten: {}".format(
                value, self.antrean.naif.ukuran(), self.antrean.konsisten()), clear=False)
            self._log("M2", "Enqueue", value)
            self.queue_entry.set("")
        except Exception as error:
            messagebox.showerror("Enqueue gagal", str(error))

    def dequeue_one(self):
        try:
            if self.active_key and self.active_key[0] == "m2":
                out_naif, out_circle = self.antrean.dequeue(1)
                self._write_output("Dequeue naif: {}\nDequeue circular: {}\nKonsisten: {}".format(
                    out_naif, out_circle, self.antrean.konsisten()), clear=False)
                self._log("M2", "Dequeue", "1 item; konsisten={}".format(self.antrean.konsisten()))
            else:
                self.show_m2()
                out_naif, out_circle = self.antrean.dequeue(1)
                self._write_output("Dequeue naif: {}\nDequeue circular: {}".format(out_naif, out_circle))
        except Exception as error:
            messagebox.showerror("Dequeue gagal", str(error))

    def dequeue_naif(self):
        try:
            self._clear_work()
            self.active_key = ("m2", "queue")
            self._header("Queue - Dequeue Naif", "Mengambil elemen terdepan dari antrean berbasis list.")
            self._make_output()
            start = time.perf_counter()
            item = self.antrean.naif.dequeue()
            elapsed = (time.perf_counter() - start) * 1000
            self._write_output("Dequeue naif: {}\\nSisa antrean naif: {}\\nGeseran kumulatif: {}\\nWaktu: {:.4f} ms".format(
                item, self.antrean.naif.ukuran(), self.antrean.naif.total_geser, elapsed))
            self._log("M2", "queue_dequeue_naif", "{:.4f} ms".format(elapsed))
        except Exception as error:
            messagebox.showerror("Dequeue naif gagal", str(error))

    def dequeue_circular(self):
        try:
            self._clear_work()
            self.active_key = ("m2", "queue")
            self._header("Queue - Dequeue Circular", "Mengambil elemen terdepan dari circular queue.")
            self._make_output()
            start = time.perf_counter()
            item = self.antrean.melingkar.dequeue()
            elapsed = (time.perf_counter() - start) * 1000
            self._write_output("Dequeue circular: {}\\nSisa antrean circular: {}\\nKapasitas: {}\\nWaktu: {:.4f} ms".format(
                item, self.antrean.melingkar.ukuran(), self.antrean.melingkar.kapasitas(), elapsed))
            self._log("M2", "queue_dequeue_circular", "{:.4f} ms".format(elapsed))
        except Exception as error:
            messagebox.showerror("Dequeue circular gagal", str(error))

    def undo_m2(self):
        result = self.antrean.undo()
        self._write_output(result, clear=False)
        self._log("M2", "Undo", result)

    def redo_m2(self):
        result = self.antrean.redo()
        self._write_output(result, clear=False)
        self._log("M2", "Redo", result)

    def check_m2(self):
        result = self.antrean.konsisten()
        self._write_output("Konsistensi Queue: {}".format(result), clear=False)
        self._log("M2", "Cek konsistensi", str(result))

    def compare_queue(self):
        try:
            data = muat_pesanan_antre("data/pesanan.csv")
            result = bandingkan_dequeue(data, min(100, len(data)))
            text = ("Perbandingan {} dequeue:\n"
                    "Queue naif: {:.4f} ms\nGeseran naif: {}\n"
                    "Circular Queue: {:.4f} ms\nGeseran circular: {}").format(
                        min(100, len(data)), result["waktu_naif_ms"],
                        result["geseran_naif"], result["waktu_melingkar_ms"],
                        result["geseran_melingkar"])
            self._write_output(text, clear=False)
            self._log("M2", "Bandingkan Queue", "perbandingan selesai")
        except Exception as error:
            messagebox.showerror("Perbandingan gagal", str(error))

    def calculate_m2(self):
        try:
            expression = self.expr_var.get()
            postfix, value = hitung_ekspresi(expression)
            self._write_output("Infix: {}\nPostfix: {}\nHasil: {}".format(
                expression, " ".join(postfix), value))
            self._log("M2", "Kalkulator", "hasil={}".format(value))
        except Exception as error:
            messagebox.showerror("Kalkulator gagal", str(error))

    def show_m3(self, algorithm="Merge Sort"):
        self._clear_work()
        self.active_key = ("m3", algorithm)
        descriptions = {
            "Insertion Sort": "Mengurutkan sampel hingga 5.000 data untuk menjaga demo tetap responsif.",
            "Merge Sort": "Mengurutkan seluruh data laporan menggunakan Merge Sort.",
            "Linear Search": "Mencari OID secara berurutan dari awal data.",
            "Binary Search": "Mengurutkan berdasarkan OID terlebih dahulu, lalu mencari dengan Binary Search.",
        }
        self._header("M3 - Laporan dan Pencarian", descriptions[algorithm])
        form = tk.Frame(self.work_header, bg="white")
        form.pack(fill="x", padx=14, pady=(5, 8))
        self.m3_algorithm = tk.StringVar(value=algorithm)
        tk.Label(form, text="Algoritma", bg="white").grid(row=0, column=0, sticky="w")
        ttk.Combobox(form, textvariable=self.m3_algorithm,
                     values=("Insertion Sort", "Merge Sort", "Linear Search", "Binary Search"),
                     state="readonly", width=19).grid(row=1, column=0, padx=(0, 8))
        self.m3_key = tk.StringVar(value="Harga")
        tk.Label(form, text="Kunci sorting", bg="white").grid(row=0, column=1, sticky="w")
        ttk.Combobox(form, textvariable=self.m3_key,
                     values=("OID", "Harga", "Status", "Prioritas"),
                     state="readonly", width=13).grid(row=1, column=1, padx=(0, 8))
        self.m3_target = tk.StringVar(value="O-000017")
        tk.Label(form, text="OID yang dicari", bg="white").grid(row=0, column=2, sticky="w")
        ttk.Entry(form, textvariable=self.m3_target, width=18).grid(row=1, column=2, padx=(0, 8))
        ttk.Button(form, text="MUAT DATA CSV", command=self.load_m3).grid(row=1, column=3, padx=3)
        ttk.Button(form, text="JALANKAN", command=self.run_m3).grid(row=1, column=4, padx=3)
        self._make_output()
        self._write_output("M3 siap. Klik Muat Data CSV untuk memuat data pesanan.")
        self._log("M3", algorithm)

    def load_m3(self):
        try:
            self.data_laporan = muat_laporan("data/pesanan.csv")
            self._write_output("Berhasil memuat {} pesanan.".format(len(self.data_laporan)), clear=False)
            self._log("M3", "Muat CSV", "{} pesanan".format(len(self.data_laporan)))
        except Exception as error:
            messagebox.showerror("Gagal memuat CSV", str(error))

    def run_m3(self):
        if not self.data_laporan:
            try:
                self.data_laporan = muat_laporan("data/pesanan.csv")
            except Exception as error:
                messagebox.showerror("Gagal memuat CSV", str(error))
                return
        algorithm = self.m3_algorithm.get()
        key = {"OID": "oid", "Harga": "harga", "Status": "status",
               "Prioritas": "prioritas"}[self.m3_key.get()]
        try:
            if algorithm == "Insertion Sort":
                sample = self.data_laporan[:5000]
                result = insertion_sort(sample, key)
                self._write_output(
                    "=== INSERTION SORT ===\nData yang diurutkan: {}\nBatas backend: 20000\n"
                    "Perbandingan: {}\nWaktu: {:.4f} ms\n5 data pertama:\n{}".format(
                        len(sample), result["perbandingan"], result["waktu_ms"],
                        "\n".join(str(item) for item in result["data"][:5])))
            elif algorithm == "Merge Sort":
                result = merge_sort(self.data_laporan, key)
                self._write_output(
                    "=== MERGE SORT ===\nJumlah data: {}\nPerbandingan: {}\nWaktu: {:.4f} ms\n"
                    "5 data pertama:\n{}".format(
                        result["jumlah_data"], result["perbandingan"], result["waktu_ms"],
                        "\n".join(str(item) for item in result["data"][:5])))
            elif algorithm == "Linear Search":
                target = self.m3_target.get().strip()
                if not target:
                    raise ValueError("Masukkan OID yang ingin dicari.")
                result = linear_search(self.data_laporan, target, "oid")
                self._write_output(
                    "=== LINEAR SEARCH ===\nTarget: {}\nDitemukan: {}\nIndeks: {}\n"
                    "Perbandingan: {}\nWaktu: {:.4f} ms\nData: {}".format(
                        target, result["ditemukan"], result["indeks"],
                        result["perbandingan"], result["waktu_ms"], result["data"]))
            else:
                target = self.m3_target.get().strip()
                if not target:
                    raise ValueError("Masukkan OID yang ingin dicari.")
                prepared = siapkan_binary_search(self.data_laporan, "oid")
                result = binary_search(prepared["data"], target, "oid")
                self._write_output(
                    "=== BINARY SEARCH ===\nTarget: {}\nDitemukan: {}\nIndeks terurut: {}\n"
                    "Perbandingan pencarian: {}\nWaktu pencarian: {:.4f} ms\n"
                    "Waktu persiapan sorting: {:.4f} ms\nData: {}".format(
                        target, result["ditemukan"], result["indeks"],
                        result["perbandingan"], result["waktu_ms"],
                        prepared["waktu_sort_ms"], result["data"]))
            self._log("M3", algorithm, "selesai")
        except Exception as error:
            messagebox.showerror("Operasi M3 gagal", str(error))

    def show_home(self):
        self._clear_work()
        self._header("Selamat datang di 2EZ4U Food Delivery",
                     "Pilih fitur melalui menu di sebelah kiri.")
        info = tk.Frame(self.work_body, bg="white")
        info.pack(fill="both", expand=True, padx=14, pady=14)
        tk.Label(info, text="2EZ4U Food Delivery", bg="white",
                 fg=self.NAVY, font=("Arial", 20, "bold")).pack(anchor="w", pady=(12, 6))
        tk.Label(info, text="Milestone yang tersedia: M1 Data Pesanan, M2 Antrean dan Undo, M3 Laporan dan Pencarian.",
                 bg="white", fg="#4d5d6d", wraplength=650, justify="left").pack(anchor="w")
        tk.Label(info, text="Klik Load untuk memuat CSV sebelum menggunakan fitur.", bg="white",
                 fg="#4d5d6d").pack(anchor="w", pady=8)


def jalankan_ui():
    root = tk.Tk()
    app = FoodDeliveryApp(root)
    root.mainloop()


if __name__ == "__main__":
    jalankan_ui()
