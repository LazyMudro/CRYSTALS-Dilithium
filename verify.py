import json
import hashlib

# Параметры (должны совпадать)
q = 2**23 - 2**13 + 1
gamma1 = 2**17
gamma2 = gamma1 // 2
beta = 1
k = 3
l = 3

def vector_add(a, b, mod=q):
    # Сложение векторов по модулю
    return [(x + y) % mod for x, y in zip(a, b)]

def vector_mul_matrix(v, M, mod=q):
    # Умножение вектора на матрицу
    result = [0] * len(M)
    for i, row in enumerate(M):
        result[i] = sum(x * y for x, y in zip(v, row)) % mod
    return result

def high_bits(x, gamma):
    # Вычисление старших битов
    return (x + gamma) // (2 * gamma)

def hash_message(message, w1):
    # Хеширование сообщения и w1
    data = message + str(w1).encode()
    return int(hashlib.sha3_256(data).hexdigest(), 16) % 60

def verify(pk, message, signature):
    # Проверка подписи
    A, t = pk
    z, c = signature
    Az = vector_mul_matrix(z, A)
    ct = [c * ti % q for ti in t]
    w_prime = vector_add(Az, [-ct_i for ct_i in ct])
    w1_prime = [high_bits(num, gamma2) for num in w_prime]
    c_prime = hash_message(message, w1_prime)
    norm_ok = all(abs(zi) < gamma1 - beta for zi in z)
    return norm_ok and (c == c_prime)

def load_public_key():
    # Загрузка публичного ключа
    with open("public_key.json", "r") as f:
        data = json.load(f)
    return (data["A"], data["t"])

def load_signature():
    # Загрузка подписи и сообщения
    with open("signature.json", "r") as f:
        sig = json.load(f)
    with open("message.bin", "rb") as f:
        message = f.read()
    return (sig["z"], sig["c"]), message

if __name__ == "__main__":
    pk = load_public_key()
    (z, c), message = load_signature()
    is_valid = verify(pk, message, (z, c))
    print("Подпись действительна:", is_valid)