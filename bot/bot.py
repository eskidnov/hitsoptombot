# -*- coding: utf-8 -*-

import telebot
import config
import queue
import utils


bot = telebot.TeleBot(config.token)
# Меню магазина
menu = (
    'Каталог',
    'Корзина',
)
menu_keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
menu_keyboard.add(*(telebot.types.KeyboardButton(item) for item in menu))
# Каталог
catalog = {
    'Для дома и дачи'   :   [],
    'Детские товары'    :   [],
    'Зимние товары'     :   {
                                'Снежколеп'         :   ['35 см', '25 см'],
                                'Тюбинг-ватрушка'   :   ['100 см', '110 см', '120 см', '85 см', '95 см'],
                                'Диско-лампы'       :   ['Диско-лампа'],
                                'Перчатки'          :   ['IGrove', 'Для сенсорных'],
                                'Санки-коляски'     :   ['"Ника"'],
                                'Игрушки'           :   ['Интерактивный пингвинчик'],
                            },
    'Летние товары' :   [],
    'Косметика' :   {'Наборы'   :   [],
                     'Тушь'     :   [],
                     'Помады'   :   [],
                     'Тени'     :   [],
                     'Маски'    :   [],
                     'Скрабы'   :   [],
                     'Педикюр'  :   [],
                     },
    'Новые тренды'  :   [],
}
image = 'https://pp.userapi.com/c845321/v845321339/ecd2/zJeXPZUZqoI.jpg'

products = queue.Queue(7)


@bot.message_handler(commands=['start'])
def start(message):
    utils.del_user_basket(message.from_user.id)
    utils.set_basket(message.from_user.id)
    bot.send_message(message.chat.id, 'Добро пожаловать!', reply_markup=menu_keyboard)


@bot.message_handler(func=lambda item: item.text == menu[0], content_types=['text'])
def catalog_1(message):
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    #TODO обернуть в hash()
    keyboard.add(*(telebot.types.InlineKeyboardButton(text=item, callback_data=item)
                 for item in catalog.keys()))
    bot.send_message(message.chat.id, 'Выберите категорию', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda query: query.data in catalog.keys())
def catalog_2(query):
    bot.answer_callback_query(query.id)
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    cat = query.data
    try:
        bot.delete_message(query.message.chat.id, query.message.message_id)
    except:
        bot.send_message(query.message.chat.id, 'Вас давно не было!')
    # try:
        # for item in catalog[cat].keys():
        #     products.put(item)
        # product = products.get()
    if catalog[cat]:
        for item in catalog[cat]:
            keyboard.add(telebot.types.InlineKeyboardButton(text=item, callback_data=cat + '|' + item))
        keyboard.add(telebot.types.InlineKeyboardButton(text='Назад', callback_data='Назад'))
        text = cat
    else:
        keyboard.add(telebot.types.InlineKeyboardButton(text='Назад', callback_data='Назад'))
        text = 'Зайдите попозже'
    bot.send_message(query.message.chat.id, text, reply_markup=keyboard)
        # keyboard.add(telebot.types.InlineKeyboardButton(text='В корзину', callback_data=product+'|'+'В корзину'))
        # keyboard.row(telebot.types.InlineKeyboardButton(text='<-', callback_data=cat+'<-'),
        #              telebot.types.InlineKeyboardButton(text='->', callback_data=cat+'->'))
        # keyboard.add(telebot.types.InlineKeyboardButton(text='Назад', callback_data='Назад'))
        # try:
        #     print(product)
        #     bot.send_photo(query.message.chat.id, image, product, reply_markup=keyboard)
        # except:
        #     bot.send_message(query.message.chat.id, 'Что-то пошло не так...')
        # products.put(product)
    # except:
    #     keyboard.add(telebot.types.InlineKeyboardButton(text='Назад', callback_data='Назад'))
    #     bot.send_message(query.message.chat.id, 'Заходите попозже', reply_markup=keyboard)


def check_subcat(data):
    try:
        cat, subcat = data.split('|')
        if catalog[cat][subcat]:
            pass
        return True
    except:
        return False


