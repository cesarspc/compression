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

        self.current_data = b""
        self.current_pairs = None
        self.current_dict = None

    def run(self):
        self.view.mainloop()

    def on_load_text(self):
        try:
            # Updated to allow all supported types
            path = self.view.ask_open_file([("All supported", "*.txt *.xlsx *.pdf"), ("Text files", "*.txt"), ("Excel", "*.xlsx"), ("PDF", "*.pdf")])
            if not path:
                return
            self.current_data = self.fm.read_file(path)
            
            self.view.txt_original.delete("1.0", "end")
            try:
                # Try to decode to show in text area
                text_content = self.current_data.decode("utf-8")
                self.view.txt_original.insert("1.0", text_content)
            except UnicodeDecodeError:
                # If binary, show placeholder
                self.view.txt_original.insert("1.0", f"<Binary content: {len(self.current_data)} bytes>\nPreview not available.")
                
            self.view.txt_dict.delete("1.0", "end")
            self.view.lbl_stats.config(text="Estadísticas: ")
        except Exception as e:
            self.view.show_error(str(e))

    def on_compress(self):
        try:
            # If manually edited text in UI, restart from that (only if it was text)
            # But for binary support, we should prefer the loaded current_data if it wasn't modified.
            # For simplicity, if the UI content matches current_data decoded, use current_data.
            # Or if valid text is in UI, encod it.
            
            ui_content = self.view.txt_original.get("1.0", "end-1c")
            
            # Check if UI content is the placeholder
            if ui_content.startswith("<Binary content:") and "Preview not available" in ui_content:
                # Use cached binary data
                data_to_compress = self.current_data
            else:
                # User might have typed something
                data_to_compress = ui_content.encode("utf-8")
                self.current_data = data_to_compress

            pairs, dictionary = self.codec.compress(data_to_compress)
            self.current_pairs = pairs
            self.current_dict = dictionary
            self.view.txt_dict.delete("1.0", "end")
            
            # limiting dictionary display for performance if too large could be good, but keeping simple for now
            # Dictionary keys/values are now bytes often, so repr() or hex needed
            full_dict_str = ""
            for k, v in dictionary.items():
                k_str = k.hex() if isinstance(k, bytes) else str(k)
                v_str = v.hex() if isinstance(v, bytes) else str(v)
                full_dict_str += f"{k_str}: {v_str}\n"
            
            # Truncate for display if massive? Let's just show it. 
            # Tkinter might choke on massive text, maybe truncate if > 10KB text
            if len(full_dict_str) > 50000:
                self.view.txt_dict.insert("end", full_dict_str[:50000] + "\n... (truncated)")
            else:
                self.view.txt_dict.insert("end", full_dict_str)

            original_size = len(data_to_compress)
            # Rough estimate of compressed size: num_pairs * (size of int + size of char/byte)
            # Actual file size matches what write_compressed does
            compressed_size = 0
            for idx, ch_bytes in pairs:
                # In file: "index|hex_char\n"
                # index length + 1 (|) + 2 (hex) + 1 (\n) approx
                # idx len varies
                line_len = len(str(idx)) + 1 + 2 + 1 
                compressed_size += line_len
            
            ratio = 0 if original_size == 0 else 100 * (1 - compressed_size / original_size)
            self.view.lbl_stats.config(
                text=f"Original: {original_size} bytes, "
                     f"Comprimido (est): {compressed_size} bytes, "
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
            self.view.txt_dict.insert("1.0", f"Loaded {len(self.current_pairs)} pairs.\nReady to decompress.")
        except Exception as e:
            self.view.show_error(str(e))

    def on_decompress(self):
        try:
            if not self.current_pairs:
                self.view.show_error("No hay datos comprimidos")
                return
            data, dictionary = self.codec.decompress(self.current_pairs)
            self.current_data = data
            self.current_dict = dictionary
            
            self.view.txt_original.delete("1.0", "end")
            try:
                text_content = data.decode("utf-8")
                self.view.txt_original.insert("1.0", text_content)
            except UnicodeDecodeError:
                self.view.txt_original.insert("1.0", f"<Binary content: {len(data)} bytes>\nPreview not available.")

            self.view.txt_dict.delete("1.0", "end")
            
            # Show dict
            full_dict_str = ""
            for k, v in dictionary.items():
                k_str = k.hex() if isinstance(k, bytes) else str(k)
                v_str = v.hex() if isinstance(v, bytes) else str(v)
                full_dict_str += f"{k_str}: {v_str}\n"
            
            if len(full_dict_str) > 50000:
                self.view.txt_dict.insert("end", full_dict_str[:50000] + "\n... (truncated)")
            else:
                self.view.txt_dict.insert("end", full_dict_str)
                
        except Exception as e:
            self.view.show_error(str(e))

    def on_save_text(self):
        if not self.current_data:
            self.view.show_error("No hay datos para guardar")
            return
        
        # Determine default extension
        # We don't track original extension, maybe we should?
        # For now defaults to .txt but user can change
        path = self.view.ask_save_file(".txt", [("All Files", "*.*"), ("Text files", "*.txt"), ("Excel", "*.xlsx"), ("PDF", "*.pdf")])
        if not path:
            return
        try:
            self.fm.write_file(path, self.current_data)
            self.view.show_info("Archivo guardado")
        except Exception as e:
            self.view.show_error(str(e))
