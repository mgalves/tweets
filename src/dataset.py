from os import listdir
from os.path import isfile, join


def load_dataset(dataset):
    """
    Carrega os dados dos arquivos de mapeamento
    Retorna duas listas: uma completa para o TWITTER, outra quebrada por arquivo
    """
    keywords = [] # Lista completa
    keywords_by_file = {} # Lista por arquivos
    base_folder = f"/opt/datasets/{dataset}"

    for filename in listdir(base_folder):
        # Percorre o diretorio todo
        fullpath = join(base_folder, filename)

        if isfile(fullpath):
            # EH um arquivo. Vamos ler
            print(f"FILE {fullpath}")
            file = open(fullpath)
            line = file.readline()
            file.close()
            kws = line.split("=")[1].split(",")
            keywords.extend(kws) # Atualiza lista completa
            keywords_by_file[filename] = kws

    return keywords, keywords_by_file