@bot.callback_query_handler(func=lambda query: check_subcat(query.data))
def catalog_3(query):
    bot.answer_callback_query(query.id)
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    cat, subcat = query.data.split('|')
    print(cat, subcat)
    while not products.empty():
        products.get()
    try:
        bot.delete_message(query.message.chat.id, query.message.message_id)
    except:
        bot.send_message(query.message.chat.id, 'Вас давно не было!')
    try:
        for item in catalog[cat][subcat]:
            products.put(item)
        if products.empty():
            raise Exception
        else:
            product = products.get()
        keyboard.add(telebot.types.InlineKeyboardButton(text='В корзину', callback_data=product+'|'+'В корзину'))
        keyboard.row(telebot.types.InlineKeyboardButton(text='<-', callback_data=cat+'|'+subcat+'<-'),
                     telebot.types.InlineKeyboardButton(text='->', callback_data=cat+'|'+subcat+'->'))
        keyboard.add(telebot.types.InlineKeyboardButton(text='Назад', callback_data=cat+'|Назад'))
        try:
            bot.send_photo(query.message.chat.id, image, product, reply_markup=keyboard)
        except:
            bot.send_message(query.message.chat.id, 'Что-то пошло не так...')
        products.put(product)
    except:
        keyboard.add(telebot.types.InlineKeyboardButton(text='Назад', callback_data=cat+'|Назад'))
        bot.send_message(query.message.chat.id, 'Заходите попозже', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda query: query.data[-5:] == 'Назад' and query.data != 'Назад')
def back_2(query):
    bot.answer_callback_query(query.id)
    query.data = query.data[:-6]
    catalog_2(query)


@bot.callback_query_handler(func=lambda query: query.data[-2:] == '<-')
def left(query):
    bot.answer_callback_query(query.id)
    cat, subcat = query.data[:-2].split('|')
    product = products.get()
    try:
        bot.delete_message(query.message.chat.id, query.message.message_id)
    except:
        bot.send_message(query.message.chat.id, 'Вас давно не было!')
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(telebot.types.InlineKeyboardButton(text='В корзину', callback_data=product+'|'+'В корзину'))
    keyboard.row(telebot.types.InlineKeyboardButton(text='<-', callback_data=cat+'|'+subcat+'<-'),
                 telebot.types.InlineKeyboardButton(text='->', callback_data=cat+'|'+subcat+'->'))
    keyboard.add(telebot.types.InlineKeyboardButton(text='Назад', callback_data=cat+'|Назад'))
    try:
        bot.send_photo(query.message.chat.id, image, product, reply_markup=keyboard)
    except:
        bot.send_message(query.message.chat.id, 'Что-то пошло не так...')
    products.put(product)


@bot.callback_query_handler(func=lambda query: query.data[-2:] == '->')
def right(query):
    bot.answer_callback_query(query.id)
    cat, subcat = query.data[:-2].split('|')
    for i in range(products.qsize()-2):
        product = products.get()
        products.put(product)
    product = products.get()
    try:
        bot.delete_message(query.message.chat.id, query.message.message_id)
    except:
        bot.send_message(query.message.chat.id, 'Вас давно не было!')
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(telebot.types.InlineKeyboardButton(text='В корзину', callback_data=product+'|'+'В корзину'))
    keyboard.row(telebot.types.InlineKeyboardButton(text='<-', callback_data=cat+'|'+subcat+'<-'),
                 telebot.types.InlineKeyboardButton(text='->', callback_data=cat+'|'+subcat+'->'))
    keyboard.add(telebot.types.InlineKeyboardButton(text='Назад', callback_data=cat+'|Назад'))
    try:
        bot.send_photo(query.message.chat.id, image, product, reply_markup=keyboard)
    except:
        bot.send_message(query.message.chat.id, 'Что-то пошло не так...')
    products.put(product)


@bot.callback_query_handler(func=lambda query: 'В корзину' in query.data)
def to_basket(query):
    product = query.data.split('|')[0]
    if not utils.get_basket(query.from_user.id):
        utils.set_basket(query.from_user.id)
    utils.add_to_basket(query.from_user.id, product)
    bot.answer_callback_query(query.id, 'Добавлено в корзину!')


@bot.callback_query_handler(func=lambda query: query.data == 'Назад')
def back(query):
    bot.answer_callback_query(query.id)
    try:
        bot.delete_message(query.message.chat.id, query.message.message_id)
    except:
        bot.send_message(query.message.chat.id, 'Вас давно не было!')
    catalog_1(query.message)


