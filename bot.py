from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, PicklePersistence

from functools import wraps

from random import sample

from io import BytesIO

from croupier import Croupier

from top_secret import BOT_TOKEN, PERSISTENCE_FILENAME

##################################################################
### DECORADORES

def addSenderToDict(function):
    @wraps(function)
    def helper(update, context,*args,**kwargs):
        try:
            context.chat_data['users']
        except KeyError:
            context.chat_data['users'] = []
        sender = update.message.from_user
        if sender not in context.chat_data['users']:
            context.chat_data['users'].append(sender)
        return function(update,context,*args,**kwargs)
    return helper

def addUsersToChatData(function):
    @wraps(function)
    def helper(update,context,*args,**kwargs):
        if 'users' not in context.chat_data.keys():
            context.chat_data['users'] = []
        return function(update,context,*args,**kwargs)
    return helper


#No sé si esto es correcto
def esUnGrupo(chat_id):
    return chat_id < 0

def checkIfGroup(function):
    @wraps(function)
    def helper(update,context,*args,**kwargs):
        chat_id = update.effective_chat.id
        if not esUnGrupo(chat_id):
            cordialmente = "Lo único que puedo hacer por ti es decirte esto."
            context.bot.send_message(chat_id=chat_id, text=cordialmente)
            return
        return function(update,context,*args,**kwargs)
    return helper

def checkIfActiveGame(function):
    @wraps(function)
    def helper(update,context,*args,**kwargs):
        chat_id = update.effective_chat.id
        if ('croupier' not in context.chat_data.keys() or not context.chat_data['croupier']):
            mensaje = "No hay ningún juego activo."
            context.bot.send_message(chat_id=chat_id,text=mensaje)
            return
        return function(update,context,*args,**kwargs)
    return helper


def checkIfYouAreAPlayer(reproche):
    def outerHelper(function):
        @wraps(function)
        def innerHelper(update,context,*args,**kwargs):
            user = update.effective_user
            chat_id = update.effective_chat.id
            user_name = user.username if user.username else user.first_name
            if user not in context.chat_data['players']: 
                context.bot.send_message(chat_id=chat_id, text=reproche)
                return
            else:
                return function(update,context,*args,**kwargs)
        return innerHelper
    return outerHelper

####################################################################
### FUNCTIONS FOR MESSAGE HANDLERS

def replicarConVerdades(update,context):
    chat_id = update.effective_chat.id
    if update.message.new_chat_members:
        texto = "Alguien acaba de entrar."
    elif update.message.left_chat_member:
        texto = "Alguien acaba de salir."
    else:
        texto = "Nadie entró ni salió."    
    context.bot.send_message(chat_id=chat_id, text=texto)

@addUsersToChatData
def agregarOEliminarUsuariosQueUsanLaPuerta(update,context):
    chat_id = update.effective_chat.id    
    if update.message.new_chat_members:
        context.chat_data['users'].append(update.message.new_chat_members[0])
    elif update.message.left_chat_member:
        try:
            context.chat_data['users'].remove(update.message.left_chat_member)
        except:
            pass

@addUsersToChatData
def agregarUsuariosQueDanSeñasDeVida(update, context):
    chat_id = update.effective_chat.id
    user = update.message.from_user
    if user and user not in context.chat_data['users']:
        context.chat_data['users'].append(user)
        
def desconocido(update,context):
    solicitud = "No entendí nada. Escribí /ayuda para ver una lista de todas las palabras que entiendo."
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text=solicitud)

    
###################################################################
### FUNCIONES PARA DEBUGEAR

@addSenderToDict
def start(update,context):
    saludo  = 'Por ahora lo único que puedo hacer es decirte esto.'
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text=saludo)

@addSenderToDict
def estasVivo(update,context):
    consuelo = "Sí, estoy vivo."
    chat_id  = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text=consuelo)

@addSenderToDict
def echo(update,context):
    mofa = ' '.join(context.args).upper()
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text=mofa)

@addSenderToDict
def escribirChatId(update,context):
    chat_id = update.effective_chat.id
    text = str(chat_id)
    context.bot.send_message(chat_id=chat_id, text=text)

@addSenderToDict
def escribirChatType(update,context):
    chat_id = update.effective_chat.id
    text = update.effective_chat.type
    context.bot.send_message(chat_id=chat_id, text=text)

