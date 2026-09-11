# Origine du mannequin

`mannequin.glb` dérive du maillage de base de **MakeHuman** (`data/3dobjs/base.obj`
du dépôt `makehumancommunity/makehuman`).

> « This asset was explicitly released as CC0 in september 2020. »
> — en-tête du fichier source

**Licence : CC0 / domaine public.** Usage commercial libre, aucune attribution
exigée. On crédite quand même : le projet MakeHuman a fait un vrai cadeau à
l'écosystème en relâchant ce maillage.

## Ce qu'on en a tiré

| | |
|---|---|
| Sommets conservés | 13 380 (groupe `body` uniquement) |
| Triangles | 26 756 |
| Écarté | `helper-*` (géométrie d'aide au drapé), `joint-*` (cubes marqueurs) |
| Récupéré des marqueurs | 125 positions d'articulations → `profil.json` |
| Repère | pieds à y = 0, corps centré en x, **unités en centimètres** |
| Taille de la base | 166,59 cm |

## Mensurations mesurées sur le maillage

Obtenues en tranchant le maillage et en prenant le périmètre de l'enveloppe
convexe de chaque coupe — c'est la définition du mètre-ruban.

| Mesure | Base | Hauteur |
|---|---|---|
| Poitrine | 82,98 cm | y = 124,3 |
| Ceinture | 67,31 cm | y = 106,8 |
| Bassin | 91,83 cm | y = 92,3 |
| Épaules (peau) | 45,50 cm | y = 134,1 |
| Cou | 31,38 cm | y = 142,6 |
| Aisselle | — | y = 125,6 |

La base est androgyne et mince : c'est voulu, MakeHuman la conçoit pour être
morphée dans les deux sens. La masculinisation se fait par les facteurs de
mesure (poitrine ×1,18, ceinture ×1,26 pour un 178/74) plus un aplatissement
local du buste.

## Régénérer

```
python3 tools/conv.py     # base.obj -> mannequin.glb + squelette.json
python3 tools/profil.py   # mannequin.glb -> profil.json
```
