# WrestleWire Global — Current Release (26 November 2026)

**Live website:** https://wrestlewire-site.yuvraajsingh1155.workers.dev/

**Implementation report:** [Global Redesign Audit — 26 Nov 2026](GLOBAL_REDESIGN_AUDIT_2026-11-26.md)

**Safety backup:** branch backup/pre-global-redesign-2026-11-26

## Current verified state

- 110 retained article pages, 349 A–Z wrestler profiles and 12 official-source briefs, plus dedicated hubs.
- Reader and photography migration completed for 460 article/directory pages with 30 safety tests and publication integrity checks passed.
- Six license-reviewed Wikimedia Commons photo records, publicly credited. Other performers use branded text fallbacks, not misleading fake photography.
- Six-story homepage spotlight with manual controls and 2-second optional playback; responsive desktop/mobile navigation, light/dark preferences, search and links to full pages.
- WWE, AEW, Business, History, Latest, Video, Results, Events and Championship source hubs; Results/Events/Championships are source-linked gateways, not fabricated live databases.
- 4 fully translated Hindi articles and a Hindi landing page, with reciprocal hreflang.
- Search over 450+ page links; wrestler comparison (16 curated editorial profiles), device-local bookmarks, basic PWA.
- Google Search Console verified and free Cloudflare Web Analytics in existing setup. Sitemap has 476 canonical URLs.
- Free official source metadata automation continues; AI draft publishing and AdSense are not activated.

**No new paid purchase or plan has been authorized.** The current feature set uses existing GitHub/Cloudflare infrastructure subject to free-tier and provider usage limits. No guarantee of search rankings, AdSense approval or revenue.

### Important remaining limits

Full independently verified match-history results, championship statistics, every wrestler photograph, full bilingual translation, secure user accounts/admin, moderated fan comments, Google Analytics legal acceptance, AdSense approval, downloaded screenshot artifacts and certified Lighthouse scores are NOT complete. Do not present automatic publisher video metadata as independently fact-checked news.

---

# WrestleWire — Free-First Wrestling Newsroom

Production: https://wrestlewire-site.yuvraajsingh1155.workers.dev/
GitHub: https://github.com/yuvraajsingh1155-cloud/wrestlewire-site

## Verified status, 22 November 2026

- Live Cloudflare Workers site, with GitHub main automatic deployments enabled and tested
- Original red/black design, licensed action photography, article cards entirely clickable
- Eight standalone editorial articles and 16 linked wrestler career profiles
- Official WWE/AEW YouTube source radar, every 3 hours (best effort)
- Automated official source **metadata briefs**: at most 2 per UTC day, noindex
- Google Search Console: URL-prefix ownership **verified** with HTML meta tag
- Google XML sitemap: **submitted**, status Success; initially 25 discovered pages
- Public sitemap now includes 29 substantial article, profile, and policy pages
- Cloudflare Web Analytics: **free website registered and JS beacon added to all page types**
- Google Analytics 4: NOT active; Google legal terms must be accepted by the owner
- Google AdSense: NOT active; the Google account has no existing AdSense publisher account
- Optional free-tier Gemini drafting pipeline: implemented but disabled pending safely stored key and free-tier confirmation

## What gets auto-published for free

The scheduled GitHub workflow checks official WWE and AEW video feeds, validates channel IDs, video IDs, timestamps and original video links, and updates the website's Official Source Radar. It creates up to TWO short source metadata pages per UTC day in the /news/ directory, labelled as publisher updates, not original reporting. These pages do not claim results, wrestler injuries, salary numbers or contract facts, and are marked noindex to avoid scaled-content spam. Source links are attributed.

This is NOT unrestricted AI article writing. Real AI-written drafts need a verified free/unbilled AI Studio project, secret GEMINI_API_KEY stored as a GitHub Actions repository secret and variable ENABLE_FREE_AI_DRAFTS=true. The optional scripts/ai_drafts.py limits drafts to one per UTC day. Outputs are temporary GitHub Actions artifacts requiring editorial fact-checking; they are NOT automatically published to the live site. The key is never committed to the repository. No new paid service has been activated.

GitHub Models was retired July 30, 2026 and is not available as a free API substitute.

## Site content and policies

The website currently has 8 explanatory articles; 16 profile starters covering WWE, AEW and legends; accessible source links; category search and filters. It is not a complete world wrestler database or a full match-by-match results archive. Private incomes are not invented. Real action photos have image credits.

Independent policy pages:
- /about/
- /privacy/
- /editorial-policy/
- /contact/

## Monetization

Google AdSense sign-up is free, but approval is not automatic and an AdSense publisher account must first be created and verified. Google may reject a platform hostname or a site with limited original content. No publisher ID, ads.txt declaration or ad code is installed. The exact workers.dev hostname eligibility is not confirmed. Do not purchase a custom domain or provide payment/tax data unless the owner chooses.

Google Analytics 4 is free but the owner must personally accept Google's terms before a measurement ID exists. For now, cookie-free Cloudflare Web Analytics provides the no-cost traffic overview.

## Risks & limits

- No paid API, paid domain or card is required for the current site.
- GitHub schedules are best-effort and can be delayed.
- Google warns against scaled, low-value automated content; automated metadata pages are noindex by default.
- WrestleWire is not affiliated with WWE, AEW or any performer, and does not reproduce full video transcripts.
- Only verified, attributed claims should appear in reported articles.