@addSenderToDict
def escribirChatData(update,context):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text=str(context.chat_data))


##################################################################
### FUNCIONES PARA ROMPER TODO

@checkIfGroup
@checkIfActiveGame
@checkIfYouAreAPlayer("Muy artero de tu parte, {user_name}, pero no estás en el juego.")
def resetearJuego(update,context,silencioso=False):
    chat_id = update.effective_chat.id    
    context.chat_data['croupier'] = None
    context.chat_data['players'] = []
    if not silencioso:
        mensaje = "Juego eliminado."
        context.bot.send_message(chat_id=chat_id, text=mensaje)
    
def resetearUsuarios(update,context):
    context.chat_data['users'] = []

##################################################################
### FUNCIONES PARA REGULAR EL JUEGO

@addSenderToDict
@checkIfGroup
def startPosta(update,context):
    chat_id = update.effective_chat.id
    if len(context.chat_data['users'])<2:
        rechazo = "Vas a necesitar por lo menos un amigo para jugar este juego."
        context.bot.send_message(chat_id=chat_id, text=rechazo)
        return
    elif ('croupier' in context.chat_data.keys() and context.chat_data['croupier']):
        return info(update,context)
    else:
        J1, J2 = sample(context.chat_data['users'],2)
        name1 = "@"+J1.username if J1.username else J1.first_name
        name2 = "@"+J2.username if J2.username else J2.first_name
        context.chat_data['players'] = [J1,J2]
        context.chat_data['croupier'] = Croupier(J1=name1,J2=name2)
        return info(update,context,firstTime=True)
    
@checkIfGroup
@checkIfActiveGame
def mandarClaveAJugador(update,context,player=0):
    """ Función auxiliar."""
    chat_id = update.effective_chat.id
    croupier = context.chat_data['croupier']
    image = croupier.darTarjeta(player) 
    bio = BytesIO() 
    bio.name = 'image.png'
    image.save(bio, 'PNG')
    bio.seek(0)
    if player == 0:
        context.bot.send_photo(chat_id=chat_id, photo=bio)
    else:
        user = context.chat_data['players'][player-1]
        try:
            context.bot.send_photo(user.id, photo=bio)
        except:
            pass

        
@checkIfGroup
@checkIfActiveGame
@checkIfYouAreAPlayer("Si tanto querés tu propia imagen de claves, ¿por qué no empezás otro juego? Yo me banco varios al mismo tiempo.")
def dame(update,context):
    chat_id = update.effective_chat.id
    user = update.effective_user
    user_name = user.username if user.username else user.first_name
    index = 1 if context.chat_data['players'][0]==user else 2
    mandarClaveAJugador(update,context,index)
    texto = f"Ya te mandé tu imagen de claves, {user_name}."
    context.bot.send_message(chat_id=chat_id, text=texto)

    
@checkIfGroup
@checkIfActiveGame
@checkIfYouAreAPlayer("No le creas a éste, eh.")
def pista(update,context):
    chat_id = update.effective_chat.id
    user = update.effective_user
    index = 1 if context.chat_data['players'][0]==user else 2
    croupier = context.chat_data['croupier']
    try:
        pista, numero = context.args[0], context.args[1]
        croupier.recibirPista(index,pista,numero)
        return info(update,context)
    except IndexError:
        texto = "¡No entendí la pista! ¿Me la repetirías, por favor? Acordate de dejar un espacio entre la palabra y el número."
        context.bot.send_message(chat_id=chat_id, text=texto)
    except Exception as e:
        context.bot.send_message(chat_id=chat_id, text=str(e))
       

@checkIfGroup
@checkIfActiveGame
@checkIfYouAreAPlayer("Estoy seguro de que los verdaderos jugadores tendrán en cuenta tu sugerencia.")
def elijo(update,context):
    user = update.effective_user
    chat_id = update.effective_chat.id
    try:
        palabra = (context.args[0]).lower()
    except IndexError:
        disculpa = "No entendí qué palabra querés elegir. ¿Me la decís de nuevo?"
        context.bot.send_message(chat_id=chat_id, text=disculpa)
        return
    croupier = context.chat_data['croupier']
    indexJugador = 1 if context.chat_data['players'][0]==user else 2
    try:
        indexPalabra = croupier.darPalabras().index(palabra)
        croupier.arriesgar(indexJugador,indexPalabra)
        mensaje=croupier.darUltimoMensaje()
        context.bot.send_message(chat_id=chat_id,text=mensaje)
        return info(update,context)
    except ValueError:
        error = f"'{palabra}' no está en la tarjeta."
        context.bot.send_message(chat_id=chat_id, text=error)
    except Croupier.Derrota or Croupier.Victoria:
        context.bot.send_message(chat_id=chat_id, text=str(e))
        return resetearJuego(update,context,silencioso=True)
    except Exception as e:
        context.bot.send_message(chat_id=chat_id, text=str(e))
        
    
