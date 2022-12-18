import bcrypt


def hash_password(password: str) -> str:
    result = (bcrypt.hashpw(password.encode(), bcrypt.gensalt())).decode()
    return result


def check_password(password: str, hashed_password: str) -> bool:
    result = bcrypt.checkpw(password.encode(), hashed_password.encode())
    return result
