# La vidéo source — @heysirio, « bypass IP on Seedance »

- **Lien** : https://www.instagram.com/p/DeZhN96xkZo/ (donnée par Mohamed le 22/10 ; récupérée en 1080p avec son — copie de travail dans le profil CM : `generated/instagram-DeZhN96xkZo/`).
- **Auteur** : Sirio Berati (@heysirio) — également auteur du repo [Genjustsu](https://github.com/sirioberati/Genjustsu-Open-Source-Workflow) montré dans la vidéo.
- **Légende** : « This is how most apps allow you to bypass IP on Seedance. Since they make money off it, I decided to show the flow. This is not legal, and can get you in trouble. Do not do it… But you can drop “workflow” to get other motion transfer workflows and tutorials ».

## Ce qu'elle montre

1. **Méthode vidéo (0–30 s)** : flouter les yeux sur les 3 premières secondes du clip source, tout garder tel quel, exporter le clip entier comme source, et joindre un prompt de reconstruction (capture à l'appui : « Remove the blur and pixelation covering the eyes. Reconstruct natural eyes using the clear eye references provided. Preserve each person's identity, expressions, gaze, blinking and head movement. Keep the rest of the video and its audio unchanged. »).
2. **Méthode photo** : pixeliser les yeux (GPT/Photoshop) **et** joindre une capture nette des yeux en second input, générer en Omni reference.
3. **Le flux du repo (35–65 s)** : la référence vidéo passe par Video Depth Anything (masque de profondeur → garde le mouvement sans toucher à l'IP) ; un LLM décrit le décor depuis une frame extraite par FFMPEG ; un agent décrit les entrées ; un agent final fusionne le tout en un prompt unique → Seedance.

## Statut

- **Rien de la vidéo n'a été reproduit tel quel côté compte** au moment de sa récupération : c'est la source d'inspiration du système (`README.md`), pas un audit.
- Les deux méthodes « yeux » sont outillées localement : `tools/prep_reference.py` (mode `eyes`, `--video`).
- Transcription automatique (whisper, non corrigée) :

```
0.00–2.72   Buddy, I figured out how to generate anyone with see-dance.
2.72–3.56   Damn, what?
3.56–4.96   The first method is from a video.
4.96–6.84   You're gonna take any video and blur the eyes
6.84–9.20   in the first three seconds, keep everything as is,
9.20–11.64  export the entire clip and use it as a source work.
11.64–13.72 Then add this prompt to remove the blur.
13.72–14.64 You can screenshot that.
14.64–15.48 I took a selfie.
15.48–16.96 Is that helpful?
16.96–19.72 Listen, method two is from a photo.
19.72–21.80 You can take a photo and pixelate the eyes
21.80–23.44 using GPT or Photoshop
23.44–26.00 and also take a separate screenshot of the eyes
26.00–28.08 and add both as source images
28.08–29.68 and generate with Omni reference.
29.68–31.10 This is very similar to what
31.10–34.60 it does with transfer motion and avoid copyright issues.
34.60–35.44 Wait, what?
35.44–37.56 Because two things happen when you submit a video.
37.56–41.48 First, your reference video goes through video depth anything
41.48–43.12 which turns it into 3D depth mask.
43.12–44.52 Whoa, wait, that's crazy.
44.52–47.08 This way it preserves some motion without hitting IP.
47.08–48.96 You can find us on Huggingface for free.
48.96–51.08 Then an LLM watches a source video
51.08–53.36 and describes the environment from the first frame
53.36–55.48 captured by FFMPag.
55.48–56.32 And when it's all done,
56.32–59.48 another agent describes your input to input
59.48–62.36 and then a final agent merges everything
62.36–63.72 together into one single prompt.
63.72–66.32 Drop workflow and I'll send everything to you
66.32–68.28 but also follow along if you want the secrets.
68.28–69.72 You're giving them the workflow?
69.72–71.56 I had to watch this six times.
71.56–72.88 What the f**k, cereal?
```

*Textes visibles à l'écran (OCR, extraits)* : le prompt de reconstruction des yeux ; un écran Photoshop (pixellisation) ; « Bypass by … Transfer IP issue » ; les nœuds du workflow (depth / scene agent / motion reference / merge prompt) et un exemple de prompt de fusion (« Replace left performer with Sirio (@Image1), right with Tein (@Image2)… Follow @Video1 depth movement, camera and timing. »).
