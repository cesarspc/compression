class LZ78Codec:
    def compress(self, data: bytes):
        if not data:
            raise ValueError("Archivo vacío")
        # Ensure input is bytes
        if isinstance(data, str):
            data = data.encode('utf-8')
            
        dictionary = {}
        current = b""
        result = []
        dict_index = 1
        
        # Iterate over bytes (integers 0-255)
        for byte_val in data:
            # Create a single-byte bytes object
            c = bytes([byte_val])
            temp = current + c
            if temp in dictionary:
                current = temp
            else:
                index = dictionary.get(current, 0)
                result.append((index, c))
                dictionary[temp] = dict_index
                dict_index += 1
                current = b""
                
        if current:
            index = dictionary.get(current, 0)
            result.append((index, b""))  # último par
            
        return result, dictionary

    def decompress(self, pairs):
        dictionary = {}
        result = []
        dict_index = 1
        
        for idx, ch_bytes in pairs:
            # ensure ch_bytes is bytes
            if isinstance(ch_bytes, str):
                # Should not happen if loaded correctly via file_manager, but for safety
                # If it was a string representation of hex, we might need conversion?
                # For now assume tuple comes with bytes or we handle it in file manager
                pass
            
            if idx == 0:
                word = ch_bytes
            else:
                if idx not in dictionary:
                    raise ValueError(f"Diccionario incompatible: index {idx} not found")
                word = dictionary[idx] + ch_bytes
            
            result.append(word)
            dictionary[dict_index] = word
            dict_index += 1
            
        return b"".join(result), dictionary
