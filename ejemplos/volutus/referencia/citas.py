import re, os, glob
REPO = '/Users/laptop/Desktop/Trabajo/Volutus/VolutusLandingPage'
docs = glob.glob('/Users/laptop/Desktop/Trabajo/statfish/docs/**/*.md', recursive=True)
pat = re.compile(r'`((?:src|worker|public|scripts)/[\w./-]+|index\.html|CLAUDE\.md|wrangler\.jsonc|README\.md):(\d+)(?:-(\d+))?`')
vistas = {}
for d in docs:
    for m in pat.finditer(open(d).read()):
        vistas.setdefault((m.group(1), int(m.group(2)), int(m.group(3) or m.group(2))), set()).add(os.path.basename(d))
malas = 0
for (f, a, b), ds in sorted(vistas.items()):
    p = os.path.join(REPO, f)
    if not os.path.exists(p):
        print('NO EXISTE', f, a, b, ds); malas += 1; continue
    n = sum(1 for _ in open(p, encoding='utf-8'))
    if a < 1 or b > n or a > b:
        print('FUERA DE RANGO', f, a, b, 'lineas', n, ds); malas += 1
print('citas únicas', len(vistas), 'malas', malas)
