import json, struct, numpy as np, collections

V=[]; faces=[]; jgroups=collections.defaultdict(list); cur=None
for line in open("base.obj", encoding="utf-8", errors="replace"):
    if line.startswith("v "):
        a=line.split(); V.append((float(a[1]),float(a[2]),float(a[3])))
    elif line.startswith("g "):
        cur=line[2:].strip()
    elif line.startswith("f "):
        idx=[int(t.split("/")[0])-1 for t in line.split()[1:]]
        if cur=="body": faces.append(idx)
        elif cur and cur.startswith("joint-"): jgroups[cur].extend(idx)
V=np.array(V, dtype=np.float64)
print("corps : %d quads | %d marqueurs d'articulation" % (len(faces), len(jgroups)))

# --- sommets réellement utilisés, ré-indexés ------------------------------
used = sorted({i for f in faces for i in f})
remap = {o:n for n,o in enumerate(used)}
P = V[used].copy()

# --- repère : pieds à y=0, corps centré, unités en centimètres ------------
P *= 10.0                                   # décimètres MakeHuman -> cm
P[:,0] -= (P[:,0].min()+P[:,0].max())/2
P[:,2] -= (P[:,2].min()+P[:,2].max())/2
P[:,1] -= P[:,1].min()
H0 = P[:,1].max()
print("taille de la base : %.2f cm | largeur %.1f | profondeur %.1f" % (H0, np.ptp(P[:,0]), np.ptp(P[:,2])))

# --- triangulation des quads ---------------------------------------------
tris=[]
for f in faces:
    a,b,c,d = [remap[i] for i in f]
    tris.append((a,b,c)); tris.append((a,c,d))
T = np.array(tris, dtype=np.uint32)
print("sommets %d | triangles %d" % (len(P), len(T)))
assert len(P) < 65536, "trop de sommets pour un index 16 bits"

# --- squelette : centroïde de chaque cube-marqueur ------------------------
sk={}
for name, idxs in jgroups.items():
    pts = V[sorted(set(idxs))]*10.0
    c = pts.mean(axis=0)
    c[0] -= (V[used][:,0].min()*10 + V[used][:,0].max()*10)/2
    c[2] -= (V[used][:,2].min()*10 + V[used][:,2].max()*10)/2
    c[1] -= V[used][:,1].min()*10
    sk[name.replace("joint-","")] = [round(float(x),3) for x in c]
json.dump({"hauteur":round(float(H0),3), "articulations":sk}, open("squelette.json","w"), indent=1)
reperes = ["pelvis","spine-2","neck","head","l-shoulder","r-shoulder","l-elbow","l-hand","l-knee","l-ankle"]
print("\nrepères (x, y, z) en cm :")
for r in reperes:
    if r in sk: print("  %-12s %8.1f %8.1f %8.1f" % (r, *sk[r]))

# --- GLB ------------------------------------------------------------------
pos = P.astype(np.float32); idx = T.astype(np.uint16).reshape(-1)
bpos = pos.tobytes(); bidx = idx.tobytes()
pad = lambda b,n=4: b + b"\x00"*((-len(b))%n)
bpos, bidx = pad(bpos), pad(bidx)
buf = bpos + bidx
gltf = {
 "asset":{"version":"2.0","generator":"free-shop / base MakeHuman CC0"},
 "scenes":[{"nodes":[0]}],"scene":0,
 "nodes":[{"mesh":0,"name":"corps"}],
 "meshes":[{"name":"corps","primitives":[{"attributes":{"POSITION":0},"indices":1}]}],
 "buffers":[{"byteLength":len(buf)}],
 "bufferViews":[
   {"buffer":0,"byteOffset":0,"byteLength":len(bpos),"target":34962},
   {"buffer":0,"byteOffset":len(bpos),"byteLength":len(bidx),"target":34963}],
 "accessors":[
   {"bufferView":0,"componentType":5126,"count":len(pos),"type":"VEC3",
    "min":[float(pos[:,0].min()),float(pos[:,1].min()),float(pos[:,2].min())],
    "max":[float(pos[:,0].max()),float(pos[:,1].max()),float(pos[:,2].max())]},
   {"bufferView":1,"componentType":5123,"count":len(idx),"type":"SCALAR"}]
}
js = json.dumps(gltf, separators=(",",":")).encode()
js += b" "*((-len(js))%4)          # le chunk JSON se complète avec des espaces, pas des zéros
glb = struct.pack("<III", 0x46546C67, 2, 12+8+len(js)+8+len(buf))
glb += struct.pack("<II", len(js), 0x4E4F534A) + js
glb += struct.pack("<II", len(buf), 0x004E4942) + buf
open("mannequin.glb","wb").write(glb)
print("\nmannequin.glb : %.0f ko" % (len(glb)/1024))