@bot.message_handler(func=lambda item: item.text == menu[1], content_types=['text'])
def basket(message):
    user_id = message.from_user.id
    user_basket = utils.get_basket(user_id)

    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    confirm_button = telebot.types.KeyboardButton('Подтвердить заказ')
    clear_button = telebot.types.KeyboardButton('Очистить')
    back_button = telebot.types.KeyboardButton('Назад')
    keyboard.add(confirm_button, clear_button, back_button)
    bot.send_message(message.chat.id, '------------------\n| Корзина |\n------------------', reply_markup=keyboard)
    if user_basket:
        for item in user_basket:
            keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
            keyboard.row(
                telebot.types.InlineKeyboardButton(text='Меньше', callback_data=item+'less'),
                telebot.types.InlineKeyboardButton(text=str(utils.item_amount(user_id, item)), callback_data=item+'amount'),
                telebot.types.InlineKeyboardButton(text='Больше', callback_data=item+'more')
            )
            keyboard.add(telebot.types.InlineKeyboardButton(text='Удалить', callback_data=item+'del'))
            amount = utils.item_amount(user_id, item)
            price = 1400
            res = ''
            if 1 <= amount and amount < 2:
                res = str(price) + ' руб.\n'
            if 2 <= amount and amount < 4:
                res = str(price * 0.99) + ' руб.\n'
            if 4 <= amount and amount < 6:
                res = str(price * 0.98) + ' руб.\n'
            if 6 <= amount and amount < 8:
                res = str(price * 0.97) + ' руб.\n'
            if 8 <= amount and amount:
                res = str(price * 0.96) + ' руб.\n'
            bot.send_photo(message.chat.id, image, item+'\nЦена: '+res, reply_markup=keyboard)
    else:
        bot.send_message(chat_id=message.chat.id, text='Корзина пуста!', reply_markup=menu_keyboard)


@bot.callback_query_handler(func=lambda query: 'less' in query.data)
def less(query):
    bot.answer_callback_query(query.id)
    item = query.data[:-4]
    user_id = query.from_user.id

    utils.remove_amount(user_id, item)
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    keyboard.row(
        telebot.types.InlineKeyboardButton(text='Меньше', callback_data=item + 'less'),
        telebot.types.InlineKeyboardButton(text=str(utils.item_amount(user_id, item)),
                                           callback_data=item + 'amount'),
        telebot.types.InlineKeyboardButton(text='Больше', callback_data=item + 'more')
    )
    keyboard.add(telebot.types.InlineKeyboardButton(text='Удалить', callback_data=item + 'del'))
    amount = utils.item_amount(user_id, item)
    price = 1400
    res = ''
    if 1 <= amount and amount < 2:
        res = str(price) + ' руб.\n'
    if 2 <= amount and amount < 4:
        res = str(price * 0.99) + ' руб.\n'
    if 4 <= amount and amount < 6:
        res = str(price * 0.98) + ' руб.\n'
    if 6 <= amount and amount < 8:
        res = str(price * 0.97) + ' руб.\n'
    if 8 <= amount and amount:
        res = str(price * 0.96) + ' руб.\n'
    try:
        bot.edit_message_caption(item+'\nЦена: '+res, query.message.chat.id, query.message.message_id, reply_markup=keyboard)
    except:
        if utils.item_amount(user_id, item) > 1:
            bot.send_message(query.message.chat.id, 'Вас давно не было!')


@bot.callback_query_handler(func=lambda query: 'more' in query.data)
def more(query):
    bot.answer_callback_query(query.id)
    item = query.data[:-4]
    user_id = query.from_user.id

    utils.add_to_basket(user_id, item)
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    keyboard.row(
        telebot.types.InlineKeyboardButton(text='Меньше', callback_data=item + 'less'),
        telebot.types.InlineKeyboardButton(text=str(utils.item_amount(user_id, item)),
                                           callback_data='amount'),
        telebot.types.InlineKeyboardButton(text='Больше', callback_data=item + 'more')
    )
    keyboard.add(telebot.types.InlineKeyboardButton(text='Удалить', callback_data=item + 'del'))
    amount = utils.item_amount(user_id, item)
    price = 1400
    res = ''
    if 1 <= amount and amount < 2:
        res = str(price) + ' руб.\n'
    if 2 <= amount and amount < 4:
        res = str(price * 0.99) + ' руб.\n'
    if 4 <= amount and amount < 6:
        res = str(price * 0.98) + ' руб.\n'
    if 6 <= amount and amount < 8:
        res = str(price * 0.97) + ' руб.\n'
    if 8 <= amount and amount:
        res = str(price * 0.96) + ' руб.\n'
    try:
        bot.edit_message_caption(item+'\nЦена: '+res, query.message.chat.id, query.message.message_id, reply_markup=keyboard)
    except:
        if utils.item_amount(user_id, item) > 1:
            bot.send_message(query.message.chat.id, 'Вас давно не было!')


@bot.callback_query_handler(func=lambda query: 'amount' == query.data)
def num(query):
    bot.answer_callback_query(query.id)


