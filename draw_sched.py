from PIL import Image, ImageDraw, ImageFont
from math import ceil

RED = (255,153,153)
YELLOW = (254,255,153)
GREEN = (153,255,152)
BLUE = (153,204,254)
PURPLE = (204,153,255)
PINK = (255,153,204)
HOUR_PADDING = 2

left_margin_offset = 75
top_margin_offset = 45
box_width = 103
vertical_length_50 = 50

color_scheme = (RED, YELLOW, GREEN, BLUE, PURPLE, PINK)
day_lookup = {'M':0, 'T':1, 'W':2, 'R':3, 'F':4, 'S':5, 'U':6}
length_lookup = {
    0:      0,
    30:     25,
    50:     vertical_length_50,
    80:     76,
    110:    101,
    170:    154,
    180:    101,
}
font = ImageFont.truetype("fonts/tahoma.ttf", 11)

def get_draw_text(course_class):
    course_name = course_class[8]
    class_component = course_class[0]
    class_section = course_class[1]
    class_id = course_class[9]
    instructor = course_class[3]
    instructor_text = ''
    if instructor:
        instructor_full = instructor.split()
        instructor_initials = []
        for i in range(len(instructor_full)-1):
            instructor_initials.append(instructor_full[i][0].upper() + '. ')
        instructor_text = ''.join(instructor_initials) + instructor_full[-1]
        if font.getsize(instructor_text)[0] > box_width-3: # pop until fit with elipses
            while font.getsize(instructor_text + '...')[0] > box_width-3:
                instructor_text = instructor_text[:-1]
            instructor_text += '...'
        instructor_text_size = font.getsize(instructor_text)
    location = course_class[2]
    text = course_name + '\n' + class_component + ' ' + class_section +\
        ' (' + class_id + ')\n' + instructor_text
    return text.upper()

def draw_schedule(sched):
    with Image.open("boilerplate.png") as image:
        draw = ImageDraw.Draw(image)
        colors = 0
        max_end_t = -1
        for course in sched:
            color = color_scheme[colors%6]
            for course_class in course:
                start_t, end_t = course_class[4], course_class[5]
                max_end_t = max(max_end_t, end_t)
                if end_t == -1: # Asynchronous classes
                    continue
                days = course_class[6]
                for day in days:                    
                    r_x0 = left_margin_offset + day_lookup[day] * box_width + day_lookup[day]*2
                    r_x1 = r_x0 + box_width

                    r_y0 = 0
                    hours = (start_t // 60 - 8)
                    minutes = (start_t % 60)
                    bars_past = 0
                    if day in 'MWF':
                        bars_past = max(0, hours*2-1)
                    elif day in 'TR':
                        tr_offset = (start_t-480)//90
                        bars_past = max(0, tr_offset*2+tr_offset-1)
                    r_y0 = top_margin_offset + hours*vertical_length_50 + bars_past
                    r_y0 += length_lookup[minutes]
                    if hours > 0: # Manual y offset adjust 
                        r_y0 += 1

                    r_y1 = r_y0 + length_lookup[end_t - start_t]
                    draw.rectangle([(r_x0-1, r_y0-1), (r_x1+1, r_y1+1)], fill=(0,0,0))
                    draw.rectangle([(r_x0, r_y0), (r_x1, r_y1)], fill = color)
                    draw.text((r_x0+2, r_y0+2), get_draw_text(course_class), (0,0,0), font=font)
                    
            colors += 1
        w,h = image.size
        hours_cropped = 17-(ceil(max_end_t/60)-8 + HOUR_PADDING)
        crop_line = h - (hours_cropped*51 + hours_cropped)
        draw.line((0,crop_line-1, w, crop_line-1), fill=(0, 0, 0), width=1)
        image.crop((0, 0, w, crop_line)).save("schedule.png")