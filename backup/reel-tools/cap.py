import sys,json
from PIL import Image, ImageDraw, ImageFont
B="/usr/share/fonts/opentype/inter/Inter-Bold.otf"; SB="/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
def flag(d,x,y,h):
    w=h*1.45; d.rounded_rectangle([x,y,x+w,y+h],radius=h*0.08,fill=(255,215,0)); d.rounded_rectangle([x,y,x+w,y+h/2],radius=h*0.08,fill=(0,87,183)); d.rectangle([x,y+h*0.3,x+w,y+h/2],fill=(0,87,183))
def cap(fn,lines,size=54,y=230,icon=False):
    im=Image.new("RGBA",(1080,1920),(0,0,0,0)); d=ImageDraw.Draw(im)
    f=ImageFont.truetype(B,size); lh=int(size*1.28); ih=size*0.72
    ws=[d.textlength(l,font=f) for l in lines]
    if icon: ws[-1]+=ih*1.45+18
    W=max(ws)+64; H=lh*len(lines)+44
    d.rounded_rectangle([(1080-W)/2,y,(1080+W)/2,y+H],radius=22,fill=(0,0,0,110))
    for i,l in enumerate(lines):
        x=(1080-ws[i])/2; yy=y+22+i*lh
        d.text((x+2,yy+3),l,font=f,fill=(0,0,0,90)); d.text((x,yy),l,font=f,fill="white")
    if icon: flag(d,x+d.textlength(lines[-1],font=f)+18,yy+size*0.25,ih)
    im.save(fn)
def end(fn,t1,t2):
    im=Image.new("RGBA",(1080,1920),(0,0,0,0)); d=ImageDraw.Draw(im)
    f1=ImageFont.truetype(B,74); f2=ImageFont.truetype(SB,44)
    w1=d.textlength(t1,font=f1); w2=d.textlength(t2,font=f2); W=max(w1,w2)+80
    d.rounded_rectangle([(1080-W)/2,280,(1080+W)/2,470],radius=24,fill=(0,0,0,110))
    d.text(((1080-w1)/2,300),t1,font=f1,fill="white"); d.text(((1080-w2)/2,400),t2,font=f2,fill=(255,255,255,230)); im.save(fn)
spec=json.load(open(sys.argv[1]))
for i,c in enumerate(spec["caps"]): cap(f"{spec['dir']}/l{i+1}.png",c["lines"],icon=c.get("icon",False))
end(f"{spec['dir']}/end.png",*spec["end"])
