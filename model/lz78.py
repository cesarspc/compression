class LZ78Codec:
    def compress(self, data: bytes):
        if not data:
            raise ValueError("Archivo vacio")
        # Asegurar que la entrada sea en bytes
        if isinstance(data, str):
            data = data.encode('utf-8')
            
        dictionary = {}
        current = b""
        result = []
        dict_index = 1
        
        # Iterar sobre bytes (enteros 0-255)
        for byte_val in data:
            # Crear un objeto bytes de un solo byte
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
            result.append((index, b"")) 
            
        return result, dictionary

    def decompress(self, pairs):
        dictionary = {}
        result = []
        dict_index = 1
        
        for idx, ch_bytes in pairs:
            # asegurar que ch_bytes sea bytes
            if isinstance(ch_bytes, str):
                pass
            
            if idx == 0:
                word = ch_bytes
            else:
                if idx not in dictionary:
                    raise ValueError(f"Diccionario incompatible: indice {idx} no encontrado")
                word = dictionary[idx] + ch_bytes
            
            result.append(word)
            dictionary[dict_index] = word
            dict_index += 1
            
        return b"".join(result), dictionary
