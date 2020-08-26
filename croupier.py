from functools import wraps

from codenamesTemplate import crearImagenDeClaves
from tablero import Tablero

class Croupier:

    ###############################################################
    ### Excepciones a medida ######################################
    
    class NotYourTurn(Exception):
        pass
    class NotTimeForClues(Exception):
        pass
    class NotTimeForSelecting(Exception):
        pass
    class IllegalClue(Exception):
        pass
    class AlreadyTouchedThat(Exception):
        pass
    class Victoria(Exception):
        pass
    class Derrota(Exception):
        pass

    
    ###############################################################
    ### Decoradores para evitar jugadas fuera de turno ############
    
    def verSiEsTuTurno(reproche):
        def outerHelper(function):
            @wraps(function)
            def innerHelper(self, jugador, *args, **kwargs):
                if self._aQuienQue[jugador]==0:
                    raise self.__class__.NotYourTurn(reproche)
                else:
                    return function(self,jugador,*args,**kwargs)
            return innerHelper
        return outerHelper
    
    def verSiEsHoraDeDarPistas(reproche):
        def outerHelper(function):
            @wraps(function)
            def innerHelper(self, jugador, *args, **kwargs):
                if self._aQuienQue[jugador]!=1:
                    raise self.__class__.NotTimeForClues(reproche)
                else:
                    return function(self,jugador,*args,**kwargs)
            return innerHelper
        return outerHelper

    def verSiEsHoraDeSeleccionar(reproche):
        def outerHelper(function):
            @wraps(function)
            def innerHelper(self, jugador, *args, **kwargs):
                if self._aQuienQue[jugador]!=-1:
                    raise self.__class__.NotTimeForSelecting(reproche)
                else:
                    return function(self,jugador,*args,**kwargs)
            return innerHelper
        return outerHelper

    def verSiTerminó(reproche):
        def outerHelper(function):
            @wraps(function)
            def innerHelper(self, jugador, *args, **kwargs):
                if self._asesinados or self._victoria:
                    raise self.__class__.Derrota(reproche)
                else:
                    return function(self,jugador,*args,**kwargs)
            return innerHelper
        return outerHelper

    
    ################################################################
    ### Diccionario para mensajes de ayuda #########################

    sigue = {
        1:"debe dar una pista.",
        -1:"debe arriesgar."
    }

    ################################################################
    ### La posta ###################################################
    
    def __init__(self, J1="El jugador 1", J2="El jugador 2", maxRondas=9, maxErrores=9, n=5, m=5):
        self._t = Tablero(n,m)

        self._jugadores = [None,J1,J2]
        self._aQuienQue = [None,1,0]

        self._quedanRondas = maxRondas
        self._quedanHallar = [ 15 ] + [ self._t.darTarjeta(i).count('e') for i in [1,2] ]

        self._victoria = False
        self._asesinados = False

        self._historia = []

        
    def darTarjeta(self, n):
        img = crearImagenDeClaves(
            self._t._tarjetas[n],
            self._t._palabras[n],
            self._t._fil,
            self._t._col,
        )
        return img


    @verSiTerminó("El juego ya terminó.")
    @verSiEsTuTurno("Cuando sea tu turno vas a tener tiempo de dar pistas.")
    @verSiEsHoraDeDarPistas("No es momento de dar pistas.")
    def recibirPista(self, jugador, pista, k):
        K = int(k)
        if K<=0 or K>self._quedanHallar[jugador]:
            h = "Ese número de pista es ilegal."
            raise IllegalClue(h)
        elif pista.lower() in self._t.darPalabras():
            h = "Esa palabra no puede usarse como pista."
            raise IllegalClue(h)
        
        h = f"{self._jugadores[jugador]} dice: {pista}, {str(K)}."
        self._historia.append(h)
        self._aQuienQue[jugador] = 0
        self._aQuienQue[3-jugador] = -1


    @verSiTerminó("El juego ya terminó.")
    @verSiEsTuTurno("Muy amable, pero de todas formas no te tocaba jugar.")
    @verSiEsHoraDeSeleccionar("Lo siento, pero dar una pista no es opcional.")
    def pasarDeArriesgar(self, jugador):
        self._aQuienQue[jugador] = 1
        self._quedanRondas -= 1
        
        h = f"{self._jugadores[jugador]} pasa. Ahora debe dar una pista."
        self._historia.append(h)

        
    @verSiTerminó("El juego ya terminó.")
    @verSiEsTuTurno("Tu entusiasmo es apreciado, guardalo para cuando sea tu turno.")
    @verSiEsHoraDeSeleccionar("Ahora deberías dar una pista.")
    def arriesgar(self, jugador, i):
        if self._t.darValorTarjeta(0,i) in ['e','c','a',str(jugador)]:
            raise Croupier.AlreadyTouchedThat("No tiene sentido elegir eso.")

        h = f"{self._jugadores[jugador]} elige la palabra '{self._t.darPalabra(i)}'. "

        otroJugador = 3-jugador
        char = self._t.darValorTarjeta(otroJugador,i)
        if char=='e':
            self._t.cambiarTarjeta(0,i,'e')
            self._t.borrarPalabra(jugador,i)
            self._t.borrarPalabra(otroJugador,i)

            self._quedanHallar[otroJugador] -= 1
            if self._t.darValorTarjeta(jugador,i)=='e':
                self._quedanHallar[jugador] -= 1
            self._quedanHallar[0] -= 1

            h += " ¡Éxito! ¡Era un espía!\n"

            if self._quedanHallar[0] == 0:
                self._victoria = True
                h += f"{self._jugadores[jugador]} ha hecho contacto con el último espía. ¡Felicitaciones, han ganado el juego!"
                self._historia.append(h)
                raise Croupier.Victoria(h)

            elif self._quedanHallar[otroJugador] == 0:
                self._aQuienQue[jugador] = 1
                h += f"Todos los espías de {self._jugadores[otroJugador]} han sido contactados. A partir de ahora, sólo {self._jugadores[jugador]} dará las pistas... Empezando de inmediato."
                self._historia.append(h)
            
            else:
                h += f"{self._jugadores[jugador]} puede elegir de nuevo o pasar."
                self._historia.append(h)

        elif char=='c':
            charAux = 'c' if self._t.darValorTarjeta(0,i)==str(otroJugador) else str(jugador)
            self._t.cambiarTarjeta(0,i,charAux)
            self._t.borrarPalabra(otroJugador,i)

            h += f"¡Es un civil! A {self._jugadores[jugador]} se le acaban las chances para arriesgar.\n"

            if self._quedanHallar[jugador] == 0:
                self._aQuienQue[jugador] = 0
                self._aQuienQue[otroJugador] = 1
                h += f"Pero no quedan espías que contactar por parte suya, así que {self._jugadores[otroJugador]} debe continuar dando las pistas."
                self._historia.append(h)

            else:
                self._aQuienQue[jugador] = 1
                h += "Ahora debe dar una pista."
                self._historia.append(h)

        elif char=='a':
            self._t.cambiarTarjeta(0,i,'a')
            self._t.borrarPalabra(otroJugador,i)
            self._asesinados = True
            h +=  f"¡Es un asesino! {self._jugadores[jugador]} se encuentra en camino de conocer a su creador.\nEl juego ha finalizado."
            self._historia.append(h)
            raise Croupier.Derrota(h)

    def darUltimoMensaje(self):
        return self._historia[-1]
    
    def help(self):
        """Devuelve una string detallando qué es lo siguiente que hay que hacer."""
        if self._asesinados or self._victoria:
            return "¡El juego se acabó!"
        for i in [1,2]:
            if self._aQuienQue[i] in Croupier.sigue.keys():
                return f"{self._jugadores[i]} {Croupier.sigue[self._aQuienQue[i]]}"

            
###################################################################
### AUXILIARES PARA DEBUGEAR ######################################

    def mostrarTarjeta(self,i):
        self.darTarjeta(i).show()

        
###################################################################
### AUXILIARES PROBABLEMENTE INNECESARIAS #########################

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
        
###################################################################
