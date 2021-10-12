# by Juan Pablo Pineda

from collections import namedtuple
import math as pymath

V2 = namedtuple('Point2', ['x', 'y'])
V3 = namedtuple('Point3', ['x', 'y', 'z'])
V4 = namedtuple('Point4', ['x', 'y', 'z', 'w'])


def sqrt(radicand):
    return pow(radicand, 0.5)


def vecScalarProd(scalar, vector):
    if len(vector) == 2:
        answer = V2(scalar * vector.x, scalar * vector.y)
        return answer
    elif len(vector) == 3:
        answer = V3(scalar * vector.x, scalar * vector.y, scalar * vector.z)
        return answer
    elif len(vector) == 4:
        answer = V4(scalar * vector.x, scalar * vector.y,
                    scalar * vector.z, scalar * vector.w)
        return answer


def norm(v):
    if len(v) == 2:
        magnitude = sqrt(v.x * v.x + v.y * v.y)
        if magnitude != 0:
            unitVec = V2(v.x / magnitude, v.y / magnitude)
        else:
            unitVec = V2(0, 0)
        return unitVec
    elif len(v) == 3:
        magnitude = sqrt(v.x * v.x + v.y * v.y + v.z * v.z)
        if magnitude != 0:
            unitVec = V3(v.x / magnitude, v.y / magnitude, v.z / magnitude)
        else:
            unitVec = V3(0, 0, 0)
        return unitVec
    elif len(v) == 4:
        magnitude = sqrt(v.x * v.x + v.y * v.y + v.z * v.z + v.w * v.w)
        if magnitude != 0:
            unitVec = V4(v.x / magnitude, v.y / magnitude,
                         v.z / magnitude, v.w / magnitude)
        else:
            unitVec = V3(0, 0, 0)
        return unitVec


def crossProd(v1, v2):
    i = ((v1.y * v2.z) - (v1.z * v2.y))
    j = -((v1.x * v2.z) - (v1.z * v2.x))
    k = ((v1.x * v2.y) - (v1.y * v2.x))
    res = V3(i, j, k)
    return res


def add(num1, num2):
    if type(num1) == int and type(num2) == int:
        return num1 + num2
    elif type(num1) == float and type(num2) == float:
        return num1 + num2
    elif len(num1) == 2 and len(num2) == 2:
        return V2(num1.x + num2.x, num1.y + num2.y)
    elif len(num1) == 3 and len(num2) == 3:
        return V3(num1.x + num2.x, num1.y + num2.y, num1.z + num2.z)
    elif len(num1) == 4 and len(num2) == 4:
        return V4(num1.x + num2.x, num1.y + num2.y, num1.z + num2.z, num1.w + num2.w)


def subt(A, B):
    if type(A) == int and type(B) == int:
        return A - B
    elif type(A) == float and type(B) == float:
        return A - B
    elif len(A) == 2 and len(B) == 2:
        return V2(A.x - B.x, A.y - B.y)
    elif len(A) == 3 and len(B) == 3:
        return V3(A.x - B.x, A.y - B.y, A.z - B.z)
    elif len(A) == 4 and len(B) == 4:
        return V4(A.x - B.x, A.y - B.y, A.z - B.z, A.w - B.w)


def toRad(deg):
    return (deg * pymath.pi) / 180


def sen(deg):
    return round(pymath.sin(toRad(deg)), 10)


def arctangent(y, x):
    return pymath.atan2(y, x)


def arcos(deg):
    return pymath.acos(deg)


def cosine(deg):
    return round(pymath.cos(toRad(deg)), 10)


def transpose(m):
    return list(map(list, zip(*m)))


def squareMat(matrix):
    if type(matrix) != list:
        return False
    if len(matrix) <= 0:
        return False
    if len(matrix[0]) <= 0:
        return False
    if len(matrix) != len(matrix[0]):
        return False
    elif len(matrix) == len(matrix[0]):
        return True


def give_identity_mat(num_rows):
    identitymat = [[0 for i in range(num_rows)] for i in range(num_rows)]
    for i in range(0, num_rows):
        identitymat[i][i] = 1
    return identitymat


def det(m):
    if not squareMat(m):
        return
    n = len(m)
    cm = m
    for fd in range(n):
        for i in range(fd+1, n):
            if (cm[fd][fd] == 0):
                cm[fd][fd] == 1.0e-18
            crScaler = cm[i][fd] / cm[fd][fd]
            for j in range(n):
                cm[i][j] = cm[i][j] - crScaler * cm[fd][j]

    product = 1.0
    for i in range(n):
        product *= cm[i][i]
    return product


def vdp(a1, a2):
    res = 0
    for i in range(len(a1)):
        res += round(a1[i] * a2[i], 10)
    return res


def matMul(A, B):
    if type(A) != list or type(B) != list:
        return -1
    if len(A) <= 0 or len(B) <= 0:
        return -1
    if len(A[0]) <= 0 or len(B[0]) <= 0:
        return -1
    rowA = len(A)
    colA = len(A[0])
    rowB = len(B)
    colB = len(B[0])
    if colA != rowB:
        return -1

    result = []
    Btrans = transpose(B)

    for row in range(rowA):
        result.append([])
        for col in range(colB):
            result[row].append((vdp(A[row], Btrans[col])))
    return result


def inv(M):
    n = len(M)
    m = M
    for i in range(n):
        for j in range(n):
            if i == j:
                m[i].append(1)
            else:
                m[i].append(0)
    for i in range(n):
        if m[i][i] == 0.0:
            return
        for j in range(n):
            if i != j:
                ratio = m[j][i]/m[i][i]

                for k in range(2*n):
                    m[j][k] = m[j][k] - ratio * m[i][k]
    for i in range(n):
        div = m[i][i]
        for j in range(2*n):
            m[i][j] = m[i][j]/div
    resultado = [[] for _ in range(n)]
    for i in range(n):
        for j in range(n, 2*n):
            resultado[i].append(m[i][j])

    return resultado


def matScalarProd(s, m):
    if len(m) <= 0:
        return -1
    if len(m[0]) <= 0:
        return -1
    result = []
    for row in range(len(m)):
        result.append([])
        for col in range(len(m)):
            result[row].append(round(s * m[row][col], 10))

    return result


def tangent(deg):
    try:
        res = sen(deg) / cosine(deg)
        return res
    except ZeroDivisionError:
        print('cosine is 0')


def mag(vec):
    if len(vec) == 2:
        return sqrt(vec.x * vec.x + vec.y * vec.y)
    elif len(vec) == 3:
        return sqrt(vec.x * vec.x + vec.y * vec.y + vec.z * vec.z)
    elif len(vec) == 4:
        return sqrt(vec.x * vec.x + vec.y * vec.y + vec.z * vec.z + vec.w * vec.w)


def dotProd(v1, v2):
    return v1.x * v2.x + v1.y * v2.y + v1.z * v2.z
