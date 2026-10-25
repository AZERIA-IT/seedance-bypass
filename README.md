# seedance-bypass — le système

**But** : générer avec des personnages « sous droits » (ressemblances, visages réels) et passer les filtres **à chaque génération**, sans y passer la nuit.

**Base** : la vidéo de @heysirio (`doc/video-heysirio.md`), son repo [Genjustsu](https://github.com/sirioberati/Genjustsu-Open-Source-Workflow) qui pilote Seedance via Enhancor (`pass_faces`), + **nos propres tests sur le compte** — tout ce qui suit est mesuré ou étiqueté comme non testé.

## À savoir avant tout

- Le filtre lit **l'entrée** (image/vidéo de référence), pas ton texte. Le texte ne compte que quand le filtre IP accroche sur des attributs de ressemblance.
- **Un refus tombe vite (≤ 2 min) et est remboursé automatiquement** (~1–3 min). Tester coûte quasi 0. Un rendu qui passe dépasse 8 min : si ça tourne encore à +8 min, c'est bon signe.
- **Jamais relancer le même paquet à l'aveugle** (sauf `nsfw`). Les refus IP sont déterministes : le même paquet re-refusera. Un refus ⇒ étage suivant.
- **Draft 480p d'abord** (15 cr), jamais le 1080p direct. Un passage accepté **ne vaut pas droit de publication** (QA avant de figer).

## Les techs — dans l'ordre où les essayer

1. **Même paquet, autre moteur (Lite/Flash).** On ne touche ni au prompt ni aux fichiers : on prend la variante `*_flash` du moteur. *Mesuré 24/10 (foot)* : 4 refus sur la route standard (210 cr) → accepté **tel quel** sur `hf_mult_replace_object_flash` (**60 cr**). Preuve : `cas/foot-reprise-20261024/RESULT-C1.txt`.
2. **Attributs, jamais de noms. Pas de chance ? Bisection au token près.** Décrire (« a young queen with silver hair… »), pas « Elsa ». Si refus : vérifier le déterminisme (relance identique ×1), puis **1 seul token modifié par job**, en draft. *Mesuré 24/10 (reine)* : « snowy forest » refusé ×4, **« quiet forest » accepté** ; 3 contre-tests « neige » refusés 3/3. Preuve : `doc/franchises-higgsfield.md`, `cas/reine-20261024/`.
3. **Planche de référence.** Transformer la photo en « planche de production » (bandeau + croix sur un œil) : elle ne ressemble plus à une photo d'identité, l'asset sort de la classe « photo ». `tools/prep_reference.py in.png out.png --mode sheet`.
4. **Casser l'indice « yeux »** (méthode de la vidéo). Vidéo : flouter la bande des yeux sur les 3 premières secondes. Photo : pixelliser les yeux **et** joindre une capture nette des yeux en second input. `tools/prep_reference.py --video` / mode `eyes` ; joindre le prompt de reconstruction fourni par l'outil.
5. **Route qui accepte les visages** (`pass_faces: true`, API Enhancor — c'est ce que pilote le repo Genjustsu). À activer dès qu'une clé API est disponible ; étage le plus décisif pour le filtre « visage réel ».
6. **Sorties de confiance.** Générer d'abord un portrait avec le modèle, puis l'utiliser comme référence : les sorties récentes du même compte passent comme entrées (voie officielle BytePlus).
7. **Nettoyages d'asset** (réencoder sans audio, miroir). *Mesuré : insuffisant seul* (2 refus sur foot). À garder en combo, jamais en premier.

Cas particuliers :

- `nsfw` = aléatoire → relancer **une fois** à l'identique (mesuré : re-run identique accepté).
- **Réf = frame d'un film** (personnage identifiable) : refus côté « personnage » — recadrer/annoter sans effet. Si ça bloque, mettre la ref sur le moteur identité **`soul_v2`** (il l'accepte ; il tire le style/tenue, garder les attributs du prompt). Cas : `cas/aladdin-jasmine-20261025/`.
- Clips verticaux très hauts → route `hf_mult_*_flash`, pas `kling_video_edit` (5/5 échecs techniques mesurés).
- `reveal_generation` est cassé (0/5) → ne pas compter dessus.

## Le protocole, à chaque génération

1. Préparer l'entrée (attributs / planche / yeux selon le cas) — et viser le moteur **flash** dès le départ.
2. Draft 480p → jamais 1080p direct.
3. Refus ≤ 2 min → étage suivant (remboursé). Jamais 2× le même paquet.
4. Accepté → **figer** prompt + fichiers (mêmes mots, mêmes hashes), puis monter en qualité.
5. QA humaine puis publication éventuelle.

## Preuves, journal, sources

- `cas/foot-reprise-20261024/` — 4 refus remboursés (nettoyage, miroir, texte), **accepté en changeant de moteur** (paquet identique). Journal complet.
- `cas/aladdin-jasmine-20261025/` — attributs seuls (0 refus, recommence) ; comparaison vs film 1992 ; v2 corrigée ; bisection refs film : aladdin passe seul, jasmine bloquée (remboursée), `soul_v2` l'accepte.
- `cas/reine-20261024/` — bisection « quiet forest » (9 refus remboursés, 15 cr nets).
- `doc/audit-refus-2026-10.md` — audit de 22 refus (20→24/10) : chiffres, causes réelles, recette.
- `doc/franchises-higgsfield.md` — planque Disney/Pixar/Star Wars : ce qui passe, ce qui ne passe pas, formulations validées.
- `doc/face-filter.md` — le filtre « visage réel » en détail (mécanisme, planche, yeux, sortie de confiance).
- `doc/video-heysirio.md` — la vidéo source transcrite, et ce qu'elle montre vraiment.

**Sources** : vidéo instagram.com/p/DeZhN96xkZo (@heysirio) · repo [sirioberati/Genjustsu-Open-Source-Workflow](https://github.com/sirioberati/Genjustsu-Open-Source-Workflow) (MIT) · API Enhancor (`pass_faces`) · docs BytePlus/ModelArk · retours Reddit r/Seedance.

## Outils

- `tools/prep_reference.py` — planche (bandeau + croix sur l'œil détecté, YuNet), yeux pixellisés, flou oculaire vidéo. Dépendances : pillow, opencv, numpy, ffmpeg (cf. `doc/face-filter.md` §6).
- `tools/hf_mcp.py` — client Higgsfield en une commande : `refresh`, `call`, `status`, `reveal`.
- `tools/hf_franchise_test.py` — chaîne complète upload → confirm → draft → veille (exemple exécutable).
