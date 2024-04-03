import random
from Crypto.Hash import SHA3_256
from ecpy.curves import Curve, Point


def egcd(a, b):
    x, y, u, v = 0, 1, 1, 0
    while a != 0:
        q, r = b//a, b % a
        m, n = x-u*q, y-v*q
        b, a, x, y, u, v = a, r, u, v, m, n
    gcd = b
    return gcd, x, y


def modinv(a, m):
    if a < 0:
        a = a+m
    gcd, x, y = egcd(a, m)
    if gcd != 1:
        return None  # modular inverse does not exist
    else:
        return x % m


def KeyGen(E):
    n = E.order
    P = E.generator
    sA = random.randint(1, n-1)
    QA = P*sA
    return sA, QA


# message, E and secret key are taken as a parameter.
def SignGen(message, E, sA):
    h_obj = SHA3_256.new()
    h_obj.update(message)
    h2 = h_obj.hexdigest()
    n = E.order
    h = int(h2, 16) % n
    k = random.randint(2, n - 1)
    P = E.generator
    R = k * P
    r = R.x % n

    s = (sA * r - k * h) % n
    return s, r


def SignVer(message, s, r, E, QA):
    h_obj = SHA3_256.new()
    h_obj.update(message)
    h2 = h_obj.hexdigest()
    n = E.order
    h = int(h2, 16) % n

    P = E.generator

    v = modinv(h, n)
    z1 = (s * v) % n
    z2 = (r * v) % n

    z1 = n - z1

    V = z1 * P + z2 * QA
    if V.x % n == r:
        return 0
    else:
        return 1
