import random

from codenamesTemplate import crearImagenDeClaves
from escupidor import darListaPalabras

### FUNCIONES AUXILIARES ############################################

def darTamanioMax(L):
    aux = 0
    for s in L:
        aux = len(s) if len(s)>aux else aux
    return aux

def stringComoTablero(L,n):
    m = darTamanioMax(L)+1
    i = 0
    s = ''
    while i<len(L):
        for j in range(m-len(L[i])):
            s+=' '
        s+=L[i]+' '
        if (i+1)%n==0:
            s+='\n'
        i+=1
    return s
    

### TABLERO #########################################################
        
class Tablero:

    def __init__(self,n=5,m=5):
        self._fil = n
        self._col = m

        palabras = darListaPalabras(self._fil*self._col)

        espiasN = [ 'n' for i in range(self._fil*self._col) ]
        
        espiasJ1 = ['e','e','a','a','c',
                    'e','a','c','c','c',
                    'e','c','c','c','c',
                    'e','c','c','c','c',
                    'e','e','e','e','c']

        espiasJ2 = ['c','a','a','e','e',
                    'c','c','c','a','e',
                    'c','c','c','c','e',
                    'c','c','c','c','e',
                    'c','e','e','e','e']

        # a=asesino e=espía c=civil n=nada

        L = list(zip(espiasJ1,espiasJ2))
                       
        random.shuffle(L)

        espiasJ1 = [T[0] for T in L]
        #esto es lo que va a ver el jugador 1
        
        espiasJ2 = [T[1] for T in L]
        #esto es lo que va a ver el jugador 2

        self._tarjetas = [espiasN,espiasJ1,espiasJ2]
        self._palabras = [palabras.copy() for i in range(3)]


    def darTarjeta(self,player):
        return self._tarjetas[player]
        
    def darValorTarjeta(self,player,i):
        return self._tarjetas[player][i]
        
    def cambiarTarjeta(self,player,i,char):
        self._tarjetas[player][i] = char

    def darPalabras(self):
        return self._palabras[0]
        
    def darPalabra(self,i):
        return self._palabras[0][i]
        
    def borrarPalabra(self,player,i):
        self._palabras[player][i] = ''

