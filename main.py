# This bot is currently designed only to resize images
# Will probably be updated to cover more tasks

import os
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler
from telegram.ext import Filters
from telegram import ReplyKeyboardMarkup
from skimage.transform import resize
from skimage.io import imread, imsave

SECRET = os.environ[
  'token']  #pushed from replit, so the telegram bot API token is represented this way
UPLOAD, CHOOSE, WORKING_RESIZE = range(
  3)  #initiate dialog states for ConversationHandler


def start(update, context):
  context.bot.send_message(chat_id=update.effective_chat.id,
                           text=f"Send me exactly one image as an attachment.")
  return UPLOAD


#function receives image, counts its w/h ratio and offers options to modify image (currently 1 option)
def uploader(update, context):
  image = update.effective_message.effective_attachment.thumb
  ratio = image.width / image.height
  context.user_data['ratio'] = ratio  #store image dimensions ratio

  with open("temp.jpg", 'wb') as f:  #upload image to file
    context.bot.get_file(update.message.document).download(out=f)

  custom_keyboard(update, context, f"Choose an option:")
  return CHOOSE


def option_chooser(update, context):
  if update.effective_message.text == '/change_size':
    context.bot.send_message(
      chat_id=update.effective_chat.id,
      text=
      'You chose the size change option. Please enter the vertical dimension for your resized image (from 10 to 4900)'
    )
    return WORKING_RESIZE

  #new features can be added here

  else:
    custom_keyboard(
      update, context,
      f"Something went wrong! Please choose one of the options:")


def more_photos_prohibited(
    update, context):  #a fix in case more than 1 photo is uploaded
  context.bot.send_message(
    chat_id=update.effective_chat.id,
    text=
    "Sorry, I currently can't handle more than 1 image at a time. Only your first image will be processed."
  )


def image_resize(update, context):  #this function resizes images
  chat_id = update.effective_chat.id

  try:
    resolution = float(update.effective_message.text.replace(
      ',', '.'))  #fix to accept float numbers with comma
  except ValueError:
    exception_value(update, context)  #fix for values like 202,2.4

  if resolution > 4900 or resolution < 10:  #skimage doesn't work good outside this span
    exception_value(update, context)
    return

  resized_image = resize(imread('temp.jpg'),
                         (resolution, context.user_data['ratio'] * resolution))
  imsave('output.jpg', resized_image)

  context.bot.send_document(chat_id=chat_id, document=open('output.jpg', 'rb'))
  context.bot.send_message(
    chat_id=chat_id,
    text=
    f'Your image is ready! Thank you for using the bot. Please enter "/start" to use the bot again.'
  )

  return ConversationHandler.END


def exception(update, context):  #this bot can only work with attachments
  context.bot.send_message(
    chat_id=update.effective_chat.id,
    text='Error. Please try to upload your image as an attachment.')


def exception_value(update, context):
  context.bot.send_message(
    chat_id=update.effective_chat.id,
    text=
    'Error! Please enter the desired vertical dimesion for your resized image (from 10 to 4900)'
  )


def greeting_message(update, context):
  context.bot.send_message(chat_id=update.effective_chat.id,
                           text='Please enter /start to begin.')


def custom_keyboard(update, context, input):
  chat_id = update.effective_chat.id
  options = ['/change_size']  #more options to come
  keyboard = ReplyKeyboardMarkup.from_column(options,
                                             one_time_keyboard=True,
                                             resize_keyboard=True)
  context.bot.send_message(chat_id=chat_id, text=input, reply_markup=keyboard)


updater = Updater(SECRET)

con_han = ConversationHandler(
  entry_points=[CommandHandler('start', start)],
  states={
    UPLOAD: [
      MessageHandler(Filters.document.category("image"), uploader),
      MessageHandler(~Filters.document.category("image"), exception)
    ],
    CHOOSE: [
      MessageHandler(Filters.all & ~Filters.document.category("image"),
                     option_chooser),
      MessageHandler(Filters.document.category("image"),
                     more_photos_prohibited)
    ],
    WORKING_RESIZE: [
      MessageHandler(Filters.regex('^\d+|\.$|\,'), image_resize),
      MessageHandler(~Filters.regex('^\d+$'), exception_value)
    ]
  },
  fallbacks=[CommandHandler('start', start)],
  allow_reentry=True)
#proper fallbacks can be added, but there's currently no point for that

updater.dispatcher.add_handler(con_han)
updater.dispatcher.add_handler(MessageHandler(Filters.all, greeting_message))

updater.start_polling()

#Comments:
'''
1) '^\d+|\.$|\,' is a string, containing 1+ numbers (d+) and may contain numbers + '.' or numbers + ','. ^ and $ mean    the beginning and the end of word


2) updater.dispatcher.add_handler(MessageHandler(Filters.regex('\-\d+|0'), exception_value)) 
   is another option to check for zero and negative numbers 

3) a way to return a photo sent by user via link:
    photo = update.effective_message.effective_attachment.file_id
    chat_id = update.effective_chat.id
    context.bot.send_document(chat_id = chat_id, document = photo)
'''
