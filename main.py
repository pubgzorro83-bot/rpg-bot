import telebot
import random
import time

TOKEN = "8845697358:AAGHC80gXtHoQbFvu6bkxPtF9zVAN_pVKsc"
bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")

players = {}
last_farm_time = {}
last_mine_time = {}

def get_p(user):
    uid = user.id
    name = user.first_name or "Игрок"
    username = user.username or ""
    
    if uid not in players:
        players[uid] = {
            "name": name,
            "username": username,
            "gold": 100,
            "onigiri": 1,
            "hp": 100,
            "max_hp": 100,
            "lvl": 1,
            "xp": 0,
            "weapon": "Ржавый меч",
            "armor": "Тканевая одежда"
        }
    else:
        players[uid]["name"] = name
        players[uid]["username"] = username
    return players[uid]

def get_markup(shop=False):
    markup = telebot.types.InlineKeyboardMarkup()
    if shop:
        markup.row(
            telebot.types.InlineKeyboardButton("🍙 Онигири (500г)", callback_data="buy_onigiri"),
            telebot.types.InlineKeyboardButton("🧪 Зелье (3000г)", callback_data="buy_potion")
        )
        markup.row(
            telebot.types.InlineKeyboardButton("⚔️ Меч (6000г)", callback_data="buy_sword"),
            telebot.types.InlineKeyboardButton("🛡 Броня (12000г)", callback_data="buy_armor")
        )
        markup.row(telebot.types.InlineKeyboardButton("🔙 В главное меню", callback_data="menu"))
    else:
        markup.row(
            telebot.types.InlineKeyboardButton("🌾 Фарм", callback_data="farm"),
            telebot.types.InlineKeyboardButton("⛏ Шахта", callback_data="mine")
        )
        markup.row(
            telebot.types.InlineKeyboardButton("⚔️ Данж", callback_data="dungeon"),
            telebot.types.InlineKeyboardButton("🛒 Магазин", callback_data="shop")
        )
        markup.row(
            telebot.types.InlineKeyboardButton("👤 Профиль", callback_data="profile"),
            telebot.types.InlineKeyboardButton("🏆 Топ", callback_data="top")
        )
        markup.row(
            telebot.types.InlineKeyboardButton("🍙 Поесть", callback_data="eat"),
            telebot.types.InlineKeyboardButton("❓ Помощь", callback_data="help")
        )
    return markup

def send_main(call_or_message, text, shop=False):
    user = call_or_message.from_user
    tag = f"👤 **@{user.username}**" if user.username else f"👤 **{user.first_name}**"
    full_text = f"{tag}, {text}"
    
    chat_id = call_or_message.message.chat.id if hasattr(call_or_message, "message") else call_or_message.chat.id
    bot.send_message(chat_id, full_text, reply_markup=get_markup(shop))

