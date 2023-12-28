import random

a = '123456789qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'
ls = list(a)
random.shuffle(ls)
psw = ''.join([random.choice(ls) for x in range(5)])
print (psw)
