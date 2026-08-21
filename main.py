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
    else:
        players[uid]["name"] = name
    return players[uid]

def send_response(cid, text, is_group=False, shop_mode=False, name=None):
    # Добавляем имя игрока в начале для групп или текстового режима
    if name and is_group:
        text = f"👤 **{name}**, {text}"

    keyboard = None
    # Кнопки показываем ТОЛЬКО если это не группа
    if not is_group:
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

    payload = {"chat_id": cid, "text": text, "parse_mode": "Markdown"}
    if keyboard:
        payload["reply_markup"] = keyboard

    try:
        requests.post(BASE_URL + "sendMessage", json=payload, timeout=10)
    except Exception as e:
        print("Ошибка отправки:", e)

print("RPG-бот запущен и готов к работе (режим без кнопок в группах)!")
offset = None

while True:
    try:
        r = requests.get(BASE_URL + "getUpdates", params={"timeout": 30, "offset": offset}).json()
        if r.get("result"):
            for u in r["result"]:
                offset = u["update_id"] + 1
                
                # Обработка инлайн-кнопок (работает только в ЛС)
                if "callback_query" in u:
                    cq = u["callback_query"]
                    chat_type = cq["message"]["chat"]["type"]
                    is_group = chat_type in ["group", "supergroup"]
                    cid = cq["message"]["chat"]["id"]
                    uid = cq["from"]["id"]
                    name = cq["from"].get("first_name", "Игрок")
                    data = cq["data"]
                    p = get_p(uid, name)
                    
                    if data == "help":
                        send_response(cid, 
                            "📜 **Справочник:**\n\n"
                            "🌾 **Фарм** — Добыча золота и опыта (раз в 1 минуту).\n"
                            "⚔️ **Данж** — Рейд на монстров.\n"
                            "🏆 **Топ** — Рейтинг игроков.\n"
                            "🛒 **Магазин** — Покупка еды, зелий, оружия и брони.\n"
                            "🍙 **Поесть** — Восстановить HP.\n"
                            "👤 **Профиль** — Твоя статистика.", is_group=is_group, name=name
                        )
                    elif data == "profile":
                        send_response(cid, 
                            f"твоя статистика:\n"
                            f"⭐ Уровень: {p['lvl']} (XP: {p['xp']}/{p['lvl'] * 100})\n"
                            f"❤️ Здоровье: {p['hp']}/{p['max_hp']}\n"
                            f"⚔️ Оружие: {p['weapon']}\n"
                            f"🛡 Броня: {p['armor']}\n"
                            f"💰 Золото: {p['gold']}\n"
                            f"🍙 Онигири: {p['onigiri']} шт.", is_group=is_group, name=name
                        )
                    elif data == "top":
                        if not players:
                            send_response(cid, "🏆 Список лидеров пуст!", is_group=is_group, name=name)
                        else:
                            sorted_players = sorted(players.values(), key=lambda x: x['gold'], reverse=True)
                            top_text = "🏆 **Таблица лидеров (Топ богачей):**\n\n"
                            for i, pl in enumerate(sorted_players[:5], 1):
                                top_text += f"{i}. **{pl['name']}** — 💰 {pl['gold']} монет (Ур. {pl['lvl']})\n"
                            send_response(cid, top_text, is_group=is_group, name=name)
                    elif data == "farm":
                        current_time = time.time()
                        if uid in last_farm_time and current_time - last_farm_time[uid] < 60:
                            left = int(60 - (current_time - last_farm_time[uid]))
                            send_response(cid, f"⏳ Отдохни! На фарм можно ходить раз в минуту. Осталось: {left} сек.", is_group=is_group, name=name)
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
                            
                            send_response(cid, f"⛏ **Фарм завершен!**\n💰 Заработано монет: **+{g}**\n⭐ Опыт: +{xp_gain}" + ("\n🍙 Найдено: 1 Онигири!" if food else "") + f"\n💎 Всего золота: {p['gold']}" + lvl_up_text, is_group=is_group, name=name)
                    elif data == "dungeon":
                        if p['hp'] <= 25:
                            send_response(cid, "⚠️ Слишком мало здоровья для данжа! Сначала подкрепись онигири.", is_group=is_group, name=name)
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

                            send_response(cid, f"⚔️ **Данж успешно зачищен!**\n💰 Заработано монет: **+{loot}**\n⭐ Опыт: +{xp_gain}\n🩸 Потеряно HP: {dmg} (Осталось HP: {max(0, p['hp'])}/{p['max_hp']})\n💎 Всего золота: {p['gold']}{lvl_up_text}", is_group=is_group, name=name)
                    elif data == "shop":
                        send_response(cid, 
                            f"🛒 **Лавка торговца:**\nУ тебя в кармане: 💰 {p['gold']} монет\n\n"
                            "• 🍙 **Онигири** — 300 монет\n"
                            "• 🧪 **Зелье здоровья** — 600 монет\n"
                            "• ⚔️ **Стальной меч** — 1500 монет\n"
                            "• 🛡 **Тяжелые доспехи** — 3000 монет", is_group=is_group, shop_mode=True, name=name
                        )
                    elif data == "buy_onigiri":
                        if p['gold'] >= 300:
                            p['gold'] -= 300
                            p['onigiri'] += 1
                            send_response(cid, f"✅ Куплен 1 Онигири! Осталось золота: 💰 {p['gold']}", is_group=is_group, shop_mode=True, name=name)
                        else:
                            send_response(cid, f"❌ Не хватает золота! Нужно 300 монет, а у тебя {p['gold']}.", is_group=is_group, shop_mode=True, name=name)
                    elif data == "buy_potion":
                        if p['gold'] >= 600:
                            p['gold'] -= 600
                            p['hp'] = p['max_hp']
                            send_response(cid, f"✅ Зелье куплено и выпито! HP восстановлено. Золота: 💰 {p['gold']}", is_group=is_group, shop_mode=True, name=name)
                        else:
                            send_response(cid, f"❌ Не хватает золота! Нужно 600 монет, а у тебя {p['gold']}.", is_group=is_group, shop_mode=True, name=name)
                    elif data == "buy_sword":
                        if p['gold'] >= 1500:
                            p['gold'] -= 1500
                            p['weapon'] = "Стальной меч"
                            send_response(cid, f"✅ Куплен Стальной меч! Урон вырос. Золота: 💰 {p['gold']}", is_group=is_group, shop_mode=True, name=name)
                        else:
                            send_response(cid, f"❌ Не хватает золота! Нужно 1500 монет, а у тебя {p['gold']}.", is_group=is_group, shop_mode=True, name=name)
                    elif data == "buy_armor":
                        if p['gold'] >= 3000:
                            p['gold'] -= 3000
                            p['armor'] = "Тяжелые доспехи"
                            p['max_hp'] += 50
                            p['hp'] += 50
                            send_response(cid, f"✅ Куплены Тяжелые доспехи! Макс. HP увеличено на +50. Золота: 💰 {p['gold']}", is_group=is_group, shop_mode=True, name=name)
                        else:
                            send_response(cid, f"❌ Не хватает золота! Нужно 3000 монет, а у тебя {p['gold']}.", is_group=is_group, shop_mode=True, name=name)
                    elif data == "eat":
                        needed = random.randint(3, 5)
                        if p['hp'] >= p['max_hp']:
                            send_response(cid, "⚠️ Здоровье и так полностью восстановлено!", is_group=is_group, name=name)
                        elif p['onigiri'] >= needed:
                            p['onigiri'] -= needed
                            p['hp'] = p['max_hp']
                            send_response(cid, f"🍙 Ты плотно поел и потратил **{needed} шт.** онигири! HP полностью восстановлено до {p['max_hp']}. Осталось онигири: {p['onigiri']} шт.", is_group=is_group, name=name)
                        else:
                            send_response(cid, f"❌ Не хватает онигири! Чтобы полностью восстановить здоровье, нужно съесть **{needed} шт.**, а у тебя только **{p['onigiri']} шт.**", is_group=is_group, name=name)

                # Обработка текстовых сообщений (в ЛС и группах)
                elif "message" in u and "text" in u["message"]:
                    msg = u["message"]
                    chat_type = msg["chat"]["type"]
                    is_group = chat_type in ["group", "supergroup"]
                    cid = msg["chat"]["id"]
                    txt = msg["text"].lower().strip()
                    uid = msg["from"]["id"]
                    name = msg["from"].get("first_name", "Игрок")
                    p = get_p(uid, name)

                    if "@" in txt:
                        txt = txt.split("@")[0]

                    if txt in ["/start", "старт"]:
                        send_response(cid, "Привет! Добро пожаловать в экономическую RPG.", is_group=is_group, name=name)
                    elif txt in ["/help", "/помощь", "помощь"]:
                        send_response(cid, 
                            "📜 **Справочник команд:**\n\n"
                            "🌾 `фарм` — Добыча золота и опыта (раз в 1 минуту).\n"
                            "⚔️ `данж` — Рейд на монстров.\n"
                            "🏆 `топ` — Рейтинг богатейших игроков.\n"
                            "🛒 `магазин` — Список товаров.\n"
                            "🍙 `поесть` — Восстановить HP.\n"
                            "👤 `профиль` — Твоя статистика.", is_group=is_group, name=name
                        )
                    elif txt in ["/profile", "профиль"]:
                        send_response(cid, f"твоя статистика:\n⭐ Уровень: {p['lvl']} (XP: {p['xp']}/{p['lvl'] * 100})\n❤️ Здоровье: {p['hp']}/{p['max_hp']}\n⚔️ Оружие: {p['weapon']}\n🛡 Броня: {p['armor']}\n💰 Золото: {p['gold']}\n🍙 Онигири: {p['onigiri']}", is_group=is_group, name=name)
                    elif txt in ["/top", "топ"]:
                        if not players:
                            send_response(cid, "🏆 Список лидеров пуст!", is_group=is_group, name=name)
                        else:
                            sorted_players = sorted(players.values(), key=lambda x: x['gold'], reverse=True)
                            top_text = "🏆 **Таблица лидеров (Топ богачей):**\n\n"
                            for i, pl in enumerate(sorted_players[:5], 1):
                                top_text += f"{i}. **{pl['name']}** — 💰 {pl['gold']} монет (Ур. {pl['lvl']})\n"
                            send_response(cid, top_text, is_group=is_group, name=name)
                    elif txt in ["/shop", "магазин"]:
                        send_response(cid, 
                            "🛒 **Лавка торговца:**\n"
                            "• Купить онигири: `/buy onigiri` (300 монет)\n"
                            "• Купить зелье: `/buy potion` (600 монет)\n"
                            "• Купить меч: `/buy sword` (1500 монет)\n"
                            "• Купить доспехи: `/buy armor` (3000 монет)", is_group=is_group, name=name
                        )
                    elif txt in ["/farm", "фарм"]:
                        current_time = time.time()
                        if uid in last_farm_time and current_time - last_farm_time[uid] < 60:
                            left = int(60 - (current_time - last_farm_time[uid]))
                            send_response(cid, f"⏳ Отдохни! На фарм можно ходить раз в минуту. Осталось: {left} сек.", is_group=is_group, name=name)
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
                            
                            send_response(cid, f"⛏ **Фарм завершен!**\n💰 Заработано монет: **+{g}**\n⭐ Опыт: +{xp_gain}" + ("\n🍙 Найдено: 1 Онигири!" if food else "") + f"\n💎 Всего золота: {p['gold']}" + lvl_up_text, is_group=is_group, name=name)
                    elif txt in ["/dungeon", "данж"]:
                        if p['hp'] <= 25:
                            send_response(cid, "⚠️ Слишком мало здоровья для данжа! Сначала подкрепись онигири.", is_group=is_group, name=name)
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

                            send_response(cid, f"⚔️ **Данж успешно зачищен!**\n💰 Заработано монет: **+{loot}**\n⭐ Опыт: +{xp_gain}\n🩸 Потеряно HP: {dmg} (Осталось HP: {max(0, p['hp'])}/{p['max_hp']})\n💎 Всего золота: {p['gold']}{lvl_up_text}", is_group=is_group, name=name)
                    elif txt in ["поесть", "eat"]:
                        needed = random.randint(3, 5)
                        if p['hp'] >= p['max_hp']:
                            send_response(cid, "⚠️ Здоровье и так полностью восстановлено!", is_group=is_group, name=name)
                        elif p['onigiri'] >= needed:
                            p['onigiri'] -= needed
                            p['hp'] = p['max_hp']
                            send_response(cid, f"🍙 Ты плотно поел и потратил **{needed} шт.** онигири! HP полностью восстановлено до {p['max_hp']}.", is_group=is_group, name=name)
                        else:
                            send_response(cid, f"❌ Не хватает онигири! Нужно **{needed} шт.**, а у тебя **{p['onigiri']} шт.**", is_group=is_group, name=name)
                    elif txt == "/buy onigiri":
                        if p['gold'] >= 300:
                            p['gold'] -= 300
                            p['onigiri'] += 1
                            send_response(cid, "✅ Куплен 1 Онигири!", is_group=is_group, name=name)
                        else:
                            send_response(cid, "❌ Не хватает золота (нужно 300 монет)!", is_group=is_group, name=name)
                    elif txt == "/buy potion":
                        if p['gold'] >= 600:
                            p['gold'] -= 600
                            p['hp'] = p['max_hp']
                            send_response(cid, "✅ Куплено и выпито Зелье здоровья!", is_group=is_group, name=name)
                        else:
                            send_response(cid, "❌ Не хватает золота (нужно 600 монет)!", is_group=is_group, name=name)
                    elif txt == "/buy sword":
                        if p['gold'] >= 1500:
                            p['gold'] -= 1500
                            p['weapon'] = "Стальной меч"
                            send_response(cid, "✅ Куплен Стальной меч!", is_group=is_group, name=name)
                        else:
                            send_response(cid, "❌ Не хватает золота (нужно 1500 монет)!", is_group=is_group, name=name)
                    elif txt == "/buy armor":
                        if p['gold'] >= 3000:
                            p['gold'] -= 3000
                            p['armor'] = "Тяжелые доспехи"
                            p['max_hp'] += 50
                            p['hp'] += 50
                            send_response(cid, "✅ Куплены Тяжелые доспехи (+50 HP)!", is_group=is_group, name=name)
                        else:
                            send_response(cid, "❌ Не хватает золота (нужно 3000 монет)!", is_group=is_group, name=name)
    except Exception as e:
        print("Ошибка в цикле:", e)
        time.sleep(2)
