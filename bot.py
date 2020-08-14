from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, PicklePersistence

from functools import wraps

from top_secret import BOT_CODE, PERSISTENCE_FILENAME

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
### DECORATORS

def addSenderToDict(function):
    @wraps(function)
    def helper(update, context):
        try:
            context.chat_data['users']
        except KeyError:
            context.chat_data['users'] = []
        sender = update.message.from_user
        if sender not in context.chat_data['users']:
            context.chat_data['users'].append(sender)
        return function(update,context)
    return helper

def addUsersToChatData(function):
    @wraps(function)
    def helper(update,context):
        if 'users' not in context.chat_data.keys():
            context.chat_data['users'] = []
        return function(update,context)
    return helper
            

###################################################################
### FUNCTIONS FOR COMMAND HANDLERS

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

    
def resetearUsuarios(update,context):
    chat_id = update.effective_chat.id
    context.chat_data['users'] = []

#No sé si esto es correcto
def esUnGrupo(chat_id):
    return chat_id < 0

@addSenderToDict
def startPosta(update,context):
    chat_id = update.effective_chat.id
    if not esUnGrupo(chat_id):
        saludo  = 'Por ahora lo único que puedo hacer es decirte esto.'
        chat_id = update.effective_chat.id
        context.bot.send_message(chat_id=chat_id, text=saludo)
    else:
        pass

###########################################################################
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
        context.chat_data['users'].remove(update.message.left_chat_member)

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

########################################################################
### MAIN DISH
    
def main():
    my_persistence = PicklePersistence(filename=PERSISTENCE_FILENAME)
    updater = Updater(BOT_CODE,persistence=my_persistence,use_context=True)
    dp = updater.dispatcher
    
#    j = updater.job_queue
#    job_minute = j.run_repeating(unaVezPorMinuto,interval=20,first=0)
    
    dp.add_handler(CommandHandler('start',start))
    dp.add_handler(CommandHandler('estasvivo',estasVivo))
    dp.add_handler(CommandHandler('echo',echo))
    dp.add_handler(CommandHandler('chatid',escribirChatId))
    dp.add_handler(CommandHandler('chattype',escribirChatType))
    dp.add_handler(CommandHandler('chatdata', escribirChatData))
    dp.add_handler(CommandHandler('resetusers', resetearUsuarios))


    #Estos dos handlers agregan a los usuarios a la base de datos
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, agregarUsuariosQueDanSeñasDeVida))
    dp.add_handler(MessageHandler(Filters.status_update, agregarOEliminarUsuariosQueUsanLaPuerta)) 
    
    #Esto debe estar después del resto de los Handlers
    unknown_handler = MessageHandler(Filters.command,desconocido)
    dp.add_handler(unknown_handler)
    
    updater.start_polling()
    updater.idle()

main()
