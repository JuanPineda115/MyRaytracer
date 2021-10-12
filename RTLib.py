from math import pi
import struct
from collections import namedtuple
from objLoader import color
from myMath import *
import random

step = 2
opaque = 0
reflective = 1
transparent = 2
OPAQUE_REFLECTIVE = 3
MAX_RECURSION_DEPTH = 3


def char(c):
    return struct.pack('=c', c.encode('ascii'))


def word(w):
    return struct.pack('=h', w)


def dword(d):
    return struct.pack('=l', d)


def color(r, g, b):
    return bytes([int(b * 255), int(g * 255), int(r * 255)])


def baryCoords(A, B, C, P):
    try:
        u = (((B.y - C.y) * (P.x - C.x) + (C.x - B.x) * (P.y - C.y)) /
             ((B.y - C.y) * (A.x - C.x) + (C.x - B.x) * (A.y - C.y)))
        v = (((C.y - A.y) * (P.x - C.x) + (A.x - C.x) * (P.y - C.y)) /
             ((B.y - C.y) * (A.x - C.x) + (C.x - B.x) * (A.y - C.y)))

        w = 1 - u - v
    except:
        return -1, -1, -1

    return u, v, w


def reflectVector(normal, dirVector):
    reflect = 2 * dotProd(normal, dirVector)
    reflect = vecScalarProd(reflect, normal)
    reflect = subt(reflect, dirVector)
    reflect = norm(reflect)
    return reflect


def refractVector(normal, dirVector, ior):
    cosi = max(-1, min(1, dotProd(dirVector, normal)))
    etai = 1
    etat = ior
    if cosi < 0:
        cosi = -cosi
    else:
        etai, etat = etat, etai
        normal = vecScalarProd(-1, normal)
    eta = etai/etat
    k = 1 - eta * eta * (1 - (cosi * cosi))
    if k < 0:
        return None
    R = add(vecScalarProd(eta, dirVector),
            vecScalarProd((eta * cosi - k**0.5), normal))
    return norm(R)


def fresnel(normal, dirVector, ior):
    cosi = max(-1, min(1, dotProd(dirVector, normal)))
    etai = 1
    etat = ior
    if cosi > 0:
        etai, etat = etat, etai
    sint = etai / etat * (max(0, 1 - cosi * cosi) ** 0.5)
    if sint >= 1:
        return 1
    cost = max(0, 1 - sint * sint) ** 0.5
    cosi = abs(cosi)
    Rs = ((etat * cosi) - (etai * cost)) / ((etat * cosi) + (etai * cost))
    Rp = ((etai * cosi) - (etat * cost)) / ((etai * cosi) + (etat * cost))
    return (Rs * Rs + Rp * Rp) / 2


BLACK = V3(0, 0, 0)
white = V3(1, 1, 1)


