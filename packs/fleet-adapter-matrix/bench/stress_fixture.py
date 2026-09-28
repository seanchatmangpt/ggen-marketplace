def cases(n=1000): return [{'subject':f's{i%10}','consumer':f'c{i%10}','family':f'f{i%12}','targetRepo':'r','targetPath':f'p/{i}'} for i in range(n)]
