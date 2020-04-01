from PIL import ImageFont, Image, ImageDraw
import glob, os
import requests
from io import BytesIO

def create_thumb():
	size = 40, 40

	for infile in glob.glob("logos/*.png"):
	    file, ext = os.path.splitext(infile)
	    im = Image.open(infile)
	    im.thumbnail(size)
	    im.save(file+".thumbnail.png", "PNG")

def text_wrap(text, font, max_width):
    lines = []
    if font.getsize(text)[0] <= max_width:
        lines.append(text) 
    else:
        words = text.split(' ')  
        i = 0
        while i < len(words):
            line = ''         
            while i < len(words) and font.getsize(line + words[i])[0] <= max_width:                
                line = line + words[i] + " "
                i += 1
            if not line:
                line = words[i]
                i += 1
            lines.append(line)    
    return lines

def generate_poster(background, text, text_color='', font='Comic', url='', rabbit='', logo_pic=''):
	rgb = tuple(int(background[i:i+2], 16) for i in (0, 2, 4))
	text_color_rgb = tuple(int(text_color[i:i+2], 16) for i in (0, 2, 4))

	img_height = 250
	img_width = 500
	padding = 10

	size = img_height - padding*2, img_height - padding*2

	if(url):
		response = requests.get(url)
		print(response)
		bird = Image.open(BytesIO(response.content)).convert("RGBA")

	else: 
		bird = Image.open("images/{!s}.png".format(rabbit), 'r').convert("RGBA")
	width, height = bird.size 
	min_widht = width
	if height < width:
		min_widht = height

	left = (width - min_widht)/2
	top = (height - min_widht)/2
	right = (width + min_widht)/2
	bottom = (height + min_widht)/2

	bird = bird.crop((left, top, right, bottom))
	bird.thumbnail(size)

	margin_left = img_width - bird.size[0] - padding
	margin_top = img_height - bird.size[1] - padding

	img = Image.new('RGBA', (img_width, img_height), color = rgb)

	if logo_pic and logo_pic != '-':
		logo = Image.open("logos/{!s}.thumbnail.png".format(logo_pic)).convert("RGBA")
		img.paste(logo, (5, 5), logo)

	img.paste(bird, (margin_left, margin_top), bird)

	draw = ImageDraw.Draw(img)

	font = ImageFont.truetype("fonts/{!s}".format(font), size=30, encoding="unic")
	lines = text_wrap(text, font, img_width/2 - 30)
	line_height = font.getsize('hg')[1]

	count = len(lines)
	x = 30
	y = 50

	for line in lines:
	    draw.text((x, y), line, fill=text_color_rgb, font=font)
	    y = y + line_height

	byte_io = BytesIO()
	img.save(byte_io, format='PNG')
	byte_io = byte_io.getvalue()
	return byte_io
	#img.save('images/pil_text.png', optimize=True)


