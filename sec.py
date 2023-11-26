from passlib.context import CryptContext
import hashlib
from random import random
from string import ascii_letters, digits

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)

def create_secret_key() -> str:
    val = "".join([ascii_letters, digits])
    super_val =  "".join([val[int(random() * len(val))] for _ in range(6)])
    return password_context.hash(super_val)

def assinado_rm(secret_key, extracted_number):
    validation_code = hashlib.sha256(
        (str(extracted_number) +
        secret_key).encode()).hexdigest()[:4] 
    return validation_code