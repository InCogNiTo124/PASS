from Crypto.Cipher import AES
from Crypto.Hash import MD5
import base64

PAD_CHAR = "!"

keyGenerator = MD5.new()
text = input("Message: ")
text = text + PAD_CHAR * (16 - len(text) % 16)
key = input("Key: ")
keyGenerator.update(key.encode("UTF-8"))

cipher = AES.new(keyGenerator.hexdigest().encode("UTF-8"))
encrypted = cipher.encrypt(text.encode("UTF-8"))
eString = base64.b64encode(encrypted).decode("UTF-8")
print("Encrypted: ", eString)

deString = base64.b64decode(eString.encode("UTF-8"))
original = cipher.decrypt(deString).decode("UTF-8").strip(PAD_CHAR)
print("Decrypted: ", original)
