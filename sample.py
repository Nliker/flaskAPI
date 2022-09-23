import jwt
from datetime import datetime, timedelta
import time

print (type(datetime.utcnow()))
print (datetime.utcnow())
#private_key = open('es256-private-key.txt').read()
private_key = "secret_key"
print(private_key)
# token = jwt.encode({"some": "payload"}, private_key, algorithm="ES256")
token = jwt.encode({
  "iss": "issuer",
  "sub": "subject",
  "iat": datetime.utcnow(),
  'exp':datetime.utcnow() + timedelta(days=3),
}, private_key, "HS256")
print(token)


# public_key = """-----BEGIN PUBLIC KEY-----
# MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAETYvVFPg0qhcDkzYGOa5xCrZiZ9uoJUltWjSWlW5tw85vHkqDIA+45fJ8YN5bSVmUE9ahW/IA5DKUyYS87W/JKQ==
# -----END PUBLIC KEY-----"""
public_key = "secret_key"
try:
    decoded = jwt.decode(token, public_key, "HS256")
    print(decoded)
    timestamp=datetime.fromtimestamp(decoded['iat'])
    print(timestamp.strftime('%Y-%m-%d %H:%M:%S'))
    
except jwt.exceptions.ExpiredSignatureError as e:
    print('Excepton:', e)