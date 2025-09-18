# Astonish docs (Docusaurus)

This folder contains a minimal Docusaurus site that documents the `astonish.py` generative art script.

To run locally (if you have Node.js and Docusaurus installed):

```
cd website
npm install
npm start
```

Note: this is a light scaffold; the actual renders live in the repo `outputs/` folder.

GitHub Pages / CI
------------------

This repository contains a GitHub Actions workflow `.github/workflows/gh-pages.yml` that builds the Docusaurus site on pushes to `main` and deploys the `website/build` directory to GitHub Pages using `peaceiris/actions-gh-pages`. No further configuration is required for public repositories; GitHub will provide the `GITHUB_TOKEN` to the workflow.
