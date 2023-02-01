from telegram.ext import ConversationHandler
from skimage.transform import resize
from skimage.io import imread, imsave


def image_resize(update, context):
    chat_id = update.effective_chat.id

    try:
        resolution = float(update.effective_message.text.replace(
            ',', '.'))  # fix to accept float numbers with comma
    except ValueError:
        exception_value(update, context)  # fix for values like 202,2.4

    if resolution > 4900 or resolution < 10:  # skimage doesn't work good outside this span
        exception_value(update, context)
        return

    resized_image = resize(
        imread('temp.jpg'),
        (resolution, context.user_data['ratio'] * resolution))
    imsave('output.jpg', resized_image)

    context.bot.send_document(chat_id=chat_id,
                              document=open('output.jpg', 'rb'))
    context.bot.send_message(
        chat_id=chat_id,
        text=
        f'Your image is ready! Thank you for using the bot. Please enter "/start" to use the bot again.'
    )

    return ConversationHandler.END


def exception_value(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=
        'Error! Please enter the desired vertical dimesion for your resized image (from 10 to 4900)'
    )