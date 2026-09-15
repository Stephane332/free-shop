"""base.obj (MakeHuman, CC0) -> mannequin.glb + squelette.json

Ne garde que le groupe `body`. Les groupes `helper-*` (aide au drapé) sont
jetés ; les `joint-*` sont des cubes marqueurs dont on ne garde que le
centroïde : ils nous donnent le squelette gratuitement.
Les UV sont conservées — sans elles aucune texture de peau ne peut se poser.
"""
import json, struct, numpy as np, collections

V=[]; VT=[]; faces=[]; jg=collections.defaultdict(list); cur=None
for line in open("base.obj", encoding="utf-8", errors="replace"):
    if line.startswith("v "):
        a=line.split(); V.append((float(a[1]),float(a[2]),float(a[3])))
    elif line.startswith("vt "):
        a=line.split(); VT.append((float(a[1]), float(a[2])))
    elif line.startswith("g "): cur=line[2:].strip()
    elif line.startswith("f "):
        t=[x.split("/") for x in line.split()[1:]]
        if cur=="body":
            faces.append([(int(p[0])-1, int(p[1])-1 if len(p)>1 and p[1] else -1) for p in t])
        elif cur and cur.startswith("joint-"):
            jg[cur].extend(int(p[0])-1 for p in t)
V=np.array(V, dtype=np.float64); VT=np.array(VT, dtype=np.float64)
print("corps : %d quads | %d marqueurs d'articulation" % (len(faces), len(jg)))

# --- Morph de morphologie ------------------------------------------------
# La base MakeHuman est neutre et androgyne. On lui applique la cible
# officielle « african-male-young » (CC0, écrite par l'équipe MakeHuman) :
# c'est un vrai morph d'auteur, pas une déformation devinée. Elle porte le
# genre ET l'ethnie, ce qui est exactement la clientèle de la boutique.
CIBLE, POIDS = "cibles/african-male-young.target", 1.0
import os
if os.path.exists(CIBLE):
    n = 0
    for L in open(CIBLE):
        L = L.strip()
        if not L or L.startswith("#"): continue
        p = L.split()
        if len(p) < 4: continue
        i = int(p[0])
        if i < len(V):
            V[i] += POIDS*np.array([float(p[1]), float(p[2]), float(p[3])]); n += 1
    print("morph « %s » appliqué à %.0f %% : %d sommets" % (os.path.basename(CIBLE), POIDS*100, n))
else:
    print("ATTENTION : cible de morphologie absente, le corps restera androgyne")

# sommets uniques sur la paire (position, uv) : les coutures UV en dupliquent
paires={}; P=[]; UV=[]; src=[]
def idx(pv):
    if pv not in paires:
        paires[pv]=len(P); P.append(V[pv[0]]); UV.append(VT[pv[1]] if pv[1]>=0 else (0.,0.)); src.append(pv[0])
    return paires[pv]
tris=[]
for f in faces:
    a,b,c,d = [idx(p) for p in f]
    tris.append((a,b,c)); tris.append((a,c,d))
P=np.array(P); UV=np.array(UV); T=np.array(tris, dtype=np.uint32)

# repère : pieds à y=0, corps centré en x et z, unités en centimètres
P *= 10.0                                     # décimètres MakeHuman -> cm
dx = (P[:,0].min()+P[:,0].max())/2; dz = (P[:,2].min()+P[:,2].max())/2; dy = P[:,1].min()
P[:,0] -= dx; P[:,2] -= dz; P[:,1] -= dy
H0 = P[:,1].max()
UV[:,1] = 1.0 - UV[:,1]                       # OBJ compte v vers le haut, glTF vers le bas
print("taille de la base %.2f cm | sommets %d | triangles %d" % (H0, len(P), len(T)))
assert len(P) < 65536, "trop de sommets pour un index 16 bits"

sk={}
for name, idxs in jg.items():
    c = V[sorted(set(idxs))].mean(axis=0)*10.0
    sk[name.replace("joint-","")] = [round(float(c[0]-dx),3), round(float(c[1]-dy),3), round(float(c[2]-dz),3)]
json.dump({"hauteur":round(float(H0),3), "articulations":sk}, open("squelette.json","w"), indent=1)

pos = P.astype(np.float32); uv = UV.astype(np.float32); ind = T.astype(np.uint16).reshape(-1)
pad = lambda b: b + b"\x00"*((-len(b))%4)
bpos, buv, bind = pad(pos.tobytes()), pad(uv.tobytes()), pad(ind.tobytes())
buf = bpos + buv + bind
gltf = {
 "asset":{"version":"2.0","generator":"free-shop / base MakeHuman CC0"},
 "scenes":[{"nodes":[0]}], "scene":0, "nodes":[{"mesh":0,"name":"corps"}],
 "meshes":[{"name":"corps","primitives":[{"attributes":{"POSITION":0,"TEXCOORD_0":1},"indices":2}]}],
 "buffers":[{"byteLength":len(buf)}],
 "bufferViews":[
   {"buffer":0,"byteOffset":0,"byteLength":len(bpos),"target":34962},
   {"buffer":0,"byteOffset":len(bpos),"byteLength":len(buv),"target":34962},
   {"buffer":0,"byteOffset":len(bpos)+len(buv),"byteLength":len(bind),"target":34963}],
 "accessors":[
   {"bufferView":0,"componentType":5126,"count":len(pos),"type":"VEC3",
    "min":[float(pos[:,i].min()) for i in range(3)], "max":[float(pos[:,i].max()) for i in range(3)]},
   {"bufferView":1,"componentType":5126,"count":len(uv),"type":"VEC2"},
   {"bufferView":2,"componentType":5123,"count":len(ind),"type":"SCALAR"}]
}
js = json.dumps(gltf, separators=(",",":")).encode(); js += b" "*((-len(js))%4)
glb  = struct.pack("<III", 0x46546C67, 2, 12+8+len(js)+8+len(buf))
glb += struct.pack("<II", len(js), 0x4E4F534A) + js
glb += struct.pack("<II", len(buf), 0x004E4942) + buf
open("mannequin.glb","wb").write(glb)
print("mannequin.glb : %.0f ko (avec UV)" % (len(glb)/1024))
