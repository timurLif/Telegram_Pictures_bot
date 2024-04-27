# Импортируем необходимые классы.
import os
import logging
from telegram.ext import Application, MessageHandler, filters, CallbackContext

from telegram.ext import CommandHandler
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove

from fus_br_api_test import gen_pic

# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

activity_style = False
current_user_input_style = 'default'
activity_aspect_ratio = False
current_user_input_aspect_ratio = '1:1'
activity_generate_picture = False

# Напишем соответствующие функции.
async def help(update, context):
    await update.message.reply_text(
        "Я бот генерирущий картинки по запросу.\nВведите /start чтобы начать!\n/style - выбор стиля\n/aspect_ratio - выбор соотношения сторон\n/generate_picture - генерация картинки"
    )
    
async def start(update, context):
    user = update.effective_user
    await update.message.reply_text(
        rf"Привет! Я эхо-бот. Напишите мне что-нибудь, и я пришлю это назад!",
        reply_markup=markup
    )

async def current_user_message(update, context):
    global cur_user_mes
    cur_user_mes = update.message.text
    await save_selected_style(update, context, cur_user_mes)
    await save_selected_aspect_ratio(update, context, cur_user_mes)
    await selected_generate_picture(update, context, cur_user_mes)

async def style(update, context):
    if activity_aspect_ratio:
        await update.message.reply_text(
            f"Сначала выберите соотношение сторон:"
        )
    elif activity_generate_picture:
        await update.message.reply_text(
            f"Сначала сгенерируйте картинку:"
        )
    else:
        global activity_style
        activity_style = True

        await update.message.reply_text(
            f"Выберите стиль из предложенных вариантов:",
            reply_markup=markup_style
        )

async def save_selected_style(update, context, cur_user_mes):
    global activity_style
    global current_user_input_style
    if activity_style:
        user_input_style = cur_user_mes.lower()  # Convert to lowercase
        styles_list = ['abstract', 'uhd', 'anime', 'default']
        
        if user_input_style in styles_list:
            current_user_input_style = user_input_style
            activity_style = False

            await update.message.reply_text(f"Выбран стиль: {current_user_input_style}", reply_markup=markup)
        else:
            await update.message.reply_text("Выбранный стиль отсутствует в списке. Попробуйте еще раз.")

async def aspect_ratio(update, context):
    if activity_style:
        await update.message.reply_text(
            f"Сначала выберите стиль:"
        )
    elif activity_generate_picture:
        await update.message.reply_text(
            f"Сначала сгенерируйте картинку:"
        )
    else:
        global activity_aspect_ratio
        activity_aspect_ratio = True
        await update.message.reply_text(
            f"Выберите соотношение сторон из предложенных вариантов:",
            reply_markup=markup_aspect_ratio
        )

async def save_selected_aspect_ratio(update, context, cur_user_mes):
    global activity_aspect_ratio
    global current_user_input_aspect_ratio
    if activity_aspect_ratio:
        user_input_aspect_ratio = cur_user_mes
        aspect_ratio_list = ['9:16', '16:9', '2:3', '3:2', '1:1']

        if user_input_aspect_ratio in aspect_ratio_list:
            current_user_input_aspect_ratio = user_input_aspect_ratio
            activity_aspect_ratio = False

            await update.message.reply_text(f"Выбрано соотношение сторон: {current_user_input_aspect_ratio}", reply_markup=markup)
        else:
            await update.message.reply_text("Выбранное соотношение сторон отсутствует в списке. Попробуйте еще раз.")

async def close_keyboard(update, context):
    await update.message.reply_text(
        "Ok",
        reply_markup=ReplyKeyboardRemove()
    )

async def generate_picture(update, context: CallbackContext):
    if activity_aspect_ratio == False and activity_style == False:
        global activity_generate_picture
        activity_generate_picture = True
        await update.message.reply_text(f"Введите какую картинку хотите получить:")

async def selected_generate_picture(update, context: CallbackContext, cur_user_mes):
    global activity_generate_picture
    if activity_generate_picture:
        activity_generate_picture = False
        st_dict = {'abstract': 0, 'uhd': 1, 'anime': 2, 'default': 3}
        asp_rt = {'9:16': (480, 854), '16:9': (854, 480), '2:3': (640, 960), '3:2': (960, 640), '1:1': (1024, 1024)}

        await update.message.reply_text(f"Подождите пока генерируется картинка, может занять от 5 до 20 секунд.")

        # Путь к изображению
        image_data = gen_pic(cur_user_mes, st=st_dict[current_user_input_style],
                             wh=asp_rt[current_user_input_aspect_ratio][0],
                             ht=asp_rt[current_user_input_aspect_ratio][1])


        with open("image.jpg", "wb") as file:
            file.write(image_data)

        image_path = 'image.jpg'
        # Открываем изображение как бинарный файл
        with open(image_path, 'rb') as image_file:
            # Отправляем изображение через бота
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=image_file)
        
        os.remove("image.jpg")


reply_keyboard = [['/style', '/aspect_ratio'],
                  ['/generate_picture']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)

reply_keyboard_style = [['Abstract', 'UHD'],
                        ['Anime', 'Default']]
markup_style = ReplyKeyboardMarkup(reply_keyboard_style, one_time_keyboard=False)

reply_keyboard_aspect_ratio = [['9:16', '16:9'],
                               ['2:3', '3:2'],
                               ['1:1']]
markup_aspect_ratio = ReplyKeyboardMarkup(reply_keyboard_aspect_ratio, one_time_keyboard=False)


def main():
    application = Application.builder().token("7102151340:AAGO2Un1eDrq4-vtAJr0OjYO004sUwSpcsw").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("style", style))
    application.add_handler(CommandHandler("aspect_ratio", aspect_ratio))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, current_user_message))
    application.add_handler(CommandHandler("generate_picture", generate_picture))
    application.add_handler(CommandHandler("close", close_keyboard))

    application.run_polling()


if __name__ == '__main__':
    main()
