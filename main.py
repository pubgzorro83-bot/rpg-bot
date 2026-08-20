import time
import requests
import random

TOKEN = "8845697358:AAGHC80gXtHoQbFvu6bkxPtF9zVAN_pVKsc"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"

players = {}
last_farm_time = {}

def get_p(uid, name):
    if uid not in players:
        players[uid] = {
            "name": name, 
            "gold": 100, 
            "onigiri": 2, 
            "hp": 100, 
            "max_hp": 100,
            "lvl": 1,
            "xp": 0,
            "weapon": "Ржавый меч",
            "armor": "Тканевая одежда"
        }
    return players[uid]

def send_menu(cid, text, shop_mode=False):
    if shop_mode:
        keyboard = {
            "inline_keyboard": [
                [{"text": "🍙 Онигири (300г)", "callback_data": "buy_onigiri"}, {"text": "🧪 Зелье (600г)", "callback_data": "buy_potion"}],
                [{"text": "⚔️ Меч (1500г)", "callback_data": "buy_sword"}, {"text": "🛡 Доспехи (3000г)", "callback_data": "buy_armor"}],
                [{"text": "🔙 Назад в меню", "callback_data": "help"}]
            ]
        }
    else:
        keyboard = {
            "inline_keyboard": [
                [{"text": "🌾 Фарм", "callback_data": "farm"}, {"text": "⚔️ Данж", "callback_data": "dungeon"}],
                [{"text": "👤 Профиль", "callback_data": "profile"}, {"text": "🏆 Топ", "callback_data": "top"}],
                [{"text": "🛒 Магазин", "callback_data": "shop"}, {"text": "🍙 Поесть", "callback_data": "eat"}],
                [{"text": "❓ Помощь", "callback_data": "help"}]
            ]
        }
    try:
        requests.post(BASE_URL + "sendMessage", json={"chat_id": cid, "text": text, "reply_markup": keyboard}, timeout=10)
    except Exception as e:
        print("Ошибка отправки:", e)

print("RPG-бот запущен и готов к работе!")
offset = None

