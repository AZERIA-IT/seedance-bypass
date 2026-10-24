# Seedance 2.5 — passer le filtre « visage réel » à chaque génération

TL;DR : le blocage n'est pas le prompt, c'est **l'asset d'entrée**. Il faut donc agir sur
l'image/vidéo de référence *et* choisir une route qui accepte les visages. Le script `tools/prep_reference.py` fait la partie locale en une commande.

## 1. Mécanisme réel

- Le filtre est un classifieur « photo de personne réelle » appliqué **aux entrées**
  (images/vidéos de référence), par ByteDance, **avant** que le prompt soit lu.
- Erreur typique : `InputImageSensitiveContentDetected.PrivacyInformation` (parfois un
  simple `Unprocessable Entity` sans détail).
- Il tourne en amont de tous les revendeurs : changer d'hôte **seul** ne suffit pas.
- Mesure de terrain (Reddit) : avec un portrait photoréaliste joint → ~4 refus sur 5 ;
  sans image → jamais de refus. C'est un tirage au sort tant qu'on ne traite pas l'asset.

## 2. Ce qui ne marche PAS

- Recadrer, changer la résolution, le format, réexporter.
- Ajouter des lunettes de soleil.
- Écrire « this is a real person » / « it's me » dans le prompt (le classifieur ne le lit pas).
- Forcer en relançant : c'est un pile ou face, pas une progression.

## 3. Ce qui marche, dans l'ordre d'efficacité

**A. Route qui accepte les visages** — le plus décisif.
Ex. : l'API Seedance 2.5 d'Enhancor (`pass_faces: true`), celle qu'utilise le repo
Genjustsu (`docs/ENHANCOR-API.md`). Base : `https://apireq.enhancor.ai/api/seedance2.5/v1`.
Certains hôtes exposent aussi un palier « portrait » natif.

**B. Sortir l'image de la classe « photo » : envoyer une *planche de référence*.**
Bandeau texte + croix sur un œil (mode `sheet`). Un asset de production annoté n'est plus
classé « photo de quelqu'un » — et les traits restent intacts, donc l'identité passe.
Rapporté fiable (astuce « character sheet ») ; sur 2.5 la ressemblance reste haute.

**C. Casser l'indice « yeux »** (méthode de la vidéo de référence).
Vidéo : flouter la bande des yeux sur les 3 premières secondes. Photo : pixelliser les yeux
**et** joindre une capture nette des yeux en second input. Le modèle reconstruit les yeux,
et la référence n'est plus un visage « vu ».
→ modes `--video` et `eyes` du script ; prompt de reconstruction fourni en sortie.

**D. Route « sortie de confiance ».**
Générer d'abord un portrait avec le modèle, puis l'utiliser comme référence : les sorties
du même compte (< 30 jours, non éditées) sont acceptées comme entrées. C'est la voie
officielle BytePlus — utile pour enchaîner les scènes d'un même personnage.

## 4. Séquence par génération

1. Choisir la route A (clé API qui a `pass_faces`).
2. Préparer la référence avec le script (B ou C).
3. Envoyer en **draft 480p**, jamais directement en 1080p.
4. Accepté → compléter en 1080p. Refusé → changer d'étage (B→C→D), pas de relance aveugle.
5. Joindre le prompt du script : il annule visuellement bandeau/croix/flou dans la sortie.

## 5. À éviter dans la référence

- Une seule photo de face sur fond neutre = le profil exact d'une photo d'identité.
- Une star identifiable (refusée quasi systématiquement) : préférer un visage « commun ».
- Un cadrage multi-plans pour une seule bande de flou : la bande est calculée sur un plan.

## 6. Outil

```bash
PY=/home/ubuntu/ops-tools/releve-caviarde-20261021/.venv/bin/python   # a pillow + opencv

# image : planche (bandeau + croix sur l'œil détecté)
$PY tools/prep_reference.py portrait.png out.png --mode sheet
# image : pixellisation des yeux
$PY tools/prep_reference.py portrait.png out.png --mode eyes
# vidéo : yeux floutés sur les 3 premières secondes
$PY tools/prep_reference.py --video ref.mp4 out.mp4 --seconds 3
# si la détection échoue (yeux déjà pixelisés, cadrage inhabituel)
$PY tools/prep_reference.py --video ref.mp4 out.mp4 --band-rel 0.1,0.30,0.8,0.09
```

Détection : YuNet (`models/face_detection_yunet_2023mar.onnx`, 227 Ko, sha256
`8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4`) → sinon cascade Haar →
sinon bande heuristique / `--band*`. La détection est refaite sur plusieurs instants en
vidéo, la première réussie gagne.

Dépendances : `pillow`, `opencv-python-headless`, `numpy`, `ffmpeg`.

## 7. Fichiers de ce dossier

- `tools/prep_reference.py` — l'outil (modes `sheet`, `eyes`, `grid`, `all`, `--video`).
- `tools/models/` — modèle YuNet.
- `out/` — rendus de test (planche sur un personnage 3D, bande oculaire sur une vidéo).

## 8. Sources

- Doc BytePlus/ModelArk (restriction visages réels + route « sorties de confiance »).
- Repo `sirioberati/Genjustsu-Open-Source-Workflow` (intégration Enhancor `pass_faces`,
  prétraitements depth/masques/face-mesh, draft avant 1080p).
- Retours terrain Reddit/r/Seedance + vidéo « pixelate the eyes / blur the eyes ».
