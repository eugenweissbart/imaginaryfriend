import logging

from telegram.ext import MessageHandler as ParentHandler, Filters

from src.domain.message import Message
from src.entity.chat import Chat


class MessageHandler(ParentHandler):
    def __init__(self, message_sender, data_learner, reply_generator):
        super(MessageHandler, self).__init__(
            Filters.text | Filters.sticker,
            self.handle)

        self.message_sender = message_sender
        self.data_learner = data_learner
        self.reply_generator = reply_generator

    def handle(self, bot, update):
        chat = Chat.get_chat(update.message)
        message = Message(chat=chat, message=update.message)

        if message.has_text():
            logging.debug("[Chat %s %s bare_text] %s" %
                          (message.chat.chat_type,
                           message.chat.telegram_id,
                           message.text))

        if message.has_text() and not message.is_editing():
            return self.__process_message(message)
        elif message.is_sticker():
            return self.__process_sticker(message)

    def __process_message(self, message):
        self.data_learner.learn(message)

        if message.has_anchors() \
                or message.is_private() \
                or message.is_reply_to_bot() \
                or message.is_random_answer():
            reply = self.reply_generator.generate(message)
            if reply != '':
                self.message_sender.answer(message, reply)

    def __process_sticker(self, message):
        if message.has_anchors() \
                or message.is_private() \
                or message.is_reply_to_bot() \
                or message.is_random_answer():

            self.message_sender.send_sticker(message, "BQADAgADSAIAAkcGQwU-G-9SZUDTWAI")
