import json,re,pathlib
root=pathlib.Path(__file__).resolve().parents[1]
items=json.loads((root/"data/features-100.json").read_text())
for item in items:
    slug=item["slug"]
    p=root/"articles"/slug/"index.html"
    if not p.exists(): continue
    html=p.read_text()
    # Put the real image element in the HTML itself, so it is visible even if JS fails.
    img='<img src="/assets/features/'+slug+'.svg" alt="Original editorial artwork illustrating '+item["title"].replace('"',"&quot;")+'" loading="eager" width="1200" height="675">'
    html=re.sub(r'<figure class="hero" id="photo">.*?</figure>',lambda _: '<figure class="hero" id="photo">'+img+'</figure>',html,count=1,flags=re.S)
    html=re.sub(r'<div class="credit" id="credit">.*?</div>', '<div class="credit" id="credit">Original WrestleWire editorial illustration — not a real event photograph.</div>',html,count=1,flags=re.S)
    html=re.sub(r'<script>.*?</script>', "", html, flags=re.S)
    p.write_text(html)
p=root/"index.html"
html=p.read_text()
if "function featureCoverFor" not in html:
    marker="  const storySlides=[];"
    insert='  function featureCoverFor(slug){return slug&&slug.startsWith("feature-")?{src:"/assets/features/"+slug+".svg",alt:"Original wrestling editorial illustration, not an event photograph",credit:"Original WrestleWire artwork",link:"/editorial-policy/"}:null;}\n'
    html=html.replace(marker,insert+marker)
    html=html.replace('const image=editorialPhotos[story.title] ||','const image=featureCoverFor(slug)||editorialPhotos[story.title] ||')
    html=html.replace('const specific=editorialPhotos[s.title];','const specific=featureCoverFor(urlMap[s.title])||editorialPhotos[s.title];')
    html=html.replace('uniquePhoto:!!newFeatures.find(x=>x.title===story.title)','uniquePhoto:false')
p.write_text(html)
print("Updated",len(items),"article covers and homepage art")

# Trigger artwork integration after workflow registration.
