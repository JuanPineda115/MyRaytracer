# Universidad del Valle de Guatemala
# Graficas por Computadora
# Juan Pablo Pineda 19087
# Basado en el codigo del catedratico Carlos Alonso
# Modulo para cargar archivos OBJ
from math import pi
import struct
from PIL import Image
from myMath import V3, arcos, arctangent, norm

def color(r, g, b):
    return bytes([int(b * 255), int(g * 255), int(r * 255)])

class Obj(object):
    def __init__(self, filename):
        with open(filename, "r") as file:
            self.lines = file.read().splitlines()
        self.vertices = []
        self.texcoords = []
        self.normals = []
        self.faces = []
        self.readFile()

    def readFile(self):
        for line in self.lines:
            if line and line[0] != '#':
                prefix, value = line.split(' ', 1)
                if prefix == 'v':  # Vertex
                    self.vertices.append(list(map(float, value.split(' '))))
                elif prefix == 'vt':  # Texture Coords
                    self.texcoords.append(list(map(float, value.split(' '))))
                elif prefix == 'vn':  # Normal
                    self.normals.append(list(map(float, value.split(' '))))
                elif prefix == 'f':  # Faces
                    self.faces.append([list(map(int, vert.split('/')))
                                       for vert in value.split(' ') if vert != ''])


class Texture(object):
    def __init__(self, filename):
        self.filename = filename
        self.read()

    def read(self):
        if self.filename.find(".bmp") > 0:
            with open(self.filename, "rb") as image:
                image.seek(10)
                headerSize = struct.unpack('=l', image.read(4))[0]

                image.seek(14 + 4)
                self.width = struct.unpack('=l', image.read(4))[0]
                self.height = struct.unpack('=l', image.read(4))[0]

                image.seek(headerSize)

                self.pixels = []

                for x in range(self.width):
                    self.pixels.append([])
                    for y in range(self.height):
                        b = ord(image.read(1)) / 255
                        g = ord(image.read(1)) / 255
                        r = ord(image.read(1)) / 255

                        self.pixels[x].append(V3(r, g, b))

            image.close()

        else:
            img = Image.open(self.filename)

            self.width = img.width
            self.height = img.height

            self.pixels = []

            for x in range(self.width):
                self.pixels.append([])
                for y in range(self.height):
                    r = img.getpixel((x, y))[0] / 255
                    g = img.getpixel((x, y))[1] / 255
                    b = img.getpixel((x, y))[2] / 255

                    self.pixels[x].append(V3(r, g, b))

            img.close()

    def getColor(self, xcoord, ycoord):
        if 0 <= xcoord < 1 and 0 <= ycoord < 1:
            x = round(xcoord * self.width)
            y = round(ycoord * self.height)
            if y < len(self.pixels):
                if x < len(self.pixels[y]):
                    return self.pixels[y][x]
                else:
                    return V3(0, 0, 0)
            else:
                return V3(0, 0, 0)
            # return self.pixels[y][x]
        else:
            return V3(0, 0, 0)


class EnvMap(object):
    def __init__(self, filename):
        self.filename = filename
        self.read()

    def read(self):
        if self.filename.find(".bmp") > 0:
            with open(self.filename, "rb") as image:
                image.seek(10)
                headerSize = struct.unpack('=l', image.read(4))[0]

                image.seek(14 + 4)
                self.width = struct.unpack('=l', image.read(4))[0]
                self.height = struct.unpack('=l', image.read(4))[0]

                image.seek(headerSize)

                self.pixels = []

                for y in range(self.height):
                    self.pixels.append([])
                    for x in range(self.width):
                        b = ord(image.read(1)) / 255
                        g = ord(image.read(1)) / 255
                        r = ord(image.read(1)) / 255

                        self.pixels[y].append(V3(r, g, b))
        else:
            self.img = Image.open(self.filename)

            self.width = self.img.width
            self.height = self.img.height
            self.imgCoords = self.img.load()

            self.pixels = []

            for x in range(self.img.size[0]):
                print("ENV... ", x)
                self.pixels.append([])
                for y in range(self.img.size[1]):
                    if type(self.imgCoords[x, y]) == int:
                        r = self.imgCoords[x, y] / 255
                        g = self.imgCoords[x, y] / 255
                        b = self.imgCoords[x, y] / 255
                    else:
                        r = self.imgCoords[x, y][0] / 255
                        g = self.imgCoords[x, y][1] / 255
                        b = self.imgCoords[x, y][2] / 255

                    self.pixels[x].append(V3(r, g, b))

    def getColor(self, dir):

        dir = norm(dir)

        x = int(((arctangent(dir[2], dir[0]) / (2 * pi)) - 0.15) * self.width)
        y = int(arcos(-dir[1]) / pi * self.height)

        return self.pixels[y][x]
