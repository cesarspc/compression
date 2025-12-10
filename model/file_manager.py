import os

class FileManager:
    def read_file(self, path: str) -> bytes:
        if not os.path.exists(path):
            raise FileNotFoundError("Archivo no encontrado")
        with open(path, "rb") as f:
            data = f.read()
        if not data:
            raise ValueError("Archivo vacío")
        return data

    def write_file(self, path: str, data: bytes):
        with open(path, "wb") as f:
            f.write(data)

    def write_compressed(self, path: str, pairs):
        # Format: index|hex_string
        # Example: 0|41 (where 41 is 'A' in hex)
        # Empty byte is represented as empty string
        with open(path, "w", encoding="utf-8") as f:
            for idx, ch_bytes in pairs:
                # Convert bytes to hex string for storage
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
                    # Handle possible corruption or format error
                    continue
        return pairs

    def write_dict_and_code(self, path: str, pairs, dictionary):
        with open(path, "w", encoding="utf-8") as f:
            f.write("Diccionario (Bytes en Hex):\n")
            for k, v in dictionary.items():
                if isinstance(v, str): # Legacy check just in case
                    val_str = v
                elif isinstance(v, bytes):
                    val_str = v.hex()
                else:
                    val_str = str(v)
                    
                # Store key also as hex if it's bytes (which it is now)
                key_str = k.hex() if isinstance(k, bytes) else str(k)
                f.write(f"{key_str}: {val_str}\n")
                
            f.write("\nCodigo:\n")
            for idx, ch_bytes in pairs:
                f.write(f"({idx},'{ch_bytes.hex()}') ")