class Raytracer(object):
    def __init__(self, width, height):
        self.curr_color = white
        self.clear_color = BLACK
        self.glCreateWindow(width, height)
        self.camPosition = V3(0, 0, 0)
        self.fov = 60
        self.background = None
        self.scene = []
        self.pointLights = []
        self.ambLight = None
        self.dirLight = None
        self.envmap = None

    def glFinish(self, filename):
        with open(filename, "wb") as file:
            file.write(bytes('B'.encode('ascii')))
            file.write(bytes('M'.encode('ascii')))
            file.write(dword(14 + 40 + (self.width * self.height * 3)))
            file.write(dword(0))
            file.write(dword(14 + 40))
            file.write(dword(40))
            file.write(dword(self.width))
            file.write(dword(self.height))
            file.write(word(1))
            file.write(word(24))
            file.write(dword(0))
            file.write(dword(self.width * self.height * 3))
            file.write(dword(0))
            file.write(dword(0))
            file.write(dword(0))
            file.write(dword(0))
            for y in range(self.height):
                for x in range(self.width):
                    file.write(color(self.pixels[x][y][0],
                                     self.pixels[x][y][1],
                                     self.pixels[x][y][2]))

    def glCreateWindow(self, width, height):
        self.width = width
        self.height = height
        self.glClear()
        self.glViewport(0, 0, width, height)

    def glViewport(self, x, y, width, height):
        self.vpX = int(x)
        self.vpY = int(y)
        self.vpWidth = int(width)
        self.vpHeight = int(height)

    def glClearColor(self, r, g, b):
        self.clear_color = V3(r, g, b)

    def glClear(self):
        self.pixels = [[self.clear_color for y in range(self.height)]
                       for x in range(self.width)]

    def glClearBackground(self):
        if self.background:
            for x in range(self.vpX, self.vpX + self.vpWidth):
                for y in range(self.vpY, self.vpY + self.vpHeight):
                    tx = (x - self.vpX) / self.vpWidth
                    ty = (y - self.vpY) / self.vpHeight
                    self.glPoint(x, y, self.background.getColor(tx, ty))

    def glViewportClear(self, color=None):
        for x in range(self.vpX, self.vpX + self.vpWidth):
            for y in range(self.vpY, self.vpY + self.vpHeight):
                self.glPoint(x, y, color)

    def glColor(self, r, g, b):
        self.curr_color = V3(r, g, b)

    def glPoint(self, x, y, color=None):
        if x < self.vpX or x >= self.vpX + self.vpWidth or y < self.vpY or y >= self.vpY + self.vpHeight:
            return

        if (0 <= x < self.width) and (0 <= y < self.height):
            self.pixels[int(x)][int(y)] = color or self.curr_color

    def glRender(self):
        for y in range(0, self.height, step):
            print(round(y/self.height * 100, 2)," %")
            for x in range(0, self.width, step):
                Px = 2 * ((x + 0.5) / self.width) - 1
                Py = 2 * ((y + 0.5) / self.height) - 1
                t = tangent(self.fov / 2)
                r = t * self.width / self.height
                Px *= r
                Py *= t
                direction = V3(Px, Py, -1)
                direction = norm(direction)
                self.glPoint(x, y, self.cast_ray(self.camPosition, direction))

    def cast_ray(self, orig, dir, origObj=None, recursion=0):
        intersect = self.scene_intersect(orig, dir, origObj)
        if intersect == None or recursion >= MAX_RECURSION_DEPTH:
            if self.envmap:
                return self.envmap.getColor(dir)
            return self.clear_color
        material = intersect.sceneObject.material
        finalColor = V3(0, 0, 0)
        objectColor = V3(material.diffuse[0],
                         material.diffuse[1],
                         material.diffuse[2])
        ambientColor = V3(0, 0, 0)
        dirLightColor = V3(0, 0, 0)
        pLightColor = V3(0, 0, 0)
        finalSpecColor = V3(0, 0, 0)
        refractColor = V3(0, 0, 0)
        view_dir = subt(self.camPosition, intersect.point)
        view_dir = norm(view_dir)
        if self.ambLight:
            ambientColor = V3(self.ambLight.getColor()[0], self.ambLight.getColor()[
                              1], self.ambLight.getColor()[2])
        if self.dirLight:
            shadow_intensity = 0
            light_dir = vecScalarProd(-1, self.dirLight.direction)
            intensity = max(0, dotProd(intersect.normal, light_dir)
                            ) * self.dirLight.intensity
            diffuseColor = V3(intensity * self.dirLight.color[0],
                              intensity * self.dirLight.color[1],
                              intensity * self.dirLight.color[2])
            reflect = reflectVector(intersect.normal, light_dir)
            spec_intensity = pow(
                self.dirLight.intensity * max(0, dotProd(view_dir, reflect)), material.spec)
            specColor = V3(spec_intensity * self.dirLight.color[0],
                           spec_intensity * self.dirLight.color[1],
                           spec_intensity * self.dirLight.color[2])
            shadInter = self.scene_intersect(
                intersect.point, light_dir, intersect.sceneObject)
            if shadInter:
                shadow_intensity = 1
            dirLightColor = vecScalarProd((1 - shadow_intensity), diffuseColor)
            finalSpecColor = add(finalSpecColor, vecScalarProd(
                (1 - shadow_intensity), specColor))
        for pointLight in self.pointLights:
            shadow_intensity = 0
            light_dir = subt(pointLight.position, intersect.point)
            light_dir = norm(light_dir)
            intensity = max(0, dotProd(intersect.normal,
                                       light_dir)) * pointLight.intensity
            diffuseColor = V3(intensity * pointLight.color[0],
                              intensity * pointLight.color[1],
                              intensity * pointLight.color[2])
            reflect = reflectVector(intersect.normal, light_dir)
            spec_intensity = pointLight.intensity * \
                pow(max(0, dotProd(view_dir, reflect)), material.spec)
            specColor = V3(spec_intensity * pointLight.color[0],
                           spec_intensity * pointLight.color[1],
                           spec_intensity * pointLight.color[2])
            shadInter = self.scene_intersect(
                intersect.point, light_dir, intersect.sceneObject)
            lightDistance = mag(subt(
                pointLight.position, intersect.point))
            if shadInter and shadInter.distance < lightDistance:
                shadow_intensity = 1
            pLightColor = add(pLightColor, vecScalarProd(
                (1 - shadow_intensity), diffuseColor))
            finalSpecColor = add(finalSpecColor, vecScalarProd(
                (1 - shadow_intensity), specColor))
        if material.matType == opaque:
            finalColor = add(add(pLightColor, ambientColor),
                             add(dirLightColor, finalSpecColor))
            if material.texture and intersect.texCoords:
                texColor = material.texture.getColor(
                    intersect.texCoords.x, intersect.texCoords.y)
                finalColor = V3(finalColor[0] * texColor[0],
                                finalColor[1] * texColor[1],
                                finalColor[2] * texColor[2])
        elif material.matType == OPAQUE_REFLECTIVE:
            k = material.reflex
            finalColor = add(add(pLightColor, ambientColor),
                             add(dirLightColor, finalSpecColor))
            if material.texture and intersect.texCoords:
                texColor = material.texture.getColor(
                    intersect.texCoords.x, intersect.texCoords.y)
                finalColor = V3(finalColor[0] * texColor[0],
                                finalColor[1] * texColor[1],
                                finalColor[2] * texColor[2])
            reflect = reflectVector(intersect.normal, vecScalarProd(-1, dir))
            reflectColor = self.cast_ray(
                intersect.point, reflect, intersect.sceneObject, recursion + 1)
            reflectColor = V3(reflectColor[0],
                              reflectColor[1],
                              reflectColor[2])
            finalColor = add(vecScalarProd(k, finalColor),
                             vecScalarProd((1-k), reflectColor))
        elif material.matType == reflective:
            reflect = reflectVector(intersect.normal, vecScalarProd(-1, dir))
            reflectColor = self.cast_ray(
                intersect.point, reflect, intersect.sceneObject, recursion + 1)
            reflectColor = V3(reflectColor[0],
                              reflectColor[1],
                              reflectColor[2])
            finalColor = reflectColor + finalSpecColor
        elif material.matType == transparent:
            outside = dotProd(dir, intersect.normal) < 0
            bias = vecScalarProd(0.001, intersect.normal)
            kr = fresnel(intersect.normal, dir, material.ior)
            reflect = reflectVector(intersect.normal, vecScalarProd(-1, dir))
            reflectOrig = add(intersect.point, bias) if outside else subt(
                intersect.point, bias)
            reflectColor = self.cast_ray(
                reflectOrig, reflect, None, recursion + 1)
            if kr < 1:
                refract = refractVector(intersect.normal, dir, material.ior)
                refractOrig = subt(intersect.point, bias) if outside else add(
                    intersect.point, bias)
                refractColor = self.cast_ray(
                    refractOrig, refract, None, recursion + 1)
            finalColor = add(add(vecScalarProd(kr, reflectColor), vecScalarProd(
                (1-kr), refractColor)), finalSpecColor)
        finalColor = V3(finalColor[0] * objectColor[0],
                        finalColor[1] * objectColor[1],
                        finalColor[2] * objectColor[2])
        r = min(1, finalColor[0])
        g = min(1, finalColor[1])
        b = min(1, finalColor[2])
        return V3(r, g, b)

    def scene_intersect(self, orig, dir, origObj=None):
        depth = float('inf')
        intersect = None
        for obj in self.scene:
            if obj is not origObj:
                hit = obj.ray_intersect(orig, dir)
                if hit != None:
                    if hit.distance < depth:
                        depth = hit.distance
                        intersect = hit
        return intersect
