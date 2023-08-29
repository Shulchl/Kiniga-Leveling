from os import mkdir
from os.path import abspath, exists


class fontPath():
    _path = abspath('_temp')

    exist = exists(_path)
    if not exist:
        mkdir(_path)
    pathMonserrat = abspath('src/fonts/Montserrat/')
    pathOpen = abspath('src/fonts/Opensans/')

    if not exists(pathMonserrat):
        print(f"Não consegui encontrar o caminho para {pathMonserrat}")

    if not exists(pathOpen):
        print(f"Não consegui encontrar o caminho para {pathOpen}")
