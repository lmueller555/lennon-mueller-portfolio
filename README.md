# Lennon Mueller Portfolio

This repository contains a simple static portfolio site. The site is deployed using **GitHub Pages** through the workflow defined in `.github/workflows/static.yml`.

To view the page after the workflow runs, visit the GitHub Pages URL for the repository.

The home page includes a dynamic typing animation in the banner. If the page does not immediately show the updated banner, ensure the Pages workflow has completed successfully and refresh your browser.

## Chatbot API Key

The chatbot on the site now uses an OpenAI API key that is injected during the
deployment workflow. Set the `OPENAI_API_KEY` secret in the repository so the
workflow can substitute it into `chatbot.js` when deploying. The key will be
baked into the static site, so ensure you are comfortable exposing it publicly.
