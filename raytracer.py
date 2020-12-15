import math
import sys
from PIL import Image
eye = (0,0,0)
forward = (0,0,-1)
right = (1,0,0)
up = (0,1,0)
colorLen = 3
def magnSquared(v, l=3):
	return sum([v[i]**2 for i in range(l)])
def vecSub(v1, v2, l=3): #v1 - v2
	return tuple([v1[i] - v2[i] for i in range(l)])
def vecAdd(v1, v2, l=3):
	return tuple([v1[i] + v2[i] for i in range(l)])
def dotProd(v1, v2, l=3):
	return sum([v1[i] * v2[i] for i in range(l)])
def scalarMult(s, v, l=3):
	return tuple([s*v[i] for i in range(l)])
def vecMulti(v1, v2, l=3):
	return tuple([v1[i] * v2[i] for i in range(l)])
def normalize(v, l=3):
	return scalarMult(1/magnSquared(v,l)**(1/2), v, l)
def cross(a, b):
    return (a[1]*b[2] - a[2]*b[1],
         a[2]*b[0] - a[0]*b[2],
         a[0]*b[1] - a[1]*b[0])

def sphereIntersection(s, rd, eye):
	r = s[3]
	inside = magnSquared(vecSub(s, eye)) < r**2
	tc = dotProd(vecSub(s, eye), rd)/magnSquared(rd)**(1/2)
	if not inside and tc < 0:
		return 'NULL'
	d2 = magnSquared(vecAdd(eye, vecSub(scalarMult(tc, rd), s)))
	if not inside and d2 > r**2:
		return 'NULL'
	toffset = (r**2 - d2)**(1/2)/magnSquared(rd)**(1/2)
	if inside:
		return tc + toffset
	else:
		return tc - toffset

def render(spheres, img):
	for x in range(img.width):
		for y in range(img.height):
			sx = (2*x - img.width)/max(img.width, img.height)
			sy = (img.height - 2*y)/max(img.width, img.height)
			rd = vecAdd(forward, vecAdd(scalarMult(sx, right), scalarMult(sy, up)))
			rd = normalize(rd)
			mindist = -1
			objInd = -1
			for ind, s in enumerate(spheres): #checking intersection
				tmp = sphereIntersection(s, rd, eye)
				if tmp != 'NULL' and (mindist == -1 or tmp < mindist):
					mindist = tmp
					objInd = ind
			#illumination
			if mindist != -1:
				n = vecAdd(eye, vecSub(scalarMult(mindist, rd), spheres[objInd]))
				if dotProd(n, rd) > 0:
					n = scalarMult(-1, n)
				n = normalize(n)
				colorSeen = (0,0,0)
				for l in lights:
					if not l[3]: # sun
						norml = normalize(l) # direction to light unit
						shadow = False
						for ind, s in enumerate(spheres):
							if ind == objInd:
								continue
							if sphereIntersection(s, norml, vecAdd(eye, scalarMult(mindist, rd))) != 'NULL':
								shadow = True
								break
						if not shadow:
							colorSeen = vecAdd(colorSeen, scalarMult(max(0,dotProd(n, norml)), vecMulti(spheres[objInd][-colorLen::], l[-colorLen::])))
					else: #bulb
						rell = vecSub(l, vecAdd(eye, scalarMult(mindist, rd))) # direction to light nonunit
						d2 = magnSquared(rell)
						rell = normalize(rell)
						shadow = False
						for ind, s in enumerate(spheres):
							if ind == objInd:
								continue
							if sphereIntersection(s, rell, vecAdd(eye, scalarMult(mindist, rd))) != 'NULL':
								shadow = True
								break
						if not shadow:
							intensity = scalarMult(1/d2, l[-colorLen::])
							newColor = scalarMult(max(0, dotProd(n, rell)), vecMulti(spheres[objInd][-colorLen::], intensity))
							colorSeen = vecAdd(colorSeen, newColor)
				colorSeen = tuple([max(0,min(255, round(c * 255))) for c in colorSeen]) #clampin color
				img.im.putpixel((x,y), colorSeen + tuple([255]))

f = open(sys.argv[1], "r")
lines = f.readlines()
img = Image.new("RGBA", (0,0), (0,0,0,0))
outfile = 'Error.png'
spheres = [] #(x,y,z,radius,r,g,b)
lights = [] #(x,y,z,type 1=bulb 0=sun, r,g,b)
currColor = (1, 1, 1) # rgb
for line in lines:
	line.strip()
	lineItems = line.split()
	if lineItems:
		if lineItems[0] == 'png':
			width = float(lineItems[1])
			height = float(lineItems[2])
			outfile = lineItems[3]
			# ... set width, height, etc.
			img = Image.new("RGBA", (round(width), round(height)), (0,0,0,0))
			putpixel = img.im.putpixel
		elif lineItems[0] == 'sphere':
			x = float(lineItems[1])
			y = float(lineItems[2])
			z = float(lineItems[3])
			r = float(lineItems[4])
			spheres.append((x,y,z,r) + currColor)
		elif lineItems[0] == 'color':
			r = float(lineItems[1]) 
			g = float(lineItems[2])
			b = float(lineItems[3])
			currColor = (r, g, b)
		elif lineItems[0] == 'sun':
			x = float(lineItems[1])
			y = float(lineItems[2])
			z = float(lineItems[3])
			lights.append((x,y,z,0) + currColor)
		elif lineItems[0] == 'bulb':
			x = float(lineItems[1])
			y = float(lineItems[2])
			z = float(lineItems[3])
			lights.append((x,y,z,1) + currColor)
		elif lineItems[0] == 'eye':
			x = float(lineItems[1])
			y = float(lineItems[2])
			z = float(lineItems[3])
			# global eye
			eye = (x, y, z)

render(spheres, img)
img.save(outfile)