@bot.message_handler(commands=['start', 'menu'])
def start_cmd(message):
    get_p(message.from_user)
    send_main(message, "Добро пожаловать в Хардкорную RPG! Выбирай действие кнопками ниже:")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user = call.from_user
    uid = user.id
    p = get_p(user)
    data = call.data
    cid = call.message.chat.id

    try:
        bot.answer_callback_query(call.id)
    except:
        pass

    if data == "menu":
        send_main(call, "Главное меню:")
    elif data == "help":
        send_main(call, "📜 **Справочник:**\n\n🌾 **Фарм** — Золото.\n⛏ **Шахта** — Риск/награда.\n⚔️ **Данж** — Монстры.\n🛒 **Магазин** — Экипировка.\n🍙 **Поесть** — Хиллим HP.")
    elif data == "profile":
        send_main(call, f"Твоя статистика:\n⭐ Уровень: {p['lvl']}\n❤️ Здоровье: {p['hp']}/{p['max_hp']}\n⚔️ Оружие: {p['weapon']}\n🛡 Броня: {p['armor']}\n💰 Золото: {p['gold']}\n🍙 Онигири: {p['onigiri']}")
    elif data == "top":
        if not players:
            send_main(call, "🏆 Список лидеров пуст!")
        else:
            sorted_players = sorted(players.values(), key=lambda x: x['gold'], reverse=True)
            top_text = "🏆 **Таблица лидеров:**\n\n"
            for i, pl in enumerate(sorted_players[:5], 1):
                u_tag = f"@{pl['username']}" if pl['username'] else pl['name']
                top_text += f"{i}. **{u_tag}** — 💰 {pl['gold']} (Ур. {pl['lvl']})\n"
            send_main(call, top_text)
    elif data == "shop":
        send_main(call, f"🛒 **Магазин:**\nУ тебя: 💰 {p['gold']} монет", shop=True)
    elif data == "buy_onigiri":
        if p['gold'] >= 500:
            p['gold'] -= 500
            p['onigiri'] += 1
            send_main(call, f"✅ Куплен Онигири! Золота: 💰 {p['gold']}", shop=True)
        else:
            send_main(call, f"❌ Не хватает золота! Нужно 500, а у тебя {p['gold']}.", shop=True)
    elif data == "buy_potion":
        if p['gold'] >= 3000:
            p['gold'] -= 3000
            p['hp'] = p['max_hp']
            send_main(call, f"✅ Зелье выпито! Золота: 💰 {p['gold']}", shop=True)
        else:
            send_main(call, f"❌ Не хватает золота! Нужно 3000, а у тебя {p['gold']}.", shop=True)
    elif data == "buy_sword":
        if p['gold'] >= 6000:
            p['gold'] -= 6000
            p['weapon'] = "Стальной меч"
            send_main(call, f"✅ Куплен Стальной меч! Золота: 💰 {p['gold']}", shop=True)
        else:
            send_main(call, f"❌ Не хватает золота! Нужно 6000, а у тебя {p['gold']}.", shop=True)
    elif data == "buy_armor":
        if p['gold'] >= 12000:
            p['gold'] -= 12000
            p['armor'] = "Тяжелая броня"
            p['max_hp'] += 100
            p['hp'] += 100
            send_main(call, f"✅ Куплена Тяжелая броня! Золота: 💰 {p['gold']}", shop=True)
        else:
            send_main(call, f"❌ Не хватает золота! Нужно 12000, а у тебя {p['gold']}.", shop=True)
    elif data == "farm":
        now = time.time()
        if uid in last_farm_time and now - last_farm_time[uid] < 60:
            left = int(60 - (now - last_farm_time[uid]))
            send_main(call, f"⏳ Отдохни еще {left} сек.")
        else:
            last_farm_time[uid] = now
            g = random.randint(10, 20)
            p['gold'] += g
            send_main(call, f"🌾 Получено **+{g}** золота. Всего: {p['gold']}")
    elif data == "mine":
        now = time.time()
        if uid in last_mine_time and now - last_mine_time[uid] < 90:
            left = int(90 - (now - last_mine_time[uid]))
            send_main(call, f"⏳ Подожди еще {left} сек.")
        else:
            last_mine_time[uid] = now
            damage = random.randint(25, 50)
            p['hp'] -= damage
            if random.random() < 0.35:
                gold = random.randint(250, 600)
                p['gold'] += gold
                send_main(call, f"⛏ Обвал (-{damage} HP), но нашел золото: **+{gold}**! (HP: {max(0, p['hp'])}/{p['max_hp']})")
            else:
                send_main(call, f"💥 Обвал! Урон: **{damage}** (HP: {max(0, p['hp'])}/{p['max_hp']})")
    elif data == "dungeon":
        if p['hp'] <= 50:
            send_main(call, "⚠️ Слишком опасно! HP <= 50, подлечись.")
        else:
            dmg = random.randint(35, 60)
            loot = random.randint(200, 450)
            p['hp'] -= dmg
            p['gold'] += loot
            send_main(call, f"⚔️ Данж пройден! Золото: **+{loot}**, урон: {dmg} (HP: {max(0, p['hp'])}/{p['max_hp']})")
    elif data == "eat":
        if p['hp'] >= p['max_hp']:
            send_main(call, "⚠️ Здоровье и так полное!")
        elif p['onigiri'] > 0:
            p['onigiri'] -= 1
            p['hp'] = min(p['max_hp'], p['hp'] + 40)
            send_main(call, f"🍙 Съеден Онигири (+40 HP). HP: {p['hp']}/{p['max_hp']}.")
        else:
            send_main(call, "❌ Нет Онигири!")

print("Бот запущен через pyTelegramBotAPI...")
bot.infinity_polling(timeout=60, long_polling_timeout=60)
