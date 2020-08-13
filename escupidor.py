#!/usr/bin/python3

import re
import os
import sys
import pickle
import random

def getAndSavePalabras(str):
    file = open("./"+str,'r')
    stringAUX = file.read()
    file.close
    listaAUX = re.split(r'(?m)\s*$\n\s*|\s*,\s*|\A\s+|\s+\Z',stringAUX)
    palabras = []
    n = len(listaAUX)
    for i in range(n):
        aux = listaAUX[i].lower()
        if len(aux)==0:
            continue
        else:
            palabras.append(aux)
    f = open("./base.dict",'bw')
    pickle.dump(palabras,f)
    f.close()
    return

def darListaPalabras(n):
    if os.path.exists("./base.dict"):
        f = open("./base.dict",'rb')
        palabras = pickle.load(f)
        f.close()
        L = random.sample(palabras,n)
        return L
    else:
        print("No se pudo encontrar un archivo 'base.dict'. Saliendo...")
        return []

def imprimirListaLindo(l):
    for s in l:
        print(s.upper())

def main():
        
    if len(sys.argv)==1 or (len(sys.argv)>1 and
                              sys.argv[1]!='reset'):
        n = 1 if len(sys.argv)==1 else int(sys.argv[1])
        L = darListaPalabras(n)
        if len(L)>0:
            imprimirListaLindo(L)

    elif len(sys.argv)>1 and sys.argv[1]=='reset':
        str = sys.argv[2]
        getAndSavePalabras(str)

