# view/main_view.py
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

class MainView(tk.Tk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("Compresor LZ78")
        self.geometry("800x600")

        frame_buttons = tk.Frame(self)
        frame_buttons.pack(fill="x", pady=5)

        tk.Button(frame_buttons, text="Cargar texto",
                  command=self.controller.on_load_text).pack(side="left")
        tk.Button(frame_buttons, text="Comprimir",
                  command=self.controller.on_compress).pack(side="left")
        tk.Button(frame_buttons, text="Guardar comprimido",
                  command=self.controller.on_save_compressed).pack(side="left")
        tk.Button(frame_buttons, text="Cargar comprimido",
                  command=self.controller.on_load_compressed).pack(side="left")
        tk.Button(frame_buttons, text="Descomprimir",
                  command=self.controller.on_decompress).pack(side="left")
        tk.Button(frame_buttons, text="Guardar texto",
                  command=self.controller.on_save_text).pack(side="left")

        self.txt_original = scrolledtext.ScrolledText(self, height=10)
        self.txt_original.pack(fill="both", expand=True)

        self.txt_dict = scrolledtext.ScrolledText(self, height=10)
        self.txt_dict.pack(fill="both", expand=True)

        self.lbl_stats = tk.Label(self, text="Estadísticas: ")
        self.lbl_stats.pack(fill="x")

    def ask_open_file(self, filetypes):
        return filedialog.askopenfilename(filetypes=filetypes)

    def ask_save_file(self, defaultextension, filetypes):
        return filedialog.asksaveasfilename(defaultextension=defaultextension,
                                            filetypes=filetypes)

    def show_error(self, msg: str):
        messagebox.showerror("Error", msg)

    def show_info(self, msg: str):
        messagebox.showinfo("Info", msg)
