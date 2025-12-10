# vista/main_view.py
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

class MainView(tk.Tk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("Compresor LZ78")
        self.geometry("800x600")

        # Frame para los botones de control
        frame_buttons = tk.Frame(self)
        frame_buttons.pack(fill="x", pady=5)

        tk.Button(frame_buttons, text="Cargar Archivo",
                  command=self.controller.on_load_text).pack(side="left")
        tk.Button(frame_buttons, text="Comprimir",
                  command=self.controller.on_compress).pack(side="left")
        tk.Button(frame_buttons, text="Guardar comprimido",
                  command=self.controller.on_save_compressed).pack(side="left")
        tk.Button(frame_buttons, text="Cargar comprimido",
                  command=self.controller.on_load_compressed).pack(side="left")
        tk.Button(frame_buttons, text="Descomprimir",
                  command=self.controller.on_decompress).pack(side="left")
        tk.Button(frame_buttons, text="Guardar Archivo Descomprimido",
                  command=self.controller.on_save_text).pack(side="left")

        # Area de texto para mostrar contenido original
        self.txt_original = scrolledtext.ScrolledText(self, height=10)
        self.txt_original.pack(fill="both", expand=True)

        # Area de texto para mostrar diccionario
        self.txt_dict = scrolledtext.ScrolledText(self, height=10)
        self.txt_dict.pack(fill="both", expand=True)

        # Etiqueta para mostrar estadisticas
        self.lbl_stats = tk.Label(self, text="Estadisticas: ")
        self.lbl_stats.pack(fill="x")

    def ask_open_file(self, filetypes):
        """Abre dialogo para seleccionar archivo a cargar"""
        return filedialog.askopenfilename(filetypes=filetypes)

    def ask_save_file(self, defaultextension, filetypes):
        """Abre dialogo para guardar archivo"""
        return filedialog.asksaveasfilename(defaultextension=defaultextension,
                                            filetypes=filetypes)

    def show_error(self, msg: str):
        """Muestra dialogo de error"""
        messagebox.showerror("Error", msg)

    def show_info(self, msg: str):
        """Muestra dialogo de informacion"""
        messagebox.showinfo("Info", msg)
