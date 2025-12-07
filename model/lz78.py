# model/lz78.py
class LZ78Codec:
    def compress(self, text: str):
        if not text:
            raise ValueError("Archivo vacío")
        dictionary = {}
        current = ""
        result = []
        dict_index = 1
        for c in text:
            temp = current + c
            if temp in dictionary:
                current = temp
            else:
                index = dictionary.get(current, 0)
                result.append((index, c))
                dictionary[temp] = dict_index
                dict_index += 1
                current = ""
        if current:
            index = dictionary.get(current, 0)
            result.append((index, ""))  # último par
        return result, dictionary

    def decompress(self, pairs):
        dictionary = {}
        result = []
        dict_index = 1
        for idx, ch in pairs:
            if idx == 0:
                word = ch
            else:
                if idx not in dictionary:
                    raise ValueError("Diccionario incompatible")
                word = dictionary[idx] + ch
            result.append(word)
            dictionary[dict_index] = word
            dict_index += 1
        return "".join(result), dictionary