while True:
    try:
        r = requests.get(BASE_URL + "getUpdates", params={"timeout": 30, "offset": offset}).json()
        if r.get("result"):
            for u in r["result"]:
                offset = u["update_id"] + 1
                
                # Обработка инлайн-кнопок
                if "callback_query" in u:
                    cq = u["callback_query"]
                    cid = cq["message"]["chat"]["id"]
                    uid = cq["from"]["id"]
                    name = cq["from"].get("first_name", "Игрок")
                    data = cq["data"]
                    p = get_p(uid, name)
                    
                    if data == "help":
                        send_menu(cid, 
                            "📜 **Справочник:**\n\n"
                            "🌾 **Фарм** — Добыча золота и опыта (раз в 1 минуту).\n"
                            "⚔️ **Данж** — Рейд на монстров за ценными трофеями.\n"
                            "🏆 **Топ** — Рейтинг богатейших игроков.\n"
                            "🛒 **Магазин** — Покупка еды, зелий, оружия и брони.\n"
                            "🍙 **Поесть** — Восстановить HP (нужно от 3 до 5 онигири).\n"
                            "👤 **Профиль** — Твоя статистика и снаряжение.\n\n"
                            "👥 **Команды для групп:**\n"
                            "• `/farm` — Фарм\n"
                            "• `/dungeon` — Данж\n"
                            "• `/profile` — Профиль\n"
                            "• `/top` — Топ\n"
                            "• `/shop` — Магазин"
                        )
                    elif data == "profile":
                        send_menu(cid, 
                            f"👤 **Игрок:** {p['name']}\n"
                            f"⭐ Уровень: {p['lvl']} (XP: {p['xp']}/{p['lvl'] * 100})\n"
                            f"❤️ Здоровье: {p['hp']}/{p['max_hp']}\n"
                            f"⚔️ Оружие: {p['weapon']}\n"
                            f"🛡 Броня: {p['armor']}\n"
                            f"💰 Золото: {p['gold']}\n"
                            f"🍙 Онигири: {p['onigiri']} шт."
                        )
                    elif data == "top":
                        if not players:
                            send_menu(cid, "🏆 Список лидеров пуст!")
                        else:
                            sorted_players = sorted(players.values(), key=lambda x: x['gold'], reverse=True)
                            top_text = "🏆 **Таблица лидеров (Топ богачей):**\n\n"
                            for i, pl in enumerate(sorted_players[:5], 1):
                                top_text += f"{i}. **{pl['name']}** — 💰 {pl['gold']} монет (Ур. {pl['lvl']})\n"
                            send_menu(cid, top_text)
                    elif data == "farm":
                        current_time = time.time()
                        if uid in last_farm_time and current_time - last_farm_time[uid] < 60:
                            left = int(60 - (current_time - last_farm_time[uid]))
                            send_menu(cid, f"⏳ Отдохни! На фарм можно ходить раз в минуту. Осталось: {left} сек.")
                        else:
                            last_farm_time[uid] = current_time
                            g = random.randint(30, 60)
                            xp_gain = random.randint(15, 30)
                            food = random.choice([0, 1])
                            p['gold'] += g
                            p['xp'] += xp_gain
                            p['onigiri'] += food
                            
                            lvl_up_text = ""
                            if p['xp'] >= p['lvl'] * 100:
                                p['lvl'] += 1
                                p['max_hp'] += 20
                                p['hp'] = p['max_hp']
                                lvl_up_text = f"\n🎉 **Новый уровень ({p['lvl']})!** Макс. HP увеличено!"
                            
                            send_menu(cid, f"⛏ **Фарм завершен!**\n💰 Заработано монет: **+{g}**\n⭐ Опыт: +{xp_gain}" + ("\n🍙 Найдено: 1 Онигири!" if food else "") + f"\n💎 Всего золота: {p['gold']}" + lvl_up_text)
                    elif data == "dungeon":
                        if p['hp'] <= 25:
                            send_menu(cid, "⚠️ Слишком мало здоровья для данжа! Сначала подкрепись онигири.")
                        else:
                            dmg = random.randint(20, 45)
                            loot = random.randint(80, 180)
                            xp_gain = random.randint(40, 80)
                            p['hp'] -= dmg
                            p['gold'] += loot
                            p['xp'] += xp_gain
                            
                            lvl_up_text = ""
                            if p['xp'] >= p['lvl'] * 100:
                                p['lvl'] += 1
                                p['max_hp'] += 20
                                lvl_up_text = f"\n🎉 **Новый уровень ({p['lvl']})!**"

                            send_menu(cid, f"⚔️ **Данж успешно зачищен!**\n💰 Заработано монет: **+{loot}**\n⭐ Опыт: +{xp_gain}\n🩸 Потеряно HP: {dmg} (Осталось HP: {max(0, p['hp'])}/{p['max_hp']})\n💎 Всего золота: {p['gold']}{lvl_up_text}")
                    elif data == "shop":
                        send_menu(cid, 
                            f"🛒 **Лавка торговца:**\nУ тебя в кармане: 💰 {p['gold']} монет\n\n"
                            "• 🍙 **Онигири** — 300 монет\n"
                            "• 🧪 **Зелье здоровья** — 600 монет\n"
                            "• ⚔️ **Стальной меч** — 1500 монет\n"
                            "• 🛡 **Тяжелые доспехи** — 3000 монет", shop_mode=True
                        )
                    elif data == "buy_onigiri":
                        if p['gold'] >= 300:
                            p['gold'] -= 300
                            p['onigiri'] += 1
                            send_menu(cid, f"✅ Куплен 1 Онигири! Осталось золота: 💰 {p['gold']}", shop_mode=True)
                        else:
                            send_menu(cid, f"❌ Не хватает золота! Нужно 300 монет, а у тебя {p['gold']}.", shop_mode=True)
                    elif data == "buy_potion":
                        if p['gold'] >= 600:
                            p['gold'] -= 600
                            p['hp'] = p['max_hp']
                            send_menu(cid, f"✅ Зелье куплено и выпито! HP восстановлено. Золота: 💰 {p['gold']}", shop_mode=True)
                        else:
                            send_menu(cid, f"❌ Не хватает золота! Нужно 600 монет, а у тебя {p['gold']}.", shop_mode=True)
                    elif data == "buy_sword":
                        if p['gold'] >= 1500:
                            p['gold'] -= 1500
                            p['weapon'] = "Стальной меч"
                            send_menu(cid, f"✅ Куплен Стальной меч! Урон вырос. Золота: 💰 {p['gold']}", shop_mode=True)
                        else:
                            send_menu(cid, f"❌ Не хватает золота! Нужно 1500 монет, а у тебя {p['gold']}.", shop_mode=True)
                    elif data == "buy_armor":
                        if p['gold'] >= 3000:
                            p['gold'] -= 3000
                            p['armor'] = "Тяжелые доспехи"
                            p['max_hp'] += 50
                            p['hp'] += 50
                            send_menu(cid, f"✅ Куплены Тяжелые доспехи! Макс. HP увеличено на +50. Золота: 💰 {p['gold']}", shop_mode=True)
                        else:
                            send_menu(cid, f"❌ Не хватает золота! Нужно 3000 монет, а у тебя {p['gold']}.", shop_mode=True)
                    elif data == "eat":
                        needed = random.randint(3, 5)
                        if p['hp'] >= p['max_hp']:
                            send_menu(cid, "⚠️ Здоровье и так полностью восстановлено!")
                        elif p['onigiri'] >= needed:
                            p['onigiri'] -= needed
                            p['hp'] = p['max_hp']
                            send_menu(cid, f"🍙 Ты плотно поел и потратил **{needed} шт.** онигири! HP полностью восстановлено до {p['max_hp']}. Осталось онигири: {p['onigiri']} шт.")
                        else:
                            send_menu(cid, f"❌ Не хватает онигири! Чтобы полностью восстановить здоровье, нужно съесть **{needed} шт.**, а у тебя только **{p['onigiri']} шт.**")

                # Обработка текстовых команд (в личке и группах)
                elif "message" in u and "text" in u["message"]:
                    msg = u["message"]
                    cid = msg["chat"]["id"]
                    txt = msg["text"].lower().strip()
                    uid = msg["from"]["id"]
                    name = msg["from"].get("first_name", "Игрок")
                    p = get_p(uid, name)

                    if "@" in txt:
                        txt = txt.split("@")[0]

                    if txt in ["/start", "старт"]:
                        send_menu(cid, f"🌾 Привет, {name}! Добро пожаловать в экономическую RPG. Используй кнопки ниже:")
                    elif txt in ["/help", "/помощь", "помощь"]:
                        send_menu(cid, 
                            "📜 **Справочник:**\n\n"
                            "🌾 **Фарм** — Добыча золота и опыта (раз в 1 минуту).\n"
                            "⚔️ **Данж** — Рейд на монстров за ценными трофеями.\n"
                            "🏆 **Топ** — Рейтинг богатейших игроков.\n"
                            "🛒 **Магазин** — Покупка еды, зелий, оружия и брони.\n"
                            "🍙 **Поесть** — Восстановить HP (нужно от 3 до 5 онигири).\n"
                            "👤 **Профиль** — Твоя статистика и снаряжение.\n\n"
                            "👥 **Команды для групп:**\n"
                            "• `/farm` — Фарм\n"
                            "• `/dungeon` — Данж\n"
                            "• `/profile` — Профиль\n"
                            "• `/top` — Топ\n"
                            "• `/shop` — Магазин"
                        )
                    elif txt in ["/profile", "профиль"]:
                        send_menu(cid, f"👤 **Игрок:** {p['name']}\n⭐ Уровень: {p['lvl']} (XP: {p['xp']}/{p['lvl'] * 100})\n❤️ Здоровье: {p['hp']}/{p['max_hp']}\n⚔️ Оружие: {p['weapon']}\n🛡 Броня: {p['armor']}\n💰 Золото: {p['gold']}\n🍙 Онигири: {p['onigiri']}")
                    elif txt in ["/top", "топ"]:
                        if not players:
                            send_menu(cid, "🏆 Список лидеров пуст!")
                        else:
                            sorted_players = sorted(players.values(), key=lambda x: x['gold'], reverse=True)
                            top_text = "🏆 **Таблица лидеров (Топ богачей):**\n\n"
                            for i, pl in enumerate(sorted_players[:5], 1):
                                top_text += f"{i}. **{pl['name']}** — 💰 {pl['gold']} монет (Ур. {pl['lvl']})\n"
                            send_menu(cid, top_text)
                    elif txt in ["/shop", "магазин"]:
                        send_menu(cid, 
                            f"🛒 **Лавка торговца:**\nУ тебя в кармане: 💰 {p['gold']} монет\n\n"
                            "• 🍙 **Онигири** — 300 монет\n• 🧪 **Зелье здоровья** — 600 монет\n"
                            "• ⚔️ **Стальной меч** — 1500 монет\n• 🛡 **Тяжелые доспехи** — 3000 монет", shop_mode=True
                        )
                    elif txt in ["/farm", "фарм"]:
                        current_time = time.time()
                        if uid in last_farm_time and current_time - last_farm_time[uid] < 60:
                            left = int(60 - (current_time - last_farm_time[uid]))
                            send_menu(cid, f"⏳ Отдохни! На фарм можно ходить раз в минуту. Осталось: {left} сек.")
                        else:
                            last_farm_time[uid] = current_time
                            g = random.randint(30, 60)
                            xp_gain = random.randint(15, 30)
                            food = random.choice([0, 1])
                            p['gold'] += g
                            p['xp'] += xp_gain
                            p['onigiri'] += food
                            
                            lvl_up_text = ""
                            if p['xp'] >= p['lvl'] * 100:
                                p['lvl'] += 1
                                p['max_hp'] += 20
                                p['hp'] = p['max_hp']
                                lvl_up_text = f"\n🎉 **Новый уровень ({p['lvl']})!** Макс. HP увеличено!"
                            
                            send_menu(cid, f"⛏ **Фарм завершен!**\n💰 Заработано монет: **+{g}**\n⭐ Опыт: +{xp_gain}" + ("\n🍙 Найдено: 1 Онигири!" if food else "") + f"\n💎 Всего золота: {p['gold']}" + lvl_up_text)
                    elif txt in ["/dungeon", "данж"]:
                        if p['hp'] <= 25:
                            send_menu(cid, "⚠️ Слишком мало здоровья для данжа! Сначала подкрепись онигири.")
                        else:
                            dmg = random.randint(20, 45)
                            loot = random.randint(80, 180)
                            xp_gain = random.randint(40, 80)
                            p['hp'] -= dmg
                            p['gold'] += loot
                            p['xp'] += xp_gain
                            
                            lvl_up_text = ""
                            if p['xp'] >= p['lvl'] * 100:
                                p['lvl'] += 1
                                p['max_hp'] += 20
                                lvl_up_text = f"\n🎉 **Новый уровень ({p['lvl']})!**"

                            send_menu(cid, f"⚔️ **Данж успешно зачищен!**\n💰 Заработано монет: **+{loot}**\n⭐ Опыт: +{xp_gain}\n🩸 Потеряно HP: {dmg} (Осталось HP: {max(0, p['hp'])}/{p['max_hp']})\n💎 Всего золота: {p['gold']}{lvl_up_text}")
                    elif txt == "/buy onigiri":
                        if p['gold'] >= 300:
                            p['gold'] -= 300
                            p['onigiri'] += 1
                            send_menu(cid, "✅ Куплен 1 Онигири!")
                        else:
                            send_menu(cid, "❌ Не хватает золота (нужно 300 монет)!")
                    elif txt == "/buy potion":
                        if p['gold'] >= 600:
                            p['gold'] -= 600
                            p['hp'] = p['max_hp']
                            send_menu(cid, "✅ Куплено и выпито Зелье здоровья! HP восстановлено.")
                        else:
                            send_menu(cid, "❌ Не хватает золота (нужно 600 монет)!")
                    elif txt == "/buy sword":
                        if p['gold'] >= 1500:
                            p['gold'] -= 1500
                            p['weapon'] = "Стальной меч"
                            send_menu(cid, "✅ Куплен Стальной меч! Твой урон в данжах стал выше.")
                        else:
                            send_menu(cid, "❌ Не хватает золота (нужно 1500 монет)!")
                    elif txt == "/buy armor":
                        if p['gold'] >= 3000:
                            p['gold'] -= 3000
                            p['armor'] = "Тяжелые доспехи"
                            p['max_hp'] += 50
                            p['hp'] += 50
                            send_menu(cid, "✅ Куплены Тяжелые доспехи! Максимальное здоровье увеличено на +50 HP.")
                        else:
                            send_menu(cid, "❌ Не хватает золота (нужно 3000 монет)!")
    except Exception as e:
        print("Ошибка в цикле:", e)
        time.sleep(2)
