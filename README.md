# WrestleWire — Wrestling news website

**Status (22 November 2026):** A responsive, functioning **editorial demo homepage** is committed as `index.html`. It includes category filters, live search and six demonstration explainers with source attribution. It is not a live, continuously updated news publication.

## Publish it using GitHub Pages

1. Open **Settings → Pages** in this repository.
2. Under **Build and deployment**, choose **Source: GitHub Actions**.
3. Go to **Actions → Publish WrestleWire to GitHub Pages → Run workflow**, or push a new change to `index.html`.
4. Wait until the deployment is successful. For this repository the expected URL is `https://yuvraajsingh1155-cloud.github.io/wrestlewire-site/`; **do not treat it as live until the deployment is successful**.

The file `.github/workflows/pages.yml` performs the static deployment.

## About the automated newsroom

The separate workflow `.github/workflows/wrestlewire.yml` is an **inactive guarded scaffold** until its source scripts are added. It will not fabricate stories or consume AI API credit without configured feeds and a secret key. The complete original newsroom starter is packaged separately for owner review; it has not yet been uploaded into this repository.

For the next production phase, upload the source package and verify tests, configure approved editorial feeds and an OpenAI API secret, enable scheduled refresh, and connect a domain and analytics. Start with human review for sensitive stories. GitHub Actions scheduling is best-effort.

**Safety:** Never commit API secrets. The site is not affiliated with WWE or AEW. Do not publish unsupported medical or salary claims. Copyrighted photos must be appropriately licensed.

> **Commercial hosting note:** GitHub Pages is for our design preview only. For an advertising-supported wrestling news business, deploy to a hosting platform whose terms allow the intended commercial use, such as a suitable Cloudflare Pages plan; confirm current terms before launch.
