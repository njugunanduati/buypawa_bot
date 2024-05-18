#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.
import asyncio
import environ
import logging
from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, filters,
                          ConversationHandler)
from paybill.payment import Payment
from pawa.ipay import Ipay
from database.db import Customer, Meter

# read variables for .env file
ENV = environ.Env()
environ.Env.read_env(".env")

TOKEN = ENV.str("TOKEN", "")

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

# Keyboard for the first time customer Add phone number
reply_keyboard_phone_number = [['Add Phone No.']]

# Keyboard for the first time customer Add meter
reply_keyboard_meter = [['Add Meter']]

# Keyboard for the first time customer
reply_keyboard_main = [['Select Meter', 'Enter Amount'],
                      ['Done']]
# select meter keyboard
reply_keyboard_select_meter = [[]]

markup_phone_number = ReplyKeyboardMarkup(reply_keyboard_phone_number, one_time_keyboard=True)
markup_meter = ReplyKeyboardMarkup(reply_keyboard_meter, one_time_keyboard=True)
markup_main = ReplyKeyboardMarkup(reply_keyboard_main, one_time_keyboard=True)


def start(update, context):
    user_data = update.message.from_user
    data = [user_data.username,
            user_data.first_name,
            user_data.last_name
            ]
    customer = Customer().get_customer(data)
    if customer:
        update.message.reply_text(
            'Welcome back {} to BuyPawa.'
            'Select an option to get started:'.format(user_data.first_name), reply_markup=markup_main)
    else:
        update.message.reply_text(
            'Welcome to BuyPawa. BuyPawa allows you to buy Kenya Power tokens easily and conveniently.'
            'No need to remember the pay-bill number and your meter number. You can also buy tokens for more '
            'than one meter at at a single buy.'
            'Select Add Phone No. option to get started:', reply_markup=markup_phone_number)

    return CHOOSING


def regular_choice(update, context):
    the_data = update.message.from_user
    text = update.message.text
    context.user_data['choice'] = text

    if text == 'Add Phone No.':
        message = 'Enter your Safaricom number in this format e.g 254722******:'
        update.message.reply_text(message.format(text.lower()))
        reply_type = TYPING_REPLY
        return reply_type

    if text == 'Add Meter':
        message = 'Enter your 11 digit Kenya Power meter number:'
        update.message.reply_text(message.format(text.lower()))
        reply_type = TYPING_REPLY
        return reply_type

    if text == 'Select Meter':
        print("user_data", the_data)
        data = [the_data.username,
                the_data.first_name,
                the_data.last_name
                ]
        customer = Customer().get_customer(data)
        data = [customer[0]]
        meter = Meter().get_meters(data)
        message = 'Choose a meter from the given list to buy Kenya Power Tokens:'
        reply_keyboard_select_meter[0] = meter
        markup_meters = ReplyKeyboardMarkup(reply_keyboard_select_meter, one_time_keyboard=True)
        update.message.reply_text(message, reply_markup=markup_meters)
        reply_type = TYPING_REPLY
        return reply_type

    if text == 'Enter Amount':
        message = 'Enter the amount you wish to spend:'
        update.message.reply_text(message.format(text.lower()))
        reply_type = TYPING_REPLY
        return reply_type

    if text == 'Done':
        return done(update, context)


def custom_choice(update, context):
    update.message.reply_text('Alright, please send me the category first, '
                              'for example "Most impressive skill"')

    return TYPING_CHOICE


def received_information(update, context):
    the_data = update.message.from_user
    user_data = context.user_data
    text = update.message.text
    category = user_data['choice']
    user_data[category] = text
    del user_data['choice']

    print("user_data", user_data)

    if 'Add Phone No.' in user_data:
        data = [the_data.username,
                the_data.first_name,
                the_data.last_name,
                user_data['Add Phone No.']
                ]
        Customer().add_customer(data)
        message = 'Phone Number added successfully. Select Add Meter option to add your meter:'
        del user_data['Add Phone No.']
        update.message.reply_text(message, reply_markup=markup_meter)
        return CHOOSING

    if 'Add Meter' in user_data:
        data = [the_data.username,
                the_data.first_name,
                the_data.last_name
                ]
        customer = Customer().get_customer(data)
        print("customer", customer)
        data = [customer[0], user_data['Add Meter']]
        Meter().add_meter(data)
        message = 'Meter added successfully. Choose the Select Meter option to proceed to buy Kenya Power Tokens:'
        del user_data['Add Meter']
        update.message.reply_text(message, reply_markup=markup_main)
        return CHOOSING

    if 'Select Meter' in user_data and 'Enter Amount' not in user_data:
        message = 'Meter selected. Choose a enter amount option:'
        update.message.reply_text(message, reply_markup=markup_main)
        return CHOOSING

    if 'Enter Amount' in user_data and 'Enter Amount' in user_data:
        print("the_data", the_data)
        data = [the_data.username,
                the_data.first_name,
                the_data.last_name
                ]
        customer = Customer().get_customer(data)
        print("user_data", user_data)
        message = 'Check your phone to complete the m-pesa payment. Select Done to get token:'
        pay = Payment().online_payment(customer[4], amount)
        print("payment", pay)
        update.message.reply_text(message, reply_markup=markup_main)
        return CHOOSING


def done(update, context):
    user_data = context.user_data
    if 'choice' in user_data:
        del user_data['choice']
    print("data for token", user_data)

    meter = user_data['Select Meter']
    amount = user_data['Enter Amount']

    buy_token = Ipay(meter, int(amount))
    token_data = buy_token.get_token()

    print("----", token_data)
    token = token_data['token']
    units = token_data['units']

    message = 'Token: {}  Units: {} Until next time. GoodBye!'.format(token, units)

    update.message.reply_text(message)

    user_data.clear()
    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    print("the error", context.error)
    logger.warning('Update "%s" caused error "%s"', update, context.error)


async def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            CHOOSING: [MessageHandler(filters.regex('^(Add Meter|Add Phone No.|Add Meter'
                                                    '|Enter Amount|Select Meter|Done)$'),
                                      regular_choice),
                       # MessageHandler(Filters.regex('^(Select Meter)$'),
                       #                custom_choice)
                       ],

            TYPING_CHOICE: [MessageHandler(filters.text,
                                           regular_choice)
                            ],

            TYPING_REPLY: [MessageHandler(filters.text,
                                          received_information),
                           ],
        },

        fallbacks=[MessageHandler(filters.regex('^Done$'), done)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    asyncio.run(main())
