import charade
import codecs
def detect(s):
     
    try:
        # check it in the charade list
        if isinstance(s, str):
            return charade.detect(s.encode())
        # detecting the string
        else:
            return charade.detect(s)
     
    # in case of error
    # encode with 'utf -8' encoding
    except UnicodeDecodeError:
        return charade.detect(s.encode('utf-8'))

obj = b'v20\x16 \xa0\xf7\xcez\xa30}\xdb\xcfw\x8b\xef\xb7t\xe0+%\x18\xbc\x86\xb9\xde+2X\x0b/\xfe\xac\x8fa\xe3\x07\xa1\xe3\xe3\xb5\x19\xf6\xd3\x97U\xcc&`lu\xbd\xd0O\xe8e\xfd\xc6\xc40\xe6\xe8\xec\xf1\r\x1f!\xb8\xdb\x97\x9f\xb1\x0c\x1e,\xd2\xe7#\xbe-\xbd\xda\xb7,\x04\x1d\x9b\xf8\xc7\xec\xc5\x90\xc9:rYqW'

print(detect(obj))
codecs.__all__
for s in codecs.__all__:
    if 'decode' in s:
        print(codecs.decode())