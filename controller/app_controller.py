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
            # tipos de archivos soportados
            path = self.view.ask_open_file([("Todos soportados", "*.txt *.xlsx *.pdf"), ("Archivos de texto", "*.txt"), ("Excel", "*.xlsx"), ("PDF", "*.pdf")])
            if not path:
                return
            self.current_data = self.fm.read_file(path)
            
            self.view.txt_original.delete("1.0", "end")
            try:
                # Intentar decodificar para mostrar en el area de texto
                text_content = self.current_data.decode("utf-8")
                self.view.txt_original.insert("1.0", text_content)
            except UnicodeDecodeError:
                # Si es binario, mostrar marcador de posicion
                self.view.txt_original.insert("1.0", f"<Contenido binario: {len(self.current_data)} bytes>\nVista previa no disponible.")
                
            self.view.txt_dict.delete("1.0", "end")
            self.view.lbl_stats.config(text="Estadisticas: ")
        except Exception as e:
            self.view.show_error(str(e))

    def on_compress(self):
        try:
            # Si el texto se edito manualmente en la interfaz, la compresion o descompresion partira desde ahi
            # Para soporte binario, debemos preferir los current_data cargados si no se modificaron.
            
            ui_content = self.view.txt_original.get("1.0", "end-1c")
            
            # Verificar si el contenido de la interfaz es el marcador de posicion
            if ui_content.startswith("<Contenido binario:") and "Vista previa no disponible" in ui_content:
                # Usar datos binarios almacenados en cache
                data_to_compress = self.current_data
            else:
                # Verificar si el usuario podria haber escrito algo
                data_to_compress = ui_content.encode("utf-8")
                self.current_data = data_to_compress

            pairs, dictionary = self.codec.compress(data_to_compress)
            self.current_pairs = pairs
            self.current_dict = dictionary
            self.view.txt_dict.delete("1.0", "end")
            
            # Limitar la visualizacion del diccionario por rendimiento
            # Las claves/valores del diccionario son bytes, asi que se usa la funcion repr() o hex
            full_dict_str = ""
            for k, v in dictionary.items():
                k_str = k.hex() if isinstance(k, bytes) else str(k)
                v_str = v.hex() if isinstance(v, bytes) else str(v)
                full_dict_str += f"{k_str}: {v_str}\n"
            
            # Truncar para mejor visualizacion, solo para visualizar
            if len(full_dict_str) > 50000:
                self.view.txt_dict.insert("end", full_dict_str[:50000] + "\n... (truncado)")
            else:
                self.view.txt_dict.insert("end", full_dict_str)

            original_size = len(data_to_compress)
            # Estimacion aproximada del tamano comprimido: num_pairs * (tamano de int + tamano de char/byte)
            # El tamano real del archivo coincide con lo que hace write_compressed
            compressed_size = 0
            for idx, ch_bytes in pairs:
                # En archivo: "index|hex_char\n"
                # longitud del index + 1 (|) + 2 (hex) + 1 (\n) aprox
                # la longitud de idx varia
                line_len = len(str(idx)) + 1 + 2 + 1 
                compressed_size += line_len
            
            ratio = 0 if original_size == 0 else 100 * (1 - compressed_size / original_size)
            self.view.lbl_stats.config(
                text=f"Original: {original_size} bytes, "
                     f"Comprimido (est): {compressed_size} bytes, "
                     f"Compresion: {ratio:.2f}%"
            )
        except Exception as e:
            self.view.show_error(str(e))

    def on_save_compressed(self):
        if not self.current_pairs:
            self.view.show_error("No hay datos comprimidos")
            return
        path = self.view.ask_save_file(".lz78", [("Archivos LZ78", "*.lz78")])
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
            path = self.view.ask_open_file([("Archivos LZ78", "*.lz78")])
            if not path:
                return
            self.current_pairs = self.fm.read_compressed(path)
            self.view.txt_dict.delete("1.0", "end")
            self.view.txt_dict.insert("1.0", f"Se cargaron {len(self.current_pairs)} pares.\nListo para descomprimir.")
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
                self.view.txt_original.insert("1.0", f"<Contenido binario: {len(data)} bytes>\nVista previa no disponible.")

            self.view.txt_dict.delete("1.0", "end")
            
            # Mostrar diccionario
            full_dict_str = ""
            for k, v in dictionary.items():
                k_str = k.hex() if isinstance(k, bytes) else str(k)
                v_str = v.hex() if isinstance(v, bytes) else str(v)
                full_dict_str += f"{k_str}: {v_str}\n"
            
            if len(full_dict_str) > 50000:
                self.view.txt_dict.insert("end", full_dict_str[:50000] + "\n... (truncado)")
            else:
                self.view.txt_dict.insert("end", full_dict_str)
                
        except Exception as e:
            self.view.show_error(str(e))

    def on_save_text(self):
        if not self.current_data:
            self.view.show_error("No hay datos para guardar")
            return
        
        # Determinar extension por defecto
        path = self.view.ask_save_file(".txt", [("Todos los archivos", "*.*"), ("Archivos de texto", "*.txt"), ("Excel", "*.xlsx"), ("PDF", "*.pdf")])
        if not path:
            return
        try:
            self.fm.write_file(path, self.current_data)
            self.view.show_info("Archivo guardado")
        except Exception as e:
            self.view.show_error(str(e))
