def make_image(prompt):
 p = clean(prompt).strip()
 # Clean the prompt - remove "image of" words for better AI
 for w in ["image of","picture of","photo of","draw an image of","draw a","draw","generate","create an image of","create"]:
  if p.lower().startswith(w):
   p = p[len(w):].strip()
 if not p: p = "random beautiful scene"
 # Add quality boost for ANYTHING
 quality = "ultra detailed, 8k, cinematic, highly detailed, sharp focus, professional photography"
 safe=urllib.parse.quote_plus(f"{p}, {quality}")
 return f"https://image.pollinations.ai/prompt/{safe}?width=1024&height=1024&nologo=true&seed={random.randint(1,9999999)}&model=flux&enhance=true&nologo=true"
