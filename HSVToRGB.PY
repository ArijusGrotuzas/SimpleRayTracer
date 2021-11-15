import sys

def HSVtoRGB (hsv):
	h, s, v = hsv

	c = v * s

	r, g, b = 0.0, 0.0, 0.0

	HPrime = h / 60.0

	x = c * (1.0 - abs((HPrime % 2.0 - 1.0)))
	m = v - c

	if (0.0 <= HPrime < 1.0):
	    r = c
	    g = x
	    b = 0.0

	elif (1.0 <= HPrime < 2.0):
	    r = x
	    g = c
	    b = 0.0

	elif (2.0 <= HPrime < 3.0):
	    r = 0.0
	    g = c
	    b = x

	elif (3.0 <= HPrime < 4.0):
	    r = 0.0
	    g = x
	    b = c

	elif (4.0 <= HPrime < 5.0):
	    r = x
	    g = 0.0
	    b = c

	elif (5.0 <= HPrime < 6.0):
	    r = c
	    g = 0.0
	    b = x

	rgb = (r * 255 + m, g * 255 + m, b * 255 + m)

	return rgb

def main():
	rgb = HSVtoRGB((float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3])))
	print("RGB:", rgb)

if __name__ == '__main__':
	main()