import os
file_name = 'images/2024_11_06-00_49_20-00001-2222.png'
file_name = 'images/2024_11_06-00_49_21-00002-2222-markup.png'
nfilename = os.path.normpath(file_name)
print(nfilename+ ' = '+file_name)
ff = open(file_name, 'rb')
bin = ff.read()

print(bin)
ff.close()
