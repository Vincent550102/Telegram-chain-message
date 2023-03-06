from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from telegram.constants import ChatType
from database import Database
from dotenv import load_dotenv
import os

load_dotenv()


class TelegramBot():

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="""[指令列表]
/help 印出這個列表
/addchain <id> [id]... 增加想要連鎖發話的 id，可透過 /mygroupid 來獲得 id
/listchain 列出當前有設定哪些連鎖發話
/deletechain <id> 刪除指定連鎖發話
/wall <message> 連鎖發話！
/myid 印出 id
""")

    async def addchain(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = update.message.text.split()
        if len(args) < 2:
            await context.bot.send_message(chat_id=update.effective_chat.id, text='參數錯誤')
            return

        result_message = '[新增連鎖發話]\n'
        for arg_id in args[1:]:
            try:
                if arg_id == str(update.effective_chat.id):
                    raise
                chat_context = await context.bot.get_chat(arg_id)
                self.database.update_chain_by_id(
                    update.effective_chat.id, arg_id)
                if chat_context.type in [ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL]:
                    result_message += f"👨‍👩‍👧‍👦 {chat_context.title} {arg_id}\n"
                elif chat_context.type in [ChatType.PRIVATE, ChatType.SENDER]:
                    result_message += f"👨 {chat_context.username} {arg_id}\n"
            except:
                result_message += f'❌ {arg_id}\n'

        await context.bot.send_message(chat_id=update.effective_chat.id, text=result_message)

    async def listchain(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chains = self.database.select_all_chain_by_id(
            update.effective_chat.id)
        result_message = f'[連鎖發話列表]\n{"" if len(chains) else "(暫無)"}'

        for chain in chains:
            chat_context = await context.bot.get_chat(chain)
            if chat_context.type in [ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL]:
                result_message += f"👨‍👩‍👧‍👦 {chat_context.title} {chain}\n"
            elif chat_context.type in [ChatType.PRIVATE, ChatType.SENDER]:
                result_message += f"👨 {chat_context.username} {chain}\n"
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=result_message)

    async def deletechain(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = update.message.text.split()
        if len(args) != 2:
            await context.bot.send_message(chat_id=update.effective_chat.id, text='參數錯誤')
            return
        if self.database.delete_chain_by_id(update.effective_chat.id, args[1]):
            await context.bot.send_message(chat_id=update.effective_chat.id, text='刪除成功')
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text='刪除失敗')

    async def wall(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = update.message.text[6:]
        chains = self.database.select_all_chain_by_id(
            update.effective_chat.id)
        for chain in chains:
            await context.bot.send_message(chat_id=chain, text=message)

    async def id(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(chat_id=update.effective_chat.id, text=update.effective_chat.id)

    def __init__(self):
        TGBOT_TOKEN = os.getenv("TGBOT_TOKEN", "TOKENISMISSING")
        self.app = ApplicationBuilder().token(TGBOT_TOKEN).build()
        self.database = Database()

        self.app.add_handler(CommandHandler('help', self.help))
        self.app.add_handler(CommandHandler('addchain', self.addchain))
        self.app.add_handler(CommandHandler('listchain', self.listchain))
        self.app.add_handler(CommandHandler('deletechain', self.deletechain))
        self.app.add_handler(CommandHandler('wall', self.wall))
        self.app.add_handler(CommandHandler('id', self.id))
        print(TGBOT_TOKEN)

    def run(self):
        self.app.run_polling()
        pass


if __name__ == "__main__":
    telegrambot = TelegramBot()
    telegrambot.run()
