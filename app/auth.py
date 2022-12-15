import bcrypt


def hash_password(password: str) -> str:
    res = (bcrypt.hashpw(password.encode(), bcrypt.gensalt())).decode()
    return res


def check_password(password: str, hashed_password: str):
    res = bcrypt.checkpw(password.encode(), hashed_password.encode())
    print('>>> check_password:')
    print(type(res))
    print(res)
    print('----')
    return res
