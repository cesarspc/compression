# controller/app_controller.py
from model.lz78 import LZ78Codec
from model.file_manager import FileManager
from view.main_view import MainView
import os

class AppController:
    def __init__(self):
        self.codec = LZ78Codec()
        self.fm = FileManager()
        self.view = MainView(self)

        self.current_text = ""
        self.current_pairs = None
        self.current_dict = None

    def run(self):
        self.view.mainloop()

    def on_load_text(self):
        try:
            path = self.view.ask_open_file([("Text files", "*.txt")])
            if not path:
                return
            self.current_text = self.fm.read_text(path)
            self.view.txt_original.delete("1.0", "end")
            self.view.txt_original.insert("1.0", self.current_text)
            self.view.txt_dict.delete("1.0", "end")
            self.view.lbl_stats.config(text="Estadísticas: ")
        except Exception as e:
            self.view.show_error(str(e))

    def on_compress(self):
        try:
            self.current_text = self.view.txt_original.get("1.0", "end-1c")
            pairs, dictionary = self.codec.compress(self.current_text)
            self.current_pairs = pairs
            self.current_dict = dictionary
            self.view.txt_dict.delete("1.0", "end")
            for k, v in dictionary.items():
                self.view.txt_dict.insert("end", f"{k}: {v}\n")
            original_size = len(self.current_text.encode("utf-8"))
            compressed_size = len(str(pairs).encode("utf-8"))
            ratio = 0 if original_size == 0 else 100 * (1 - compressed_size / original_size)
            self.view.lbl_stats.config(
                text=f"Original: {original_size} bytes, "
                     f"Comprimido: {compressed_size} bytes, "
                     f"Compresión: {ratio:.2f}%"
            )
        except Exception as e:
            self.view.show_error(str(e))

    def on_save_compressed(self):
        if not self.current_pairs:
            self.view.show_error("No hay datos comprimidos")
            return
        path = self.view.ask_save_file(".lz78", [("LZ78 files", "*.lz78")])
        if not path:
            return
        try:
            self.fm.write_compressed(path, self.current_pairs)
            if self.current_dict is not None:
                dict_path = os.path.splitext(path)[0] + "_dict.txt"
                self.fm.write_dict_and_code(dict_path, self.current_pairs, self.current_dict)
            self.view.show_info("Archivo comprimido guardado")
        except Exception as e:
            self.view.show_error(str(e))

    def on_load_compressed(self):
        try:
            path = self.view.ask_open_file([("LZ78 files", "*.lz78")])
            if not path:
                return
            self.current_pairs = self.fm.read_compressed(path)
            self.view.txt_dict.delete("1.0", "end")
            self.view.txt_dict.insert("1.0", str(self.current_pairs))
        except Exception as e:
            self.view.show_error(str(e))

    def on_decompress(self):
        try:
            if not self.current_pairs:
                self.view.show_error("No hay datos comprimidos")
                return
            text, dictionary = self.codec.decompress(self.current_pairs)
            self.current_text = text
            self.current_dict = dictionary
            self.view.txt_original.delete("1.0", "end")
            self.view.txt_original.insert("1.0", text)
            self.view.txt_dict.delete("1.0", "end")
            for k, v in dictionary.items():
                self.view.txt_dict.insert("end", f"{k}: {v}\n")
        except Exception as e:
            self.view.show_error(str(e))

    def on_save_text(self):
        if not self.current_text:
            self.view.show_error("No hay texto para guardar")
            return
        path = self.view.ask_save_file(".txt", [("Text files", "*.txt")])
        if not path:
            return
        try:
            self.fm.write_text(path, self.current_text)
            self.view.show_info("Archivo de texto guardado")
        except Exception as e:
            self.view.show_error(str(e))
