with open('Elsevier_LaTeX/main.tex', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace .5\times$ with 3.5$\times$
text = text.replace('.5\\times$', '3.5$\\times$')

with open('Elsevier_LaTeX/main.tex', 'w', encoding='utf-8') as f:
    f.write(text)

print('Replaced .5\\times$ with 3.5$\\times$')
