import time
import requests
import random

TOKEN = "8845697358:AAGHC80gXtHoQbFvu6bkxPtF9zVAN_pVKsc"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"

players = {}
last_farm_time = {}
last_mine_time = {}

def get_p(uid, name):
    if uid not in players:
        players[uid] = {
            "name": name, 
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
    return players[uid]

def send_response(cid, text, name=None):
    if name:
        text = f"👤 **{name}**, {text}"
    
    payload = {"chat_id": cid, "text": text, "parse_mode": "Markdown"}

    try:
        requests.post(BASE_URL + "sendMessage", json=payload, timeout=10)
    except Exception as e:
        print("Ошибка отправки:", e)

print("RPG-бот запущен (Строго без кнопок, хардкор)!")
offset = None

while True:
    try:
        r = requests.get(BASE_URL + "getUpdates", params={"timeout": 30, "offset": offset}).json()
        if r.get("result"):
            for u in r["result"]:
                offset = u["update_id"] + 1
                
                if "message" in u and "text" in u["message"]:
                    msg = u["message"]
                    cid = msg["chat"]["id"]
                    txt = msg["text"].lower().strip()
                    uid = msg["from"]["id"]
                    name = msg["from"].get("first_name", "Игрок")
                    p = get_p(uid, name)

                    if "@" in txt:
                        txt = txt.split("@")[0]

                    if txt in ["/start", "старт"]:
                        send_response(cid, "Привет! Это Хардкорная RPG. Управления кнопками больше нет. Используй команды: /farm, /mine, /dungeon, /profile, /top, /shop, /eat", name)
                    
                    elif txt in ["/help", "/помощь", "помощь"]:
                        send_response(cid, 
                            "📜 **Справочник команд:**\n\n"
                            "🌾 `/farm` — Фарм золота (раз в 1 минуту).\n"
                            "⛏ `/mine` — Опасная шахта (урон по HP, много золота).\n"
                            "⚔️ `/dungeon` — Рейд на монстров.\n"
                            "🏆 `/top` — Топ богачей.\n"
                            "🛒 `/shop` — Магазин (высокие цены).\n"
                            "🍙 `/eat` — Поесть и восстановить HP.\n"
                            "👤 `/profile` — Твоя статистика.", name
                        )
                    
                    elif txt in ["/profile", "профиль"]:
                        send_response(cid, f"Твоя статистика:\n⭐ Уровень: {p['lvl']} (XP: {p['xp']}/{p['lvl'] * 100})\n❤️ Здоровье: {p['hp']}/{p['max_hp']}\n⚔️ Оружие: {p['weapon']}\n🛡 Броня: {p['armor']}\n💰 Золото: {p['gold']}\n🍙 Онигири: {p['onigiri']}", name)
                    
                    elif txt in ["/top", "топ"]:
                        if not players:
                            send_response(cid, "🏆 Список лидеров пуст!", name)
                        else:
                            sorted_players = sorted(players.values(), key=lambda x: x['gold'], reverse=True)
                            top_text = "🏆 **Таблица лидеров:**\n\n"
                            for i, pl in enumerate(sorted_players[:5], 1):
                                top_text += f"{i}. **{pl['name']}** — 💰 {pl['gold']} (Ур. {pl['lvl']})\n"
                            send_response(cid, top_text, name)
                    
                    elif txt in ["/shop", "магазин"]:
                        send_response(cid, 
                            "🛒 **Хардкорная лавка торговца:**\n"
                            "• `/buy onigiri` — Онигири (500 монет)\n"
                            "• `/buy potion` — Зелье здоровья (3000 монет)\n"
                            "• `/buy sword` — Стальной меч (6000 монет)\n"
                            "• `/buy armor` — Тяжелая броня (12000 монет)", name
                        )
                    
                    elif txt in ["/farm", "фарм"]:
                        current_time = time.time()
                        if uid in last_farm_time and current_time - last_farm_time[uid] < 60:
                            left = int(60 - (current_time - last_farm_time[uid]))
                            send_response(cid, f"⏳ Отдохни! На фарм можно ходить раз в минуту. Осталось: {left} сек.", name)
                        else:
                            last_farm_time[uid] = current_time
                            g = random.randint(10, 25)
                            p['gold'] += g
                            send_response(cid, f"🌾 Фарм завершен. Получено: **+{g}** золота. Всего: {p['gold']}", name)

                    elif txt in ["/mine", "шахта"]:
                        current_time = time.time()
                        if uid in last_mine_time and current_time - last_mine_time[uid] < 90:
                            left = int(90 - (current_time - last_mine_time[uid]))
                            send_response(cid, f"⏳ Шахта осыпается, подожди еще {left} сек.", name)
                        else:
                            last_mine_time[uid] = current_time
                            damage = random.randint(20, 45) # Опасный урон
                            p['hp'] -= damage
                            if random.random() < 0.35: # Шанс сокровища
                                gold = random.randint(200, 500)
                                p['gold'] += gold
                                send_response(cid, f"⛏ Опасный спуск в шахту! Обвал нанес тебе **{damage} урона**, но ты откопал жилу золота: **+{gold}**! (HP: {max(0, p['hp'])}/{p['max_hp']})", name)
                            else:
                                send_response(cid, f"💥 Страшный обвал в шахте! Ты получил **{damage} урона** и едва унес ноги без добычи. (HP: {max(0, p['hp'])}/{p['max_hp']})", name)

                    elif txt in ["/dungeon", "данж"]:
                        if p['hp'] <= 50:
                            send_response(cid, "⚠️ Слишком опасно! Твое HP меньше или равно 50, сначала подлечись.", name)
                        else:
                            dmg = random.randint(35, 60)
                            loot = random.randint(200, 450)
                            p['hp'] -= dmg
                            p['gold'] += loot
                            send_response(cid, f"⚔️ Рейд в данж завершен!\n💰 Добыча: **+{loot}** золота\n🩸 Получено урона: {dmg} (Осталось HP: {max(0, p['hp'])}/{p['max_hp']})", name)

                    elif txt in ["/eat", "поесть"]:
                        if p['hp'] >= p['max_hp']:
                            send_response(cid, "⚠️ Твое здоровье и так полное!", name)
                        elif p['onigiri'] > 0:
                            p['onigiri'] -= 1
                            p['hp'] = min(p['max_hp'], p['hp'] + 40)
                            send_response(cid, f"🍙 Ты съел Онигири (+40 HP). Здоровье: {p['hp']}/{p['max_hp']}.", name)
                        else:
                            send_response(cid, "❌ У тебя нет еды (Онигири)!", name)
                    
                    elif txt == "/buy onigiri":
                        if p['gold'] >= 500:
                            p['gold'] -= 500
                            p['onigiri'] += 1
                            send_response(cid, "✅ Куплен 1 Онигири за 500 монет.", name)
                        else:
                            send_response(cid, "❌ Нужно 500 монет!", name)
                    
                    elif txt == "/buy potion":
                        if p['gold'] >= 3000:
                            p['gold'] -= 3000
                            p['hp'] = p['max_hp']
                            send_response(cid, "✅ Зелье за 3000 монет выпито! HP полностью восстановлено.", name)
                        else:
                            send_response(cid, "❌ Зелье стоит 3000 монет! Не хватает.", name)
                    
                    elif txt == "/buy sword":
                        if p['gold'] >= 6000:
                            p['gold'] -= 6000
                            p['weapon'] = "Стальной меч"
                            send_response(cid, "✅ Куплен Стальной меч за 6000 монет!", name)
                        else:
                            send_response(cid, "❌ Меч стоит 6000 монет! Не хватает.", name)
                    
                    elif txt == "/buy armor":
                        if p['gold'] >= 12000:
                            p['gold'] -= 12000
                            p['armor'] = "Тяжелая броня"
                            p['max_hp'] += 100
                            p['hp'] += 100
                            send_response(cid, "✅ Куплена Тяжелая броня за 12000 монет (+100 макс. HP)!", name)
                        else:
                            send_response(cid, "❌ Броня стоит 12000 монет! Не хватает.", name)

    except Exception as e:
        print("Ошибка:", e)
        time.sleep(2)
