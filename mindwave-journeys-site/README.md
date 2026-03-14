# MindWave Journeys — Landing page


Preview locally:

```bash
# from project root
cd "mindwave-journeys-site"
python3 -m http.server 8000
# open http://localhost:8000 in your browser
```

Notes:
- The background video is referenced from the project root as `../Flow_delpmaspu_.mp4`. Keep the file at the project root or update the `src` in `index.html`.
- Replace `audio/sample.mp3` with your real audio files in `mindwave-journeys-site/audio/`.
- Update the Formspree action URL in `index.html` with your form endpoint or replace with your preferred email/signup integration.

Deploy options:
- GitHub Pages: push this folder to a repo and enable Pages on the `main` branch (or use a `gh-pages` branch).
- Netlify / Vercel: drag-and-drop or link the repo; set the publish directory to the site root.

