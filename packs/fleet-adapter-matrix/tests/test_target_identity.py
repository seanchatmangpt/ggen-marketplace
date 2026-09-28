def key(p): return (p['targetRepo'],p['targetPath'])
def test_pair(): assert key({'targetRepo':'r','targetPath':'p'})==('r','p')
