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
        
    def borrarPalabra(self,player,i):
        self._palabras[player][i] = ''


### CROUPIER #######################################################

class Croupier:
    
    def __init__(self,maxTurnos=9,maxErrores=9,n=5,m=5):
        self._t = Tablero(n,m)
        self._leTocaAJ1 = True
        self._pista = [None,None]
        self._asesinado = False
        self._quedanTurnos = maxTurnos
        self._quedanHallar = [self._t.darTarjeta(i).count('e') for i in [1,2] ]
#        self._quedanErrores = maxErrores
        

    # CREAR LAS TARJETAS #

    def crearTarjeta(self, n):
        img = crearImagenDeClaves(
            self._t._tarjetas[n],
            self._t._palabras[n],
            self._t._fil,
            self._t._col,
        )
        return img

    def crearTarjetaNeutral(self):
        img = crearImagenDeClaves(self._t._tarjetas[0],self._t._palabras[0],self._t._fil,self._t._col)
        return img

    def crearTarjetaJ1(self):
        img = crearImagenDeClaves(self._t._tarjetas[1],self._t._palabras[1],self._t._fil,self._t._col)
        return img

    def crearTarjetaJ2(self):
        img = crearImagenDeClaves(self._t._tarjetas[2],self._t._palabras[2],self._t._fil,self._t._col)
        return img

    # MODIFICAR EL ESTADO DEL TABLERO #

    class YaTocasteEso(Exception):
        pass
    
    def arriesgar(self,i): 
        player = 1 if self._leTocaAJ1 else 2 # el que arriesgó 
        otherPlayer = 1 if player==2 else 2

        charAux = self._t.darValorTarjeta(0,i)
        if charAux in ['e','c','a',str(player)]:
            raise YaTocasteEso
        
        char = self._t.darValorTarjeta(otherPlayer,i)

        if char=='e': 
            self._t.cambiarTarjeta(0,i,'e')
            self._t.borrarPalabra(player,i)
            self._t.borrarPalabra(otherPlayer,i)
            self._quedanHallar[otherPlayer] -= 1
            if self._t.darValorTarjeta(player,i)=='e':
                self._quedanHallar[player] -= 1

        elif char=='c':
            charAux = 'c' if self._t.darValorTarjeta(0,i)==str(otherPlayer) else str(player)
            self._t.cambiarTarjeta(0,i,charAux)
            self._t.borrarPalabra(otherPlayer,i)
#            self._quedanErrores -= 1
            self.pasarTurno()

        elif char=='a':
            self._t.cambiarTarjeta(0,i,'a')
            self._asesinado = True


    # FLUJO DE JUEGO #

    def recibirPista(self,pista,n):
        self._pista = [pista,n]
    
    def pasarTurno(self):
        nextPlayer = 2 if self._leTocaAJ1 else 1
        hayCambio = self._quedanHallar[nextPlayer-1]!=0
        self._leTocaAJ1 = not self._leTocaAJ1 if hayCambio else self._leTocaAJ1
        self._quedanTurnos -= 1

    def hayDerrota(self):
        return self._quedanTurnos==0 or self._asesinado

    def hayVictoria(self):
        return self._quedanHallar==[0,0]

    
#########################################################################    
### AUXILIARES PROBABLEMENTE INNECESARIAS 

    def tableroDePalabras(self):
        """Devuelve una string en forma de tablero con las palabras"""
        return stringComoTablero(self._t._palabras[0],self.fil)
    
    def imprimirPalabras(self):
        print('\n',end='')
        print(self.tableroDePalabras())

    def imprimirTarjetaJ1(self):
        print('\n',end='')
        s = stringComoTablero(self.tarjetaJ1,self.fil)
        print(s)

    def imprimirTarjetaJ2(self):
        print('\n',end='')
        s = stringComoTablero(self.tarjetaJ2,self.fil)
        print(s)
        
####################################################################
