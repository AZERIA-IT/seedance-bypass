# Cas : photo « Aladdin & Jasmine » — attributs seuls (2026-10-25)

**Test** : générer une photo d'Aladdin et Jasmine de Disney sans écrire ni « Aladdin », ni « Jasmine », ni « Disney » dans le prompt.

- **Modèle** : `nano_banana_2_1` (Google) — t2i, 9:16, 1k, `count=2`.
- **Coût réel** : 2 × 1,5 cr = **3 cr**, acceptés au **premier essai** (0 refus, 0 remboursement).
- **Jobs** : `794a5073-9bd1-4fc7-b5d1-a379d5e30fe7`, `613eb49a-2bb1-4ab8-8630-2fc6e8f20e30`.
- **Résultat** : les deux variantes sont immédiatement reconnaissables (QA interne : 8/10 et 7/10). Le style maison `3D animated film aesthetic` + description par attributs a suffi — l'étage « reformulations » n'a pas servi sur ce cas.
- **Écarts assumés** : mains imparfaites ; tenue de la fille approximative (robe intégrale plutôt que haut + pantalon de harem) ; visages génériques.
- **Fichiers** : `v1.png` (plus fidèle), `v2.png`, `prompt.txt` (= texte exact soumis).

**Méthodo** : les refus `ip_detected` déjà mesurés sur Aladdin/Jasmine (10/2026) concernaient des jobs **vidéo** avec noms explicites et refs de film scannées. Ici, en image : attributs seuls + style maison = passé au premier essai.

## Comparaison repro vs les vrais personnages (ajout 17:12)

Demande de Mohamed : « c'est pas les vraies, c'est une reproduction — compare avec les vraies ».

Références = frames du film *Aladdin* (1992) via disney.fandom (disneyscreencaps) :
- Jasmine : `ref_jasmine_film1562.png` — jardin, plein jour, tenue turquoise (source `File:Aladdin-disneyscreencaps.com-1562.jpg`).
- Aladdin : `ref_aladdin_film742.png` — tenue de rue (fez + gilet + torse nu), visage net (source `File:Aladdin-disneyscreencaps.com-742.jpg`).

Planches côte à côte, crops buste, cadrage homogène, labels : `comparaison_jasmine.png`, `comparaison_aladdin.png` (générées par `make_compare.py`).

Écarts constatés (repro → vrai) :
- Jasmine : robe d'un bloc au lieu de crop-top + pantalon de harem (ventre nu, épaules dégagées), pas de plume de serre-tête ; coiffure approximative ; bijoux dorés OK.
- Aladdin : chemise sous le gilet (le vrai est torse nu), pas de fez, coiffure surdimensionnée, visage générique.
- Global : « reconnaissable en 2 s, pas fidèle en 5 s » — la fidélité demande une passe fiche perso + refs, pas une génération d'attributs seule.

## Passe v2 — correction des écarts (17:14) + bisection « frame du film en référence » (17:16-17:27)

**v2 (attributs affinés, toujours 0 nom)** : `prompt_v2.txt` (torse nu, gilet ouvert, calot ; haut court, harem, ventre nu, plume). `nano_banana_2_1`, 9:16, 1k, count 2 → 2 jobs **acceptés au 1er essai** `52e1376e-f0ed-4666-b906-e48ea418997d`, `39c47ceb-c0f1-4c29-bc2b-b98dc7d8bd53` (2 × 1,5 cr). Rendus `va1.png` / `va2.png`, planches `comparaison_jasmine_v2.png` / `comparaison_aladdin_v2.png` (crops larges exprès pour montrer les tenues entières). QA : tenues corrigées présentes (haut+harem+ventre nu+plume ; gilet ouvert sur torse nu+calot). Restent : mains, visages génériques ; calot violet alors que la frame source est rouge — à trancher.

**Bisection — une frame du film en référence, ça passe ?** 17 jobs testés, **tous les refus remboursés automatiquement** (~20 cr rendus, 0 cr perdus) :

- paire aladdin+jasmine (`nano_banana_2_1`) → 2× failed (`015d5a1e…`, `4481c584…`)
- **aladdin seul → PASSÉ** (`vr_aladdinref.png`)
- jasmine seule → failed ; puis 4 formes : recadrée serrée, visage seul, planche annotée (bandeau+croix), art officiel → **4× failed** (nano)
- `gpt_image_2_5` : paire ×2 puis jasmine seule → `nsfw` (relance unique = retombe `nsfw`)
- `seedream_5_0_flash` : paire ET aladdin seul → `ip_detected` (le plus strict)
- `soul_v2` (moteur identité) : jasmine seule → **PASSÉ** (`vs1.png`) ; planche duo → **PASSÉ** (`vs2.png`, sort un diptyque 2 panneaux)

**Faits** : le refus vient du **personnage** (Jasmine = déclencheur — 7 essais, 3 moteurs, aucune retouche ne la « dé-classifie »). Crop, annotation et visage seul ne suffisent pas. `soul_v2` l'accepte (0,12 cr/job) → c'est la route refs pour visages connus. Nuance : sur soul, la ref tire le style (« film 2D ») et la tenue dérive → combiner ref + attributs précis et itérer, ne pas attendre une tenue exacte d'un job à ref seule.

**Dépenses** : refus tous remboursés ; net de la soirée ≈ 4,74 cr (rendus gardés). Solde 712,56 cr.

**Fichiers ajoutés** : `prompt_v2.txt`, `va1.png`, `va2.png`, `comparaison_{jasmine,aladdin}_v2.png`, `make_compare_v2.py`, `vr_aladdinref.png`, `jasmine_tight.png`, `jasmine_face.png`, `jasmine_annotated.png`, `vs1.png`, `vs2.png`.
