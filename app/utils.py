def decrypt(text):
    if text:
        decrypt_text = ""
        text = text.lower()
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        idx = 0
        while idx < len(text):
            block_text = text[idx:idx+3]
            shift = ord(block_text[1]) - ord(block_text[0]) 
            if block_text[1] in alphabet:
                decrypt_text += block_text[1]
                idx += 3
            else:
                decrypt_text += chr(ord(block_text[1]) - shift)
                idx += 3
        return decrypt_text

def encrypt(text, shift):
    encrypted_text = ""
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    text = text.lower()
    for symbol in text:
        if symbol in alphabet:
            temp = ""
            idx = alphabet.index(symbol)
            temp += alphabet[(idx - shift) % 26]  
            temp += symbol                    
            temp += alphabet[(idx + shift) % 26]  
            encrypted_text += temp
        else:
            encrypted_text += symbol * 3
    
    return encrypted_text
