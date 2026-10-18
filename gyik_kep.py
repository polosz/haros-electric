import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageChops
import numpy as np
GF='/usr/share/fonts/truetype/google-fonts/'
if not os.path.exists(GF+'Poppins-Bold.ttf'):
    GF=os.path.join(D,'fonts')+'/'
B=ImageFont.truetype(GF+'Poppins-Bold.ttf',56)
def font(sz,w='Bold'): return ImageFont.truetype(GF+f'Poppins-{w}.ttf',sz)
import os,sys,argparse
D=os.path.dirname(os.path.abspath(__file__))
src=Image.open(os.path.join(D,'src.png')).convert('RGB')
W,H=1200,900
PH=700  # photo height
def photo(crop):
    c=src.crop(crop)
    c=c.resize((W,PH),Image.LANCZOS)
    c=c.filter(ImageFilter.UnsharpMask(2,110,3))
    return c
def tint(im,col,amt,sat=1.1,con=1.08,bright=1.0):
    im=ImageEnhance.Color(im).enhance(sat); im=ImageEnhance.Contrast(im).enhance(con); im=ImageEnhance.Brightness(im).enhance(bright)
    ov=Image.new('RGB',im.size,col)
    return Image.blend(im,ov,amt)
def vignette(im,strength=0.55):
    w,h=im.size
    y,x=np.ogrid[:h,:w]
    d=np.sqrt(((x-w*0.62)/(w*0.75))**2+((y-h*0.55)/(h*0.8))**2)
    m=np.clip(1-strength*np.clip(d-0.35,0,1)**1.4,0,1)
    a=np.array(im).astype(float)*m[...,None]
    return Image.fromarray(a.astype('uint8'))
def glow(im,cx,cy,r,col,a):
    ov=Image.new('RGB',im.size,(0,0,0)); d=ImageDraw.Draw(ov)
    for i in range(30,0,-1):
        rr=r*i/30; k=(1-i/30)**1.6
        d.ellipse([cx-rr,cy-rr,cx+rr,cy+rr],fill=tuple(int(c*k*a) for c in col))
    return ImageChops.screen(im,ov.filter(ImageFilter.GaussianBlur(25)))
def bolt(d,x,y,s,fill):
    pts=[(x+0.62*s,y),(x,y+0.58*s),(x+0.36*s,y+0.58*s),(x+0.2*s,y+s),(x+0.8*s,y+0.38*s),(x+0.44*s,y+0.38*s),(x+0.62*s,y)]
    d.polygon(pts,fill=fill)
def panel(img,question,items,small='Gyakori kérdés a VBF-ről'):
    d=ImageDraw.Draw(img)
    # gradient panel
    g=Image.new('RGB',(W,H-PH))
    gd=ImageDraw.Draw(g)
    for x in range(W):
        t=x/W
        c=(int(26+(76-26)*t),int(21+(29-21)*t),int(53+(149-53)*t))
        gd.line([(x,0),(x,H-PH)],fill=c)
    img.paste(g,(0,PH))
    d.rectangle([0,PH-5,W,PH-1],fill=(167,139,250))
    d.text((60,PH+18),small.upper(),font=font(22,'Medium'),fill=(196,181,253))
    # question autoscale
    f=font(56)
    while d.textlength(question,font=f)>W-120: f=font(f.size-2)
    d.text((60,PH+46),question,font=f,fill='white')
    # items
    x=60; y=PH+132
    fi=font(30,'Medium')
    for it in items:
        tw=d.textlength(it,font=fi)
        if x+tw+70>W-40: x=60; y+=44
        bolt(d,x,y+4,28,(196,181,253))
        d.text((x+36,y),it,font=fi,fill=(241,236,255))
        x+=36+tw+34
    return img


GRADES={
 1:lambda im:tint(im,(76,29,149),0.12,1.12,1.1),
 2:lambda im:glow(tint(im,(50,30,120),0.22,1.2,1.12),1000,200,420,(110,70,220),0.5),
 3:lambda im:vignette(tint(im,(20,40,110),0.2,1.05,1.18,1.05),0.6),
}
def photo_variant(q,items,grade,out):
    p=photo((0,0,407,240)); p=GRADES[grade](p)
    img=Image.new('RGB',(W,H)); img.paste(p,(0,0))
    panel(img,q,items).save(out,quality=92)
def hero_variant(q,items,out):
    hero=Image.open(os.path.join(D,'hero.png')).convert('RGB')
    hb=hero.resize((W,int(hero.size[1]*W/hero.size[0])),Image.LANCZOS).filter(ImageFilter.UnsharpMask(2,100,3)); hh=hb.size[1]
    img=Image.new('RGB',(W,H)); g=Image.new('RGB',(W,H)); gd=ImageDraw.Draw(g)
    for y in range(H):
        t=y/H; gd.line([(0,y),(W,y)],fill=(int(20+30*t),int(16+10*t),int(48+60*t)))
    img.paste(g); top=(H-hh)//2-150; img.paste(hb,(0,top)); d=ImageDraw.Draw(img)
    d.rectangle([0,top+hh,W,top+hh+4],fill=(167,139,250)); d.rectangle([0,top-4,W,top-1],fill=(167,139,250))
    y0=top+hh+50
    d.text((60,y0),'GYAKORI KÉRDÉS A VBF-RŐL',font=font(26,'Medium'),fill=(196,181,253))
    f=font(72); lines=[]; cur=''
    for w_ in q.split():
        t=(cur+' '+w_).strip()
        if d.textlength(t,font=f)>W-120 and cur: lines.append(cur); cur=w_
        else: cur=t
    lines.append(cur); yy=y0+44
    for l in lines: d.text((60,yy),l,font=f,fill='white'); yy+=88
    yy+=14; fi=font(36,'Medium'); x=60
    for it in items:
        tw=d.textlength(it,font=fi)
        if x+tw+70>W-40: x=60; yy+=54
        bolt(d,x,yy+4,34,(196,181,253)); d.text((x+44,yy),it,font=fi,fill=(241,236,255)); x+=44+tw+40
    img.save(out,quality=92)
if __name__=='__main__':
    a=argparse.ArgumentParser()
    a.add_argument('--style',choices=['photo','hero'],required=True)
    a.add_argument('--q',required=True); a.add_argument('--items',required=True,help='tételek | jellel elválasztva')
    a.add_argument('--grade',type=int,default=1); a.add_argument('--out',required=True)
    r=a.parse_args(); items=[x.strip() for x in r.items.split('|') if x.strip()]
    if r.style=='photo': photo_variant(r.q,items,r.grade,r.out)
    else: hero_variant(r.q,items,r.out)
    print('OK',r.out)
