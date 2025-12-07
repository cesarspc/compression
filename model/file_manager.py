# model/file_manager.py
from pathlib import Path

class FileManager:
    def read_text(self, path: str) -> str:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError("Archivo no encontrado")
        data = p.read_text(encoding="utf-8")
        if not data:
            raise ValueError("Archivo vacío")
        return data

    def write_text(self, path: str, text: str):
        Path(path).write_text(text, encoding="utf-8")

    def write_compressed(self, path: str, pairs):
        # formato simple: index:char por línea
        with open(path, "w", encoding="utf-8") as f:
            for idx, ch in pairs:
                ch_esc = ch.replace("\\", "\\\\").replace("|", "\\|")
                f.write(f"{idx}|{ch_esc}\n")

    def read_compressed(self, path: str):
        pairs = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.rstrip("\n")
                if not line:
                    continue
                idx_str, ch_esc = line.split("|", 1)
                ch = ch_esc.replace("\\|", "|").replace("\\\\", "\\")
                pairs.append((int(idx_str), ch))
        return pairs

    def write_dict_and_code(self, path: str, pairs, dictionary):
        with open(path, "w", encoding="utf-8") as f:
            f.write("Diccionario:\n")
            for k, v in dictionary.items():
                f.write(f"{k}: {v}\n")
            f.write("\nCodigo:\n")
            for idx, ch in pairs:
                f.write(f"({idx},'{ch}') ")
