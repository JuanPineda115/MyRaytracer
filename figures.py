from math import pi
from myMath import *
from RTLib import white

opaque = 0
reflective = 1
transparent = 2
OPAQUE_REFLECTIVE = 3

class Material(object):
    def __init__(self, diffuse = white, spec = 1, ior = 1, reflex = 0.85, texture = None, matType = opaque):
        self.diffuse = diffuse
        self.spec = spec
        self.ior = ior
        self.texture = texture
        self.matType = matType
        self.reflex = reflex

class Intersect(object):
    def __init__(self, distance, point, normal, texCoords, sceneObject):
        self.distance = distance
        self.point = point
        self.normal = normal
        self.texCoords = texCoords
        self.sceneObject = sceneObject

class DirectionalLight(object):
    def __init__(self, direction = V3(0,-1,0), intensity = 1, color = white ):
        self.direction = norm(direction)
        self.intensity = intensity
        self.color = color

class AmbientLight(object):
    def __init__(self, strength = 0, color = white):
        self.strength = strength
        self.color = color

    def getColor(self):
        return V3(self.strength * self.color[0],
                  self.strength * self.color[1],
                  self.strength * self.color[2])

class PointLight(object):
    # Luz con punto de origen que va en todas direcciones
    def __init__(self, position = V3(0,0,0), intensity = 1, color = white):
        self.position = position
        self.intensity = intensity
        self.color = color

class Sphere(object):
    def __init__(self, center, radius, material = Material()):
        self.center = center
        self.radius = radius
        self.material = material

    def ray_intersect(self, orig, dir):

        # P = O + t * D

        L = subt(self.center, orig)
        l = mag(L)

        tca = dotProd(L, dir)

        d = sqrt(l * l - tca * tca)

        if d > self.radius:
            return None

        thc = pow((pow(self.radius,2) - pow(d,2)), 0.5)
        t0 = tca - thc
        t1 = tca + thc

        if t0 < 0:
            t0 = t1

        if t0 < 0:
            return None

        hit = add(orig, vecScalarProd(t0, dir))
        normal = subt(hit, self.center)
        normal = norm(normal)

        u = 1 - ((arctangent( normal[2], normal[0]) / (2 * pi)) + 0.5)
        v = arcos(-normal[1]) / pi

        uvs = V2(u,v)

        return Intersect(distance = t0 ,
                         point = hit,
                         normal = normal,
                         texCoords = uvs,
                         sceneObject = self)

class Plane(object):
    def __init__(self, position, normal, material = Material()):
        self.position = position
        self.normal = norm(normal)
        self.material = material

    def ray_intersect(self, orig, dir):
        #t = (( planePos - origRayo) dot planeNormal) / (dirRayo dot planeNormal)
        denom = dotProd(dir, self.normal)

        if abs(denom) > 0.0001:
            num = dotProd(subt(self.position, orig), self.normal)
            t = num / denom
            if t > 0:
                # P = O + t * D
                hit = add(orig, vecScalarProd(t, dir))

                return Intersect(distance = t,
                                 point = hit,
                                 normal = self.normal,
                                 texCoords = None,
                                 sceneObject = self)

        return None

class AABB(object):
    # Axis Aligned Bounding Box
    def __init__(self, position, size, material = Material()):
        self.position = position
        self.size = size
        self.material = material
        self.planes = []

        self.boundsMin = [0,0,0]
        self.boundsMax = [0,0,0]

        halfSizeX = size[0] / 2
        halfSizeY = size[1] / 2
        halfSizeZ = size[2] / 2

        #Sides
        self.planes.append(Plane( add(position, V3(halfSizeX,0,0)), V3(1,0,0), material))
        self.planes.append(Plane( add(position, V3(-halfSizeX,0,0)), V3(-1,0,0), material))

        # Up and down
        self.planes.append(Plane( add(position, V3(0,halfSizeY,0)), V3(0,1,0), material))
        self.planes.append(Plane( add(position, V3(0,-halfSizeY,0)), V3(0,-1,0), material))

        # Front and Back
        self.planes.append(Plane( add(position, V3(0,0,halfSizeZ)), V3(0,0,1), material))
        self.planes.append(Plane( add(position, V3(0,0,-halfSizeZ)), V3(0,0,-1), material))

        #Bounds
        epsilon = 0.001
        for i in range(3):
            self.boundsMin[i] = self.position[i] - (epsilon + self.size[i]/2)
            self.boundsMax[i] = self.position[i] + (epsilon + self.size[i]/2)


    def ray_intersect(self, orig, dir):
        intersect = None
        t = float('inf')

        uvs = None

        for plane in self.planes:
            planeInter = plane.ray_intersect(orig, dir)
            if planeInter is not None:
                # Si estoy dentro de los bounds
                if planeInter.point[0] >= self.boundsMin[0] and planeInter.point[0] <= self.boundsMax[0]:
                    if planeInter.point[1] >= self.boundsMin[1] and planeInter.point[1] <= self.boundsMax[1]:
                        if planeInter.point[2] >= self.boundsMin[2] and planeInter.point[2] <= self.boundsMax[2]:
                            #Si soy el plano mas cercano
                            if planeInter.distance < t:
                                t = planeInter.distance
                                intersect = planeInter

                                if abs(plane.normal[0]) > 0:
                                    u = (planeInter.point[1] - self.boundsMin[1]) / (self.boundsMax[1] - self.boundsMin[1])
                                    v = (planeInter.point[2] - self.boundsMin[2]) / (self.boundsMax[2] - self.boundsMin[2])
                                elif abs(plane.normal[1]) > 0:
                                    u = (planeInter.point[0] - self.boundsMin[0]) / (self.boundsMax[0] - self.boundsMin[0])
                                    v = (planeInter.point[2] - self.boundsMin[2]) / (self.boundsMax[2] - self.boundsMin[2])
                                elif abs(plane.normal[2]) > 0:
                                    u = (planeInter.point[0] - self.boundsMin[0]) / (self.boundsMax[0] - self.boundsMin[0])
                                    v = (planeInter.point[1] - self.boundsMin[1]) / (self.boundsMax[1] - self.boundsMin[1])
                                
                                uvs = V2(u, v)

        if intersect is None:
            return None

        return Intersect(distance = intersect.distance,
                         point = intersect.point,
                         normal = intersect.normal,
                         texCoords = uvs,
                         sceneObject = self)