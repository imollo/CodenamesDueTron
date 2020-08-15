from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, PicklePersistence

from functools import wraps

from random import sample

from io import BytesIO

from tablero import Croupier

from top_secret import BOT_TOKEN, PERSISTENCE_FILENAME

##################################################################
### BOLUDECES

def añadirContador(f):
    def helper(*args):
        helper.calls += 1
        return f(*args)
    helper.calls = 0
    return helper

@añadirContador
def unaVezPorMinuto(context):
    mensaje = 'Han pasado ' +str(unaVezPorMinuto.calls)+ ' minutos.'
    chat_id = -1001481682994
    context.bot.send_message(chat_id=chat_id,text=mensaje)

def unaVezPorMinutoSimple(context):
    mensaje = 'Han pasado varios minutos.'
    chat_id = 171092449
    context.bot.send_message(chat_id=chat_id,text=mensaje)


##################################################################
### DECORADORES

def addSenderToDict(function):
    @wraps(function)
    def helper(update, context,*args):
        try:
            context.chat_data['users']
        except KeyError:
            context.chat_data['users'] = []
        sender = update.message.from_user
        if sender not in context.chat_data['users']:
            context.chat_data['users'].append(sender)
        return function(update,context,*args)
    return helper

def addUsersToChatData(function):
    @wraps(function)
    def helper(update,context,*args):
        if 'users' not in context.chat_data.keys():
            context.chat_data['users'] = []
        return function(update,context,*args)
    return helper


#No sé si esto es correcto
def esUnGrupo(chat_id):
    return chat_id < 0

def checkIfGroup(function):
    @wraps(function)
    def helper(update,context,*args):
        chat_id = update.effective_chat.id
        if not esUnGrupo(chat_id):
            cordialmente = "Lo único que puedo hacer por ti es decirte esto."
            context.bot.send_message(chat_id=chat_id, text=cordialmente)
            return
        return function(update,context,*args)
    return helper

def checkIfActiveGame(function):
    @wraps(function)
    def helper(update,context,*args):
        chat_id = update.effective_chat.id
        if ('croupier' not in context.chat_data.keys() or not context.chat_data['croupier']):
            mensaje = "No hay ningún juego activo."
            context.bot.send_message(chat_id=chat_id,text=mensaje)
            return
        return function(update,context,*args)
    return helper

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
    solicitud = "No entendí nada. Decímelo de nuevo."
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

def resetearJuego(update,context):
    chat_id = update.effective_chat.id
    if not context.chat_data['croupier']:
        mensaje = "No hay juegos activos."
        context.bot.send_message(chat_id=chat_id, text=mensaje)
    else:
        context.chat_data['croupier'] = None
        context.chat_data['players'] = []
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
        context.chat_data['players'] = [J1,J2]
        context.chat_data['croupier'] = Croupier()
        return info(update,context,firstTime=True)
    
@checkIfGroup
@checkIfActiveGame
def mandarClaveAJugador(update,context,player=0):
    """ Función auxiliar."""
    chat_id = update.effective_chat.id
    croupier = context.chat_data['croupier']
    image = croupier.crearTarjeta(player) 
    bio = BytesIO() 
    bio.name = 'image.png'
    image.save(bio, 'PNG')
    bio.seek(0)
    if player == 0:
        context.bot.send_photo(chat_id=chat_id, photo=bio)
    else:
        user = context.chat_data['players'][player-1]
        context.bot.send_photo(user.id, photo=bio)

@checkIfGroup
@checkIfActiveGame
def clave(update,context):
    chat_id = update.effective_chat.id
    user = update.effective_user
    user_name = user.first_name
    if user in context.chat_data['players']:
        index = 1 if context.chat_data['players'][0]==user else 2
        mandarClaveAJugador(update,context,index)
        texto = f"Ya te mandé tu imagen de claves, {user_name}."
    else:
        texto = f"Muy artero de tu parte, {user_name}, pero no estás en el juego."
    context.bot.send_message(chat_id=chat_id, text=texto)
    

def info(update,context,firstTime=False):
    mandarClaveAJugador(update,context,0)
    if firstTime:
        mandarClaveAJugador(update,context,1)
        mandarClaveAJugador(update,context,2)
    croupier = context.chat_data['croupier']
    player1, player2 = context.chat_data['players']
    ####TERMINAR

    


####################################################################
### MAIN DISH
    
def main():
    my_persistence = PicklePersistence(filename=PERSISTENCE_FILENAME)
    updater = Updater(BOT_TOKEN,persistence=my_persistence,use_context=True)
    dp = updater.dispatcher

    #Debug handlers
    dp.add_handler(CommandHandler('estasvivo',estasVivo))
    dp.add_handler(CommandHandler('echo',echo))
    dp.add_handler(CommandHandler('chatid',escribirChatId))
    dp.add_handler(CommandHandler('chattype',escribirChatType))
    dp.add_handler(CommandHandler('chatdata', escribirChatData))
    dp.add_handler(CommandHandler('resetusers', resetearUsuarios))

    #Real handlers
    dp.add_handler(CommandHandler('start',startPosta))
    dp.add_handler(CommandHandler('clave',clave))
    dp.add_handler(CommandHandler('info',info))
    dp.add_handler(CommandHandler('reset',resetearJuego))

    #Estos dos handlers agregan a los usuarios a la base de datos
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, agregarUsuariosQueDanSeñasDeVida))
    dp.add_handler(MessageHandler(Filters.status_update, agregarOEliminarUsuariosQueUsanLaPuerta)) 
    
    #Esto debe estar después del resto de los Handlers
    unknown_handler = MessageHandler(Filters.command,desconocido)
    dp.add_handler(unknown_handler)
    
    updater.start_polling()
    updater.idle()

main()
