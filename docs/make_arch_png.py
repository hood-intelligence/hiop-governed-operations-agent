from PIL import Image, ImageDraw, ImageFont

W, H = 1400, 720
img = Image.new("RGB", (W, H), (2, 5, 8))
d = ImageDraw.Draw(img)
font = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 16)
bold = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 18)
title = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 26)
cyan, ink, line = (67, 214, 255), (234, 247, 255), (40, 90, 110)

d.text((40, 24), "HIOP Governed Operations Agent", font=title, fill=ink)
d.text((40, 60), "Customer request → Strands clerk → Narwhal → Meerkat → CRUSHIA → action → Fossil", font=font, fill=cyan)

boxes = [
    (40, 140, 220, 230, "Customer\nrequest"),
    (260, 140, 460, 230, "Strands\nclerk"),
    (500, 80, 680, 170, "Narwhal\nidentity"),
    (500, 190, 680, 280, "Meerkat\ncontext"),
    (720, 140, 940, 230, "CRUSHIA\nauthority"),
    (980, 40, 1220, 120, "PERMIT\nexecute refund"),
    (980, 140, 1220, 220, "PERMIT_WITH_\nAPPROVAL  no dispatch"),
    (980, 240, 1220, 320, "DENY\nno dispatch"),
    (500, 360, 940, 450, "Human approval = fact, not a permit\nFresh CRUSHIA required"),
    (500, 490, 940, 580, "Fossil evidence\npermission Δ = 0"),
]
for x1, y1, x2, y2, t in boxes:
    d.rounded_rectangle([x1, y1, x2, y2], 10, outline=cyan, width=2)
    d.multiline_text((x1 + 14, y1 + 18), t, font=bold, fill=ink, spacing=4)

d.line([(220, 185), (260, 185)], fill=cyan, width=2)
d.line([(460, 185), (500, 125)], fill=cyan, width=2)
d.line([(460, 185), (500, 235)], fill=cyan, width=2)
d.line([(680, 125), (720, 185)], fill=cyan, width=2)
d.line([(680, 235), (720, 185)], fill=cyan, width=2)
d.line([(940, 160), (980, 80)], fill=cyan, width=2)
d.line([(940, 185), (980, 180)], fill=cyan, width=2)
d.line([(940, 210), (980, 280)], fill=cyan, width=2)
img.save(r"C:\Users\glitt\Downloads\hiop-governed-operations-agent\docs\architecture.png")
print("ok")
