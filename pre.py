from charm.toolbox.pairinggroup import PairingGroup
from charm.schemes.pre_mg07 import PreGA

ID = "nikos fotiou"
ID2 = "test user"
msg = "hello world!!!!!"
group = PairingGroup('SS512', secparam=1024)
pre = PreGA(group)
(master_secret_key, params) = pre.setup()
id_secret_key = pre.keyGen(master_secret_key, ID)
id2_secret_key = pre.keyGen(master_secret_key, ID2)
ciphertext = pre.encrypt(params, ID, msg)
# print(pre.decryptFirstLevel(params,id_secret_key, ciphertext, ID))
# b'hello world!!!!!'
re_encryption_key = pre.rkGen(params, id_secret_key, ID, ID2)
ciphertext2 = pre.reEncrypt(params, ID, re_encryption_key, ciphertext)
print(pre.decryptSecondLevel(params, id2_secret_key, ID, ID2, ciphertext2))
b'hello world!!!!!'
