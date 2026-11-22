# WrestleWire — आपका Step-by-Step Launch Checklist

## अभी क्या हो चुका है (22 November 2026)
- GitHub repository connected: `yuvraajsingh1155-cloud/wrestlewire-site`
- `index.html` में red-black-white wrestling theme, original luchador mask art, illustrated high-flying action, WWE/AEW/business/analysis sections, search, filters और sample stories uploaded हैं।
- `.github/workflows/pages.yml` static site deploy करने के लिए तैयार है।
- `.github/workflows/wrestlewire.yml` केवल guarded newsroom scaffold है; यह अभी पूरे article pipeline के रूप में काम नहीं कर रहा।
- Website URL live और public deployment की पुष्टि नहीं हुई है।
- Artificial wrestler salaries, injuries या financial figures publish नहीं किए गए।

## अब आपको एक-एक करके क्या करना है

### STEP 1 — GitHub Pages ON करना (अभी जरूरी)
1. यह लिंक खोलें: https://github.com/yuvraajsingh1155-cloud/wrestlewire-site/settings/pages
2. `Build and deployment > Source` में `GitHub Actions` चुनें।
3. यहाँ जाएँ: https://github.com/yuvraajsingh1155-cloud/wrestlewire-site/actions
4. `Publish WrestleWire to GitHub Pages` workflow खोलें। `Run workflow` चुनें, branch `main` रखें और run करें।
5. Run successful होने के बाद site URL देखें: https://yuvraajsingh1155-cloud.github.io/wrestlewire-site/
6. अगर GitHub permission या 404 error मिले, error का screenshot या text चैट में साझा करें।

### STEP 2 — Design approval
- Live site खोलकर desktop और mobile view देखें।
- Logo, lucha art, colours और homepage sections में edits हों तो ChatGPT को बताएं; code में edit किया जा सकता है।

### STEP 3 — Domain (optional, बाद में)
- पहले नया brand name और trademark conflicts जाँचें।
- चाहें तो domain खरीदें, जैसे अपना `.com` या `.in` विकल्प। किसी domain की availability अभी verified नहीं है।
- GitHub Pages settings में custom domain + DNS configure करें। शुरुआती free subdomain पर domain खरीदना जरूरी नहीं है।

### STEP 4 — Business identity and compliance (launch से पहले)
- Website owner/publication नाम, संपर्क email, About, Contact, Privacy Policy, Editorial Policy, Corrections Policy तैयार करें।
- अपनी actual data collection (analytics, newsletter, ads), cookie consent और applicable privacy law के अनुसार policy प्रकाशित करें; generic template के झूठे claims publish न करें।
- Copyrighted wrestler photos, promotions के logos या videos बिना अनुमति reproduce न करें; licensed/authorized images या original artwork ही प्रयोग करें।

### STEP 5 — Automated publishing (अलग technical phase)
- Verified news feeds और उनके terms of use तय करें (WWE/AEW official announcements and appropriately licensed sources)।
- Paid AI model चुनें और API budget cap बनाएं। ChatGPT subscription API calls को cover नहीं करता।
- API secret केवल `Settings > Secrets and variables > Actions` में सुरक्षित डालें; chat में secret paste न करें।
- Full newsroom scripts, tests, source checks और build integration जोड़ने के बाद workflow enable करें।
- शुरुआत में human review mode; injury, contract, salary और sensitive rumors को कभी auto-publish न करें।

### STEP 6 — Monetization (अच्छे original content के बाद)
- Google Search Console में site verify करें, sitemap submit करें और indexing देखें।
- Analytics install करें (privacy disclosures/consent जहाँ लागू हों)।
- Original reporting, proper citations, compelling explainers और regular quality review करें।
- उसके बाद Google AdSense application करें; approval, traffic, revenue या timeline की कोई guarantee नहीं।
- Affiliate offers/sponsorships पर आवश्यक disclosure करें।

## ज़रूरी links
- Repository: https://github.com/yuvraajsingh1155-cloud/wrestlewire-site
- Pages: https://github.com/yuvraajsingh1155-cloud/wrestlewire-site/settings/pages
- Actions: https://github.com/yuvraajsingh1155-cloud/wrestlewire-site/actions
- Expected site: https://yuvraajsingh1155-cloud.github.io/wrestlewire-site/
- Google Search Console: https://search.google.com/search-console/about
- Google AdSense: https://adsense.google.com/

**Next action:** सबसे पहले STEP 1 पूरा करें। फिर website working URL या GitHub run status से deployment validate किया जा सकेगा।

## Important hosting note (business use)
GitHub Pages को केवल prototype/preview के लिए इस्तेमाल करें। GitHub Pages की official limits policy इसे free hosting के रूप में online business चलाने के लिए intended/allowed नहीं मानती। Real ad-supported WrestleWire publication के production launch के लिए Cloudflare Pages या अन्य commercial-use-appropriate hosting चुनें और terms verify करें। GitHub repository code रखने के लिए जारी रह सकती है।
