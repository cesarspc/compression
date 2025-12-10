import os

class FileManager:
    def read_file(self, path: str) -> bytes:
        """Lee un archivo y devuelve su contenido como bytes.
        Tambien maneja los posibles errores al cargar el archivo."""
        if not os.path.exists(path):
            raise FileNotFoundError("Archivo no encontrado")
        with open(path, "rb") as f:
            data = f.read()
        if not data:
            raise ValueError("Archivo vacio")
        return data

    def write_file(self, path: str, data: bytes):
        with open(path, "wb") as f:
            f.write(data)

    def write_compressed(self, path: str, pairs):
        with open(path, "w", encoding="utf-8") as f:
            for idx, ch_bytes in pairs:
                # Convertir bytes a cadena hexadecimal para almacenamiento
                hex_str = ch_bytes.hex()
                f.write(f"{idx}|{hex_str}\n")

    def read_compressed(self, path: str):
        pairs = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.rstrip("\n")
                if not line:
                    continue
                try:
                    idx_str, hex_str = line.split("|", 1)
                    idx = int(idx_str)
                    ch_bytes = bytes.fromhex(hex_str)
                    pairs.append((idx, ch_bytes))
                except ValueError:
                    # Manejar posible corrupcion o error de formato
                    continue
        return pairs

    def write_dict_and_code(self, path: str, pairs, dictionary):
        with open(path, "w", encoding="utf-8") as f:
            f.write("Diccionario (Bytes en Hexadecimal):\n")
            for k, v in dictionary.items():
                if isinstance(v, str):
                    val_str = v
                elif isinstance(v, bytes):
                    val_str = v.hex()
                else:
                    val_str = str(v)
                    
                # Almacenar clave tambien como hexadecimal si es bytes
                key_str = k.hex() if isinstance(k, bytes) else str(k)
                f.write(f"{key_str}: {val_str}\n")
                
            f.write("\nCodigo:\n")
            for idx, ch_bytes in pairs:
                f.write(f"({idx},'{ch_bytes.hex()}') ")
