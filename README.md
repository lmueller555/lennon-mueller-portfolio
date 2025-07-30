# Lennon Mueller Portfolio

This repository contains a simple static portfolio site. The site is deployed using **GitHub Pages** through the workflow defined in `.github/workflows/static.yml`.

To view the page after the workflow runs, visit the GitHub Pages URL for the repository.

The home page includes a dynamic typing animation in the banner. If the page does not immediately show the updated banner, ensure the Pages workflow has completed successfully and refresh your browser.

## Chatbot backend

The chatbot sends its messages to a Pages Function located in `api/chat.js`.
This function forwards the request to the OpenAI API using the
`OPENAI_API_KEY` secret stored in the repository. The key is read on the server
only, so it never appears in the published JavaScript.

Ensure the `OPENAI_API_KEY` secret is configured in the repository. When the
Pages workflow runs, the key is made available to the function environment and
the site can call the `api/chat` endpoint (relative to the site root) to
interact with OpenAI.