@bot.callback_query_handler(func=lambda query: 'del' in query.data)
def more(query):
    bot.answer_callback_query(query.id)
    item = query.data[:-3]
    user_id = query.from_user.id

    try:
        utils.del_from_basket(user_id, item)
        bot.delete_message(query.message.chat.id, query.message.message_id)
    except:
        bot.send_message(query.message.chat.id, 'Вас давно не было!')


@bot.message_handler(func=lambda item: item.text == 'Очистить', content_types=['text'])
def clear_basket(message):
    user_id = message.from_user.id
    user_basket = utils.get_basket(user_id)

    for item in user_basket:
        utils.del_from_basket(user_id, item)

    bot.send_message(message.chat.id, 'Корзина пуста!', menu_keyboard)


@bot.message_handler(func=lambda item: item.text == 'Назад', content_types=['text'])
def back_basket(message):
    bot.send_message(message.chat.id, 'Добро пожаловать!', reply_markup=menu_keyboard)


# @bot.callback_query_handler(func=lambda query: query.data == 'Корзина')
# def back(query):
#     bot.answer_callback_query(query.id)
#     try:
#         bot.delete_message(query.message.chat.id, query.message.message_id)
#     except:
#         bot.send_message(query.message.chat.id, 'Вас давно не было!')
#     basket(query.message)


@bot.message_handler(func=lambda item: item.text == 'Подтвердить заказ', content_types=['text'])
def check_basket(message):
    user_id = message.from_user.id
    user_basket = utils.get_basket(user_id)

    bot.send_message(message.chat.id, 'Подтверждение заказа', reply_markup=menu_keyboard)
    if user_basket:
        res = ''
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        pay_button = telebot.types.InlineKeyboardButton(text='Оплатить', pay=True)
        # back_button = telebot.types.InlineKeyboardButton(text='Назад', callback_data='Корзина')
        keyboard.add(pay_button)
        price = 1400
        res = ''
        pay = 0
        for item in user_basket:
            amount = utils.item_amount(user_id, item)
            if 1 <= amount and amount  < 2:
                res += item + ': ' + str(amount) + ' * ' + str(price) + ' руб.\n'
                pay += amount * price
            if 2 <= amount and amount  < 4:
                res += item + ': ' + str(amount) + ' * ' + str(price * 0.99) + ' руб.\n'
                pay += amount * price * 0.99
            if 4 <= amount and amount  < 6:
                res += item + ': ' + str(amount) + ' * ' + str(price * 0.98) + ' руб.\n'
                pay += amount * price * 0.98
            if 6 <= amount and amount  < 8:
                res += item + ': ' + str(amount) + ' * ' + str(price * 0.97) + ' руб.\n'
                pay += amount * price * 0.97
            if 8 <= amount and amount:
                res += item + ': ' + str(amount) + ' * ' + str(price * 0.96) + ' руб.\n'
                pay += amount * price * 0.96
        # bot.send_message(message.chat.id, res, parse_mode='Markdown', reply_markup=keyboard)

        bot.send_invoice(chat_id=message.chat.id,
                         title='Ваш заказ',
                         description=res,
                         invoice_payload='invoice',
                         provider_token=config.provider_token,
                         start_parameter='invoice',
                         currency='rub',
                         prices=[telebot.types.LabeledPrice(label='Ваш заказ', amount=int(pay)*100)],
                         need_name=True,
                         need_email=True,
                         need_phone_number=True,
                         need_shipping_address=True,
                         is_flexible=True,
                         reply_markup=keyboard)
    else:
        bot.send_message(chat_id=message.chat.id, text='Корзина пуста!')


def set_shipping_option(id, title, *price):
    shipping_option = telebot.types.ShippingOption(id=id, title=title)
    shipping_option.add_price(*price)
    return shipping_option


@bot.shipping_query_handler(func=lambda query: True)
def shipping(shipping_query):
    bot.answer_shipping_query(shipping_query_id=shipping_query.id,
                              ok=True,
                              shipping_options=[set_shipping_option('1', 'Тест', telebot.types.LabeledPrice('Доставка', 100))],
                              error_message='error')


@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query_id=pre_checkout_query.id,
                                  ok=True,
                                  error_message='error')


@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    bot.send_message(chat_id=message.chat.id,
                     text=config.successful_payment.format(message.successful_payment.total_amount / 100,
                                                            message.successful_payment.currency),
                     parse_mode='Markdown')

    utils.del_user_basket(message.from_user.id)


if __name__ == '__main__':
    bot.polling(none_stop=True)