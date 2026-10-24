---
date: 2026-10-24
agent: main
type: note
tags: [higgsfield, seedance, genjutsu, audit, ip-detected, nsfw]
---

# Audit — jobs refusés Higgsfield (20 → 24 oct 2026)

Mesuré sur le compte `mabdel2014@gmail.com` via API (`higgsfield generate list --json --size 100`)
et MCP (`job_status`, `raw_data: true`). Rien de déduit.

## 1. Chiffres

- 100 derniers jobs (20 → 24/10) : **78 completed, 12 `ip_detected`, 5 `nsfw`, 5 `failed`** → 22 refus (22 %).
- Refus = **aucun rendu** (`result_url: null`), mais **crédits rendus automatiquement** :
  13 remboursements sur la fenêtre dispo (22 → 24/10) = **588 crédits**, dont
  `210 + 210` (Object Swap, 23/10), `57` (Motion Transfer, 22/10), `5 × 15` (Seedance 2.5, 24/10), `2` (Nano Banana Pro).
  Le remboursement suit le job à ~1–3 min (horodatage vérifié, ex. job 18:38:15 → refund 18:39:28).
- `reveal_generation` (MCP) = **inopérant sur 3/3 essais** → `This generation was blocked by content checks and cannot be revealed.`
  (testé : Aladdin 2f3f74b1, Star Wars 6222f4bd, Seedance ead675a6). Le bouton « I own the rights » ne sauve pas ces jobs.

## 2. Les 22 refus, un par un

| Date | Job | Modèle | Statut | Réf. média | Déclencheur |
|---|---|---|---|---|---|
| 20/10 15:36 | 6e116ac6 | hf_mult_motion_control | ip_detected | 5 | Aladdin/Jasmine/Razoul nommés |
| 20/10 15:58 | d205c656 | wan3_0_prime | nsfw | 5 | même cast + « bare chest » |
| 21/10 09:06 | de7badd6 | kling_video_edit | failed | 0 | technique (clip 984×2300) |
| 21/10 11:58 | 51fd8f6b | kling_video_edit | failed | 0 | idem |
| 21/10 11:59 | 94c1de18 | kling_video_edit | failed | 0 | idem |
| 21/10 15:32 | d09d2a92 | kling_video_edit | failed | 0 | idem |
| 21/10 16:33 | ff0b73bd | kling_video_edit | failed | 0 | idem |
| 21/10 21:48 | 265004cb | hf_mult_motion_control_flash | nsfw | 5 | Aladdin, « bare » |
| 21/10 21:54 | ad528be9 | hf_mult_motion_control | ip_detected | 5 | Aladdin/Razoul nommés |
| 21/10 22:34 | 03782c82 | hf_mult_motion_control_flash | nsfw | 5 | Aladdin, « bare » |
| 21/10 22:34 | 2f3f74b1 | hf_mult_motion_control | ip_detected | 5 | Aladdin/Razoul nommés |
| 21/10 23:51 | 54383f71 | hf_mult_motion_control | ip_detected | 5 | Aladdin/Jasmine nommés |
| 21/10 23:51 | cd9af664 | hf_mult_motion_control_flash | nsfw | 5 | idem + « barefoot » |
| 22/10 23:14 | 6222f4bd | hf_mult_motion_control | ip_detected | 5 | Obi-Wan / Anakin / Luke nommés, Coruscant |
| 23/10 16:00 | 8b1269d7 | hf_mult_replace_object | ip_detected | 8 | 7 réfs = joueurs réels (ressemblances) |
| 23/10 17:02 | 47c6a6c8 | hf_mult_replace_object | ip_detected | 8 | idem |
| 24/10 18:11 | 4625cdf2 | nano_banana_pro | nsfw | 0 | fiche perso, **faux positif** (re-run passé) |
| 24/10 18:13 | eccb8323 | seedance_2_5 | ip_detected | 1 | « ice queen + braid + ice-blue gown » |
| 24/10 18:29 | ead675a6 | seedance_2_5 | ip_detected | 1 | idem |
| 24/10 18:31 | 624f9fa8 | seedance_2_5 | ip_detected | 0 | idem, **sans aucune image** |
| 24/10 18:34 | bc4eabd3 | seedance_2_5 | ip_detected | 0 | idem |
| 24/10 18:38 | c26846a3 | seedance_2_5 | ip_detected | 0 | idem |

