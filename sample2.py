import io

data = io.StringIO()
data.write('JournalDev: ')
print('Python.', file=data)

print(data.getvalue())

data.close()