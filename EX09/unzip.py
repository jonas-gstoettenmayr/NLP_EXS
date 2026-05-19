from zipfile import ZipFile

zf = ZipFile("/home/azureuser/localfiles/jonas_g/NLP4/EX09/data/Sroie_dataset_100.zip", "r")
zf.extractall("./data/Sroie_dataset_100")