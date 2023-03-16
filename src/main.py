import asyncio

from dotenv import get_key
from telebot import types as tgTypes
from telebot.async_telebot import AsyncTeleBot

import handlers


TOKEN = get_key('../.env', 'TOKEN')
API_KEY = get_key('../.env', 'API_KEY')
handler = handlers.API_handler(API_KEY, 5)
bot = AsyncTeleBot(TOKEN)


def create_recipe_markup(rcp_id: str) -> tgTypes.InlineKeyboardMarkup:
    full_recipe = tgTypes.InlineKeyboardButton(
        text = '🔖 Full recipe',
        callback_data = rcp_id
    )
    
    markup = tgTypes.InlineKeyboardMarkup(row_width=3)
    markup.add(full_recipe)

    return markup


@bot.callback_query_handler(func = lambda call: True)
async def get_full_recipe(call: tgTypes.CallbackQuery):
    recipe = await handler.get_by_id(call.data)
    ingredients = ''

    for i, ingr in enumerate(recipe['extendedIngredients'], start = 1):
        ingredients += f"{i}) {ingr['original']}\n"

    res = f"{recipe['title']}\n\n{recipe['instructions']}\n\nINGREDIENTS:\n{ingredients}"
    res = handler.remove_tags(res)

    try:
        await bot.edit_message_caption(
            caption = res,
            chat_id = call.message.chat.id,
            message_id = call.message.id
        )

    except Exception:
        await bot.send_message(
            text = res,
            chat_id = call.message.chat.id,
            reply_to_message_id = call.message.id
        )

@bot.message_handler(commands = ['start', 'help'])
async def start_bot(msg: tgTypes.Message):
    await bot.send_message(
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
async def tag_search(msg: tgTypes.BotCommand):
    recipes = await handler.get_by_tag(msg.text[1:])

    asyncio.gather(*[bot.send_photo(
            chat_id = msg.chat.id,
            photo = recipe['image'],
            caption = f"{recipe['title']}\n\nDone in {recipe['readyInMinutes']} minutes\nLikes: {recipe['aggregateLikes']}",
            reply_markup = create_recipe_markup(str(recipe['id']))
        ) for recipe in recipes]
    )

@bot.message_handler(commands = ['random'])
async def get_random(msg: tgTypes.BotCommand):
    recipe = await handler.get_random()

    veg = '✅' if recipe['vegetarian'] else '❌'
    markup = create_recipe_markup(str(recipe['id']))

    await bot.send_photo(
        chat_id = msg.chat.id,
        photo = recipe['image'],
        caption = f"{recipe['title']}\n\nVegetarian: {veg}\nDone in {recipe['readyInMinutes']} minutes\nLikes: {recipe['aggregateLikes']}",
        reply_markup = markup
    )

@bot.message_handler(func = lambda msg: True)
async def search_by_name(msg: tgTypes.Message):
    query = msg.text.lower()
    recipes = await handler.get_by_name(query)
    
    if recipes == []:
        await bot.send_message(
            chat_id = msg.chat.id,
            text = f'😕 No results for "{msg.text}"'
        )

    else:
        asyncio.gather(*[bot.send_photo(
                chat_id = msg.chat.id,
                photo = recipe['image'],
                caption = recipe['title'],
                reply_markup = create_recipe_markup(str(recipe['id']))
            ) for recipe in recipes]
        )

if __name__ == '__main__':
    print('Bot started!')
    asyncio.run(bot.infinity_polling())