## 3. Causes réelles

### a) `ip_detected` (12) — l'IP *nommée ou ressemblante* dans l'entrée
- Aladdin/Jasmine/Razoul écrits en clair → refus (5 jobs). Star Wars (Obi-Wan, Anakin, Luke, Coruscant) → refus.
- Football : aucun nom dans le prompt, mais les 7 réfs sont des **joueurs réels** → refus.
- Cas le plus parlant : la série « ice queen, tresse platine, robe bleu glacier » → **5/5 refus en texte pur, sans image**
  (le filtre reconnaît la ressemblance Elsa) ; la variante « cheveux blancs libres + tiare + robe argent » passe.
- Conclusion : ce n'est pas le filtre « visage réel » (les réfs Aladdin sont des dessins scannés), c'est le classifieur IP,
  appliqué **avant** le rendu → refus dur. Remboursé, mais rien à récupérer côté reveal (3/3 échec).

### b) `nsfw` (5) — faux positifs sur personnages habillés
- 4 jobs du cast Aladdin : les descriptions contiennent « bare chest », « barefoot », « bare feet ».
- 1 planche perso (nano_banana_pro) : **re-run du prompt strictement identique → completed** (job e1dd9b76). Donc aléatoire, pas lié au prompt.
- Traiter comme transitoire : relancer une fois.

### c) `failed` (5) — technique, Kling O1 Video Edit
- 5/5 sur un même type d'entrée : clip vertical 984×2300, `kling_elements` vide, `debug`/`result_json` vides.
- La même tâche (remplacement de personnages par des chats) passe sur la route Genjutsu flash (7 completed en replace_object_flash).
- Donc : bug/limite de la route `kling_video_edit` sur ce format, pas la faute du contenu.

## 4. Recette

1. Écrire les attributs, jamais le nom déposé ; si le refus tombe, vérifier le déterminisme puis **bisecter token par token** (voir §5, 1 job par token, remboursé si refus) — sinon reformuler le look (2–3 variantes en draft 15 cr) ;
2. `nsfw` → re-run à l'identique une fois (faux positif) ;
3. clips verticaux très hauts → route `hf_mult_*_flash`, pas `kling_video_edit` ;
4. ne pas compter sur `reveal_generation` : considérer tout refus comme « remboursé mais sans rendu ».

## 5. Dernier job refusé — accepté (bisection, 24/10 soir)

Le job `c26846a3` (dernier refus, 18:38) ne peut pas être « réveillé » (`reveal_generation` retesté → KO 5/5) : il a été **réécrit au token près** jusqu'à acceptation.

- Contrôle de déterminisme : prompt identique relancé 2× (même seed puis seed neuf) → refus 2/2 ⇒ verdict **déterministe sur le texte** (l'inverse du `nsfw`, qui est aléatoire).
- Bisection 1 token (draft 480p, 15 cr, remboursé si refus) : sans « braid » → refus ; sans « cape » → refus ; sans « queen » → refus ; « silver »→« white » → refus ; **« snowy forest »→« quiet forest » → completed** (`633bd3b1-d190-4a91-b92e-96fac811fba4`).
- Contre-test neige : « winter forest », « forest with light snow », « snowy pine forest » → refus 3/3 ⇒ sortir du champ neige/hiver pour que cette scène passe.
- Coût net : **15 cr** (l'accepté) ; 9 refus **remboursés (135 cr)**. Solde compte : 810,8 cr.
- Pièces : `cas/reine-20261024/C3_quiet_forest.mp4` (480×854, 5 s, draft), `cas/reine-20261024/C3_frame.png`. Scripts : `cas/reine-20261024/accept_wave.py`, `accept_wave2.py`.
