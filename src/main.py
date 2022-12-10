import telebot
from dotenv import get_key
from telebot import types as tgTypes

import handlers

TOKEN = get_key('../.env', 'TOKEN')
API_KEY = get_key('../.env', 'API_KEY')
handler = handlers.API_handler(API_KEY, 5)
bot = telebot.TeleBot(TOKEN)

def create_recipe_markup(rcp_id: str) -> tgTypes.InlineKeyboardMarkup:
    full_recipe = tgTypes.InlineKeyboardButton(
        text = '🛈 more info',
        callback_data = rcp_id
    )
    markup = tgTypes.InlineKeyboardMarkup(row_width=3)
    markup.add(full_recipe)
    return markup

@bot.callback_query_handler(func = lambda call: True)
def get_full_recipe(call: tgTypes.CallbackQuery):
    recipe = handler.get_by_id(call.data)
    ingredients = ''

    for i, ingr in enumerate(recipe['extendedIngredients']):
        ingredients += f"{i+1}) {ingr['original']}\n"

    res = f"{recipe['title']}\n\n{recipe['instructions']}\n\nINGREDIENTS:\n{ingredients}"
    res = handler.remove_tags(res)

    try:
        bot.edit_message_caption(
            caption = res,
            chat_id = call.message.chat.id,
            message_id = call.message.id
        )

    except Exception:
        bot.send_message(
            text = res,
            chat_id = call.message.chat.id,
            reply_to_message_id = call.message.id
        )

@bot.message_handler(commands = ['start', 'help'])
def start_bot(msg: tgTypes.Message):
    bot.send_message(
        chat_id = msg.chat.id,
        text = 'Hello! To start searching for recipes just type any meal name you want, or use <b>special commands</b>',
        parse_mode = 'html'
    )

@bot.message_handler(
    commands = [
        'popular',
        'vegetarian',
        'dessert',
    ]
)
def tag_search(msg: tgTypes.BotCommand):
    recipes = handler.get_by_tag(msg.text[1:])

    for recipe in recipes:
        markup = create_recipe_markup(str(recipe['id']))

        bot.send_photo(
            chat_id = msg.chat.id,
            photo = recipe['image'],
            caption = f"{recipe['title']}\n\nDone in {recipe['readyInMinutes']} minutes\nLikes: {recipe['aggregateLikes']}",
            reply_markup = markup
        )

@bot.message_handler(commands = ['random'])
def get_random(msg: tgTypes.BotCommand):
    recipe = handler.get_random()

    veg = '✅' if recipe['vegetarian'] else '❌'
    markup = create_recipe_markup(str(recipe['id']))

    bot.send_photo(
        chat_id = msg.chat.id,
        photo = recipe['image'],
        caption = f"{recipe['title']}\n\nVegetarian: {veg}\nDone in {recipe['readyInMinutes']} minutes\nLikes: {recipe['aggregateLikes']}",
        reply_markup = markup
    )

@bot.message_handler(func = lambda msg: True)
def search_by_name(msg: tgTypes.Message):
    query = msg.text.lower()
    recipes = handler.get_by_name(query)

    for recipe in recipes:
        markup = create_recipe_markup(str(recipe['id']))

        bot.send_photo(
            chat_id = msg.chat.id,
            photo = recipe['image'],
            caption = recipe['title'],
            reply_markup = markup
        )

if __name__ == '__main__':
    print('Bot started!')
    bot.polling(none_stop = True)