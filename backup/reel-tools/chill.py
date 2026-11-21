import numpy as np, wave, sys
fn=sys.argv[1]; T=float(sys.argv[2]); seed=int(sys.argv[3])
rng=np.random.default_rng(seed); sr=44100
N=int(sr*(T+2)); t=np.arange(N)/sr; L=np.zeros(N); R=np.zeros(N)
def hz(n): return 440*2**((n-69)/12)
def add(y,t0,pan=0.0,amp=1.0):
    i=int(t0*sr)
    if i>=N: return
    j=min(N,i+len(y)); y=y[:j-i]*amp
    L[i:j]+=y*(1-pan)/1.0; R[i:j]+=y*(1+pan)/1.0
def ep(n,dur,vel):  # FM electric piano
    s=np.arange(int(sr*(dur+1.2)))/sr; f=hz(n)
    idx=2.2*np.exp(-s*3.0)
    y=np.sin(2*np.pi*f*s+idx*np.sin(2*np.pi*f*s))*np.exp(-s*1.1)
    y+=0.3*np.sin(2*np.pi*2*f*s)*np.exp(-s*2.5)
    rel=np.clip((dur+1.2-s)/1.2,0,1); return y*rel*np.minimum(1,s/0.005)*vel
def bell(n,vel):
    s=np.arange(int(sr*3.0))/sr; f=hz(n); y=np.zeros_like(s)
    for r,a,d in [(1,1,0.9),(2.0,0.25,0.5),(3.0,0.08,0.25)]: y+=a*np.sin(2*np.pi*f*r*s)*np.exp(-s/d)
    return y*np.minimum(1,s/0.002)*vel
def pad(notes,dur):
    s=np.arange(int(sr*(dur+1.5)))/sr; y=np.zeros_like(s)
    for n in notes:
        for dt in (-0.07,0.0,0.07):
            f=hz(n)*2**(dt/12); y+=np.sin(2*np.pi*f*s+rng.random()*6)
    env=np.clip(s/1.0,0,1)*np.clip((dur+1.5-s)/1.5,0,1); return y*env/len(notes)/3
def bass(n,dur):
    s=np.arange(int(sr*dur))/sr; f=hz(n)
    return (np.sin(2*np.pi*f*s)+0.2*np.sin(2*np.pi*2*f*s))*np.exp(-s*1.2)*np.minimum(1,s/0.01)*np.clip((dur-s)/0.08,0,1)
def shaker(vel):
    s=np.arange(int(sr*0.09))/sr; y=rng.standard_normal(len(s)); y=np.diff(np.concatenate([[0],y]))
    return y*np.exp(-s*45)*vel
def kick(vel):
    s=np.arange(int(sr*0.35))/sr; f=50+70*np.exp(-s*30)
    return np.sin(2*np.pi*np.cumsum(f)/sr)*np.exp(-s*9)*vel
progs=[[[0,4,7,11],[-3,0,4,7],[5,9,12,16],[7,11,14,17]],
       [[2,5,9,12],[7,11,14,17],[0,4,7,11],[-3,0,4,7]],
       [[0,4,7,11],[4,7,11,14],[5,9,12,16],[5,8,12,14]],
       [[-3,0,4,7],[5,9,12,16],[0,4,7,11],[7,11,14,17]],
       [[5,9,12,16],[7,11,14,17],[4,7,11,14],[-3,0,4,7]]]
key=int(rng.choice([60,62,63,65,67])); prog=progs[seed%len(progs)]
bpm=float(rng.choice([76,80,84,88])); beat=60/bpm; bar=beat*4
nbars=int(np.ceil(T/bar))+1
penta=[0,2,4,7,9,12,14,16,19,21]
for b in range(nbars):
    ch=prog[b%4]; t0=b*bar
    add(pad([key-12+x for x in ch],bar),t0,0,0.10)
    # EP comping: chord on beat 1 and an off-beat
    for k,off in enumerate([0,2.5] if b%2==0 else [0,1.5,3]):
        for x in ch: add(ep(key+x-12,beat*1.2,0.10),t0+off*beat+0.008*rng.random(),pan=float(rng.uniform(-0.3,0.3)))
    add(bass(key-24+ch[0],beat*1.8),t0,0,0.35); add(bass(key-24+ch[0]+(7 if b%2 else 12),beat*1.6),t0+2*beat,0,0.25)
    if b>0:
        add(kick(0.35),t0); add(kick(0.25),t0+2.5*beat)
        for e in range(8): add(shaker(0.05 if e%2 else 0.03),t0+e*beat/2,pan=0.4)
    # bell melody, sparse
    for e in range(8):
        if b%2==1 and rng.random()<(0.35 if e%2==0 else 0.1):
            n=key+12+int(rng.choice(penta)); add(bell(n,0.10),t0+e*beat/2,pan=float(rng.uniform(-0.4,0.4)))
# intro bell motif
pass
m=max(np.abs(L).max(),np.abs(R).max()); L/=m*1.2; R/=m*1.2
st=(np.stack([L,R],1)*32767).astype(np.int16)
w=wave.open(fn,'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(st.tobytes()); w.close()
print(key,bpm,seed%len(progs))
