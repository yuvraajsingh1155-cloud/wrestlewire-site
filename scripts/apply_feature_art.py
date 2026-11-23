import json,re,pathlib
root=pathlib.Path(__file__).resolve().parents[1]
items=json.loads((root/"data/features-100.json").read_text())
for item in items:
    slug=item["slug"]
    p=root/"articles"/slug/"index.html"
    if not p.exists(): continue
    html=p.read_text()
    tag='<script>document.getElementById("photo").innerHTML=\'<img src="/assets/features/'+slug+'.svg" alt="Original wrestling editorial illustration, not a real event photograph" loading="eager">\';document.getElementById("credit").textContent="Original WrestleWire editorial illustration. Not a real event photograph.";</script>'
    if "Original WrestleWire editorial illustration. Not a real event photograph." not in html:
        html=html.replace("</body></html>",tag+"</body></html>")
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
