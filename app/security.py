from passlib.context import CryptContext

bcrypt_context = CryptContext(schemes = ['argon2'], deprecated = 'auto')

def verify_pwd(plain_pwd : str, hashed_pwd : str):
    try:
        return bcrypt_context.verify(plain_pwd, hashed_pwd)
    except ValueError:
        return False

def get_pwd_hash(pwd : str):
    return bcrypt_context.hash(pwd)