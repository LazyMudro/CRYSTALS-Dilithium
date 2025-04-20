import hashlib
import random
import json

# Параметры
q = 2**23 - 2**13 + 1
gamma1 = 2**17
gamma2 = gamma1 // 2
beta = 1
eta = 2
k = 3
l = 3

def generate_matrix(rows, cols):
    # Генерация матрицы A
    return [[random.randint(0, q-1) for _ in range(cols)] for _ in range(rows)]

def sample_S(eta, size):
    # Генерация секретных векторов s1 и s2
    return [random.randint(-eta, eta) for _ in range(size)]

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

def low_bits(x, gamma):
    # Вычисление младших битов
    return x % (2 * gamma)

def hash_message(message, w1):
    # Хеширование сообщения и w1
    data = message + str(w1).encode()
    return int(hashlib.sha3_256(data).hexdigest(), 16) % 60

def keygen():
    # Генерация ключей
    A = generate_matrix(k, l)
    s1 = sample_S(eta, l)
    s2 = sample_S(eta, k)
    t = vector_add(vector_mul_matrix(s1, A), s2)
    return (A, t), (A, t, s1, s2)

def sign(sk, message):
    # Создание подписи
    A, t, s1, s2 = sk
    z = None
    while z is None:
        y = [random.randint(-gamma1+1, gamma1-1) for _ in range(l)]
        Ay = vector_mul_matrix(y, A)
        w1 = [high_bits(num, gamma2) for num in Ay]
        c = hash_message(message, w1)
        z = vector_add(y, [c * s for s in s1])
        if all(abs(zi) < gamma1 - beta for zi in z):
            Az_cs2 = vector_add(Ay, [-c * s for s in s2])
            low = [low_bits(num, gamma2) for num in Az_cs2]
            if all(abs(l) < gamma2 - beta for l in low):
                return (z, c)
        z = None
    return (z, c)

def save_keys(pk, sk):
    # Сохранение ключей в файлы
    with open("public_key.json", "w") as f:
        json.dump({"A": pk[0], "t": pk[1]}, f)
    with open("secret_key.json", "w") as f:
        json.dump({"A": sk[0], "t": sk[1], "s1": sk[2], "s2": sk[3]}, f)

def save_signature(signature, message):
    # Сохранение подписи и сообщения
    z, c = signature
    with open("signature.json", "w") as f:
        json.dump({"z": z, "c": c}, f)
    with open("message.bin", "wb") as f:
        f.write(message)

if __name__ == "__main__":
    # Генерация ключей
    pk, sk = keygen()
    save_keys(pk, sk)
    
    # Подпись сообщения
    message = "Сообщение для подписи...".encode('utf-8')
    signature = sign(sk, message)
    save_signature(signature, message)
    print("Данные сохранены в файлы: public_key.json, secret_key.json, signature.json, message.bin")