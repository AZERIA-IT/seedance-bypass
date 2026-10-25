from PIL import Image, ImageDraw, ImageFont
import os

base = '/home/ubuntu/projects/mohcreatesai/workspace/aladdin-jasmine'
refs = os.path.join(base, 'refs', 'film')
OUT_H = 1050
PAD = 26
TITLE_H = 130
LABEL_H = 70
FOOT_H = 56

font_title = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 42)
font_lab = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 28)
font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 24)

def crop_frac(im, x0f, x1f, y0f=0.0, y1f=1.0):
    w, h = im.size
    return im.crop((int(x0f * w), int(y0f * h), int(x1f * w), int(y1f * h)))

def panel(im, h=OUT_H):
    w, hh = im.size
    return im.resize((max(1, int(w * h / hh)), h), Image.LANCZOS)

def build(name, ref_file, ref_crop, title, footer, ours):
    ref = Image.open(os.path.join(refs, ref_file)).convert('RGB')
    ref = panel(crop_frac(ref, *ref_crop))
    panels = [(ref, 'LE VRAI — frame film 1992')]
    for f, cr, lab in ours:
        im = Image.open(os.path.join(base, f)).convert('RGB')
        panels.append((panel(crop_frac(im, *cr)), lab))
    W = sum(p.width for p, _ in panels) + PAD * (len(panels) + 1)
    H = TITLE_H + OUT_H + LABEL_H + FOOT_H + PAD
    board = Image.new('RGB', (W, H), (252, 252, 252))
    d = ImageDraw.Draw(board)
    d.text((PAD, 26), title, font=font_title, fill=(15, 15, 15))
    d.text((PAD, TITLE_H - 36), footer, font=font_small, fill=(70, 70, 70))
    x = PAD
    y = TITLE_H
    for p, lab in panels:
        d.rectangle([x - 3, y - 3, x + p.width + 3, y + p.height + 3], outline=(150, 150, 150), width=3)
        board.paste(p, (x, y))
        tw = d.textlength(lab, font=font_lab)
        d.text((x + (p.width - tw) / 2, y + p.height + 16), lab, font=font_lab, fill=(20, 20, 20))
        x += p.width + PAD
    out = os.path.join(base, name)
    board.save(out)
    print('board', out, board.size)

footer = 'v2 = attributs affines apres la comparaison (tenue, torse nu, fez). Toujours zero nom. Accepte 1er essai.'

build('comparaison_jasmine_v2.png', 'cap_1562_c.png', (0.34, 0.72, 0.02, 0.98),
      'JASMINE — la vraie (film 1992)  vs  notre correction v2', footer,
      [('va1.png', (0.42, 1.0, 0.0, 0.94), 'NOTRE CORRECTION — v2a'),
       ('va2.png', (0.42, 1.0, 0.0, 0.94), 'NOTRE CORRECTION — v2b')])

build('comparaison_aladdin_v2.png', 'chk5_742_c.png', (0.28, 0.74, 0.0, 1.0),
      'ALADDIN — le vrai (film 1992)  vs  notre correction v2', footer,
      [('va1.png', (0.0, 0.58, 0.0, 0.94), 'NOTRE CORRECTION — v2a'),
       ('va2.png', (0.0, 0.58, 0.0, 0.94), 'NOTRE CORRECTION — v2b')])
