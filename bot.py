from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, PicklePersistence

from top_secret import BOT_CODE, PERSISTENCE_FILE

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


###################################################################
### FUNCTIONS FOR COMMAND HANDLERS

def start(update,context):
    saludo  = 'Por ahora lo único que puedo hacer es decirte esto.'
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text=saludo)
    
def estasVivo(update,context):
    consuelo = "Sí, estoy vivo."
    chat_id  = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text=consuelo)

def echo(update,context):
    mofa = ' '.join(context.args).upper()
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text=mofa)

def escribirChatId(update,context):
    chat_id = update.effective_chat.id
    text = str(chat_id)
    context.bot.send_message(chat_id=chat_id, text=text)

def escribirChatData(update,context):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text=str(context.chat_data))

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

#No sé si esto es correcto
def esUnGrupo(chat_id):
    return chat_id < 0

def filtrarUsuarios(update, context):
    chat_id = update.effective_chat.id
    if users not in context.chat_data.keys():
            context.chat_data[users] = []
    if update.message.new_chat_members:
        context.chat_data[users].append(
            update.message.new_chat_member[0]
        )
    elif update.message.left_chat_member:
        context.chat_data[users].remove(
            update.message.left_chat_member
        )

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
    dp.add_handler(CommandHandler('chatdata', escribirChatData))
   
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, filtrarUsuarios))

    #Esto debe estar después del resto de los Handlers
    unknown_handler = MessageHandler(Filters.command,desconocido)
    dispatcher.add_handler(unknown_handler)
    
    updater.start_polling()
    updater.idle()

main()
