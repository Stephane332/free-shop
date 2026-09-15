# Origine du mannequin

Tout vient de **MakeHuman**, et tout est en **CC0 / domaine public** : usage
commercial libre, aucune attribution exigée. On crédite quand même — le projet
MakeHuman a fait un vrai cadeau à l'écosystème en relâchant ces assets.

| Élément | Source | Licence |
|---|---|---|
| Maillage de base | `makehuman/data/3dobjs/base.obj` | CC0 (déclaré dans l'en-tête du fichier) |
| Morphologie | `data/targets/macrodetails/african-male-young.target` | CC0 (Manuel Bastioni, 2014) |
| Peau | pack `skins02_cc0` — `mindfront_skin_male_african_middleage` | CC0 (MINDFRONT, Suède) |

## Le maillage

| | |
|---|---|
| Sommets | 14 517 (groupe `body` seul, coutures UV dupliquées) |
| Triangles | 26 756 |
| Écarté | `helper-*` (aide au drapé), `joint-*` (cubes marqueurs) |
| Récupéré des marqueurs | 125 positions d'articulations → `squelette.json` |
| Repère | pieds à y = 0, centré en x et z, **unités en centimètres** |

La base MakeHuman est neutre et androgyne. La cible officielle
`african-male-young` lui donne le genre **et** l'ethnie en un seul morph
d'auteur — bien meilleur qu'une déformation devinée.

## Mensurations, mesurées sur le maillage

Obtenues en tranchant le maillage et en prenant le périmètre de l'enveloppe
convexe de chaque coupe : c'est la définition du mètre-ruban.

| Mesure | Valeur | Hauteur |
|---|---|---|
| Stature | 181,5 cm | — |
| Poitrine | 100,4 cm | y = 133,7 |
| Ceinture | 78,1 cm | y = 114,2 |
| Bassin | 95,8 cm | y = 96,7 |
| Épaules (peau) | 51,9 cm | y = 134,1 |
| Cou | 38,7 cm | y = 158,3 |
| Entrejambe | 87,2 cm (48,0 % de la stature) | — |

Poitrine > bassin : c'est le V masculin, et ça tombe dans les normes adultes.

## Les textures

Les PNG d'origine pèsent 10,6 Mo. Ramenés à **320 ko** pour tenir sur un
forfait data réel, sans perte visible à distance d'écran.

Une correction a été nécessaire : l'auteur de cette peau a peint un visage
africain foncé sur un corps nettement plus clair, ce qui donnait un mannequin
bicolore. Le corps est recalé sur le visage avec un gain de 0,69 — mesuré
identique sur les trois canaux, donc pur écart de luminosité, aucune dérive
de teinte.

## Régénérer

```bash
pip install numpy pillow
curl -o base.obj https://raw.githubusercontent.com/makehumancommunity/makehuman/master/makehuman/data/3dobjs/base.obj
curl -o skins02.zip https://files2.makehumancommunity.org/asset_packs/skins02/skins02_cc0.zip
python3 tools/conv.py     # base.obj + morph -> mannequin.glb + squelette.json
python3 tools/profil.py   # mannequin.glb -> profil.json (mensurations par tranche)
python3 tools/tex.py      # peaux PNG -> WebP recalés
```