@checkIfGroup
@checkIfActiveGame
@checkIfYouAreAPlayer("Gracias por tu aporte, pero vos no estás jugando.")
def paso(update,context):
    user = update.effective_user
    chat_id = update.effective_chat.id
    index = 1 if context.chat_data['players'][0]==user else 2
    croupier = context.chat_data['croupier']
    try:
        croupier.pasarDeArriesgar(index)
        croupier.darUltimoMensaje()
        return info(update,context)
    except Exception as e:
        context.bot.send_message(chat_id=chat_id,text=str(e))
        return
    

@checkIfGroup
@checkIfActiveGame
def info(update,context,firstTime=False):
    chat_id = update.effective_chat.id
    mandarClaveAJugador(update,context,0)
    if firstTime:
        mandarClaveAJugador(update,context,1)
        mandarClaveAJugador(update,context,2)
        texto = "¡Y así empieza una nueva partida de Codenames Duet! Acabo de enviarles sus tarjetas de clave; si no las recibieron, escríbanme un mensaje por privado y luego escriban /dame en este chat.\n"
        context.bot.send_message(chat_id=chat_id, text=texto)
    croupier = context.chat_data['croupier']
    context.bot.send_message(chat_id=chat_id, text=croupier.darCantidadDeRondas())
    context.bot.send_message(chat_id=chat_id, text=croupier.help())
    


def ayuda(update,context):
    ayuda = "Éstos son las palabras que me sé:\n/start - empieza una nueva partida\n/info - despliega el estado actual del juego;\n/dame - envía tarjeta de claves personal por privado;\n/pista <PALABRA> <NÚMERO> - entra la pista <PALABRA> <NÚMERO> al sistema\n/elijo <PALABRA> - selecciona para arriesgar la palabra <PALABRA> \n/paso - te permite pasar cuando no querés adivinar más palabras\n /reset - elimina el juego actual. Cuidado, ¡esto no se puede deshacer!\n/ayuda - despliega este mensaje"
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text=ayuda)

    

####################################################################
### MAIN DISH
    
def main():
    my_persistence = PicklePersistence(filename=PERSISTENCE_FILENAME)
    updater = Updater(BOT_TOKEN,persistence=my_persistence,use_context=True)
    dp = updater.dispatcher

    #Debug handlers
    dp.add_handler(CommandHandler('_estasvivo',estasVivo))
    dp.add_handler(CommandHandler('_echo',echo))
    dp.add_handler(CommandHandler('_chatid',escribirChatId))
    dp.add_handler(CommandHandler('_chattype',escribirChatType))
    dp.add_handler(CommandHandler('_chatdata', escribirChatData))
    dp.add_handler(CommandHandler('_resetusers', resetearUsuarios))

    #Real handlers
    dp.add_handler(CommandHandler('start',startPosta))
    dp.add_handler(CommandHandler('dame',dame))
    dp.add_handler(CommandHandler('info',info))
    dp.add_handler(CommandHandler('pista',pista,pass_args=True))
    dp.add_handler(CommandHandler('elijo',elijo,pass_args=True))
    dp.add_handler(CommandHandler('paso',paso))
    dp.add_handler(CommandHandler('reset',resetearJuego))
    dp.add_handler(CommandHandler('ayuda',ayuda))

    #Estos dos handlers agregan a los usuarios a la base de datos
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, agregarUsuariosQueDanSeñasDeVida))
    dp.add_handler(MessageHandler(Filters.status_update, agregarOEliminarUsuariosQueUsanLaPuerta)) 
    
    #Esto debe estar después del resto de los Handlers
    unknown_handler = MessageHandler(Filters.command,desconocido)
    dp.add_handler(unknown_handler)
    
    updater.start_polling()
    updater.idle()

main()
