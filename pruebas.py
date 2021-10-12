from myMath import *
from RTLib import Raytracer, color
from objLoader import EnvMap, Texture
from figures import *
from random import *

width = 1920
height = 1080

#materials
brownGlass = Material(diffuse = V3(0.68, 0.64, 0.57), spec = 64, ior = 1.33, matType = reflective)
mintGlass = Material(diffuse = V3(0.63, 0.86, 0.667), spec = 64, ior = 1.33, matType = reflective)
skyGlass = Material(diffuse = V3(0.55, 0.96, 1), spec = 64, ior = 1.33, matType = reflective)
bloodGlass = Material(diffuse = V3(1, 0.34, 0.34), spec = 64, ior = 1.33, matType = reflective)
glass = Material(spec = 64, ior = 1.5, matType = reflective)
leather = Material(texture = Texture('src/Textures/leather.jpg'), spec=1, matType=opaque)
#funcion para generar un nuevo material de un solo color
def newColorMat():
    r = random()
    g = random()
    b = random()
    return Material(diffuse = V3(r, g, b), spec=1, matType=opaque)

#Calls
tracer = Raytracer(width,height)
tracer.envmap = EnvMap('src/maps/snowy_hillside_2k.bmp')

#Illumination
tracer.ambLight = AmbientLight(strength = 0.1)
tracer.dirLight = DirectionalLight(direction = V3(1, -1, -2), intensity = 0.5)
tracer.pointLights.append(PointLight(position = V3(0, 2, 0), intensity = 0.5))

#EsferasGrandes
    #Reflectivas
tracer.scene.append(Sphere(V3(0.5, 0.3, -3), 0.7, brownGlass))
tracer.scene.append(Sphere(V3(-0.2, 0.7, -4), 0.7, glass))
    #Opacas
tracer.scene.append(Sphere(V3(-0.9, 1.1, -5), 0.7, leather))

#esferas pequenas
    #Reflectivas
tracer.scene.append(Sphere(V3(-2, -0.2, -4.5), 0.1, brownGlass))
tracer.scene.append(Sphere(V3(-1, -0.6, -2.6), 0.1, mintGlass))
tracer.scene.append(Sphere(V3(1.5, -0.3, -3.5), 0.1, bloodGlass))
tracer.scene.append(Sphere(V3(0.3, -0.5, -2), 0.1, skyGlass))

    #Opacas
tracer.scene.append(Sphere(V3(0, -0.6, -1.5), 0.1, newColorMat()))
tracer.scene.append(Sphere(V3(-0.2, -0.5, -2.5), 0.1, newColorMat()))
tracer.scene.append(Sphere(V3(0.2, -0.3, -2.5), 0.1, newColorMat()))
tracer.scene.append(Sphere(V3(1, 0, -0.5), 0.1, newColorMat()))
tracer.scene.append(Sphere(V3(2, -0.3, -3.5), 0.1, newColorMat()))
tracer.scene.append(Sphere(V3(1.4, -0.35, -2.4), 0.1, newColorMat()))
tracer.scene.append(Sphere(V3(0, -0.6, -1.5), 0.1, newColorMat()))
tracer.scene.append(Sphere(V3(-1.2, -0.6, -1.5), 0.1, newColorMat()))

# Finalizar
tracer.glRender()
tracer.glFinish('result.bmp')