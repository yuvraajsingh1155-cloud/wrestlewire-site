# WrestleWire — Independent Wrestling Newsroom

## Current project (22 November 2026)

- **Cloudflare Worker URL supplied and opened in the owner's browser:** https://wrestlewire-site.yuvraajsingh1155.workers.dev/
- **GitHub source:** https://github.com/yuvraajsingh1155-cloud/wrestlewire-site
- **Visual identity:** original red/black/white lucha-inspired wrestling design.
- **Site:** functional static homepage with category filters, search, linked sample article dialogs, illustrated wrestler artwork.
- **Policy:** transparent About/Contact/Editorial/Privacy disclosures built into the homepage.
- **Official Source Radar:** reads WWE + AEW official YouTube Atom feeds, validates their channel IDs and video URLs, and inserts attributed headlines with canonical official-video links.
- **Scheduled workflow:** .github/workflows/wrestlewire.yml runs every 3 hours (best-effort) and on relevant code changes, tests safety, then commits updates only when sources actually change.
- **SEO groundwork:** canonical and social metadata, robots.txt, sitemap.xml. Check that Cloudflare Worker static asset configuration publishes those additional files.

### Important distinctions

**Not live AI article automation:** Source Radar publishes attributed source *links*, not independent news reporting. AI-written articles, comprehensive verification, advertiser approval, custom domain, account-based analytics and income are **not enabled**. Do not advertise the site as an AI news publisher until the future vetted article system is implemented.

**Deployment sync:** Cloudflare Workers Builds automatically deploys changes on GitHub push *only if* the Worker is configured with repository integration/auto-build. Repository commits alone do not prove a successful Workers deployment.

**Schedule caveat:** GitHub may delay scheduled runs and may disable scheduled workflows for inactive public repositories. If the first run fails, inspect GitHub Actions (the runner's internet access, repository Actions write permissions, and official source availability).

## Repository files
- index.html — design, demo articles, official Source Radar slot, policy sections
- scripts/source_radar.py — Python 3 standard library verified-channel feed importer
- tests/test_source_radar.py — 9 offline safety tests
- data/source_radar.json — safe official feed cache
- .github/workflows/wrestlewire.yml — source refresh and GitHub publish
- .github/workflows/pages.yml — optional GitHub Pages demo, not suggested for a monetized production publication
- robots.txt and sitemap.xml — additional SEO artifacts

### Safety and licensing
- WWE and AEW are unrelated third parties. WrestleWire is not affiliated with either promotion.
- Official YouTube video titles and canonical source links are attributed, with no copied full video transcript or claimed licensed photography.
- Never invent injuries, salaries, private contracts, profit or attendance. Separate opinions from confirmed reporting.
- Do not add secret API tokens to repository files. If a paid AI API is ever activated, store its token in platform secrets and set a spending cap.

### Remaining work
1. Verify Cloudflare auto-deploy and scheduled Actions logs (read from dashboard if available).
2. Build reliable multi-source editorial research, fact checking and AI article drafting/publishing, and configure API credentials and a budget with the owner.
3. Add substantive, source-backed original journalism and maintain corrections and privacy disclosures.
4. Check live sitemap, analytics/privacy compliance and Search Console.
5. Apply for ad monetization only after sufficient original content, eligibility and editorial standards are in place.
