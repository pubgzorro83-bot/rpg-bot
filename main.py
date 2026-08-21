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
            "name": name, "gold": 100, "onigiri": 1, "hp": 100, "max_hp": 100,
            "lvl": 1, "xp": 0, "weapon": "Ржавый меч", "armor": "Тканевая одежда"
        }
    else:
        players[uid]["name"] = name
    return players[uid]

def send_response(cid, text, name):
    text = f"👤 **{name}**, {text}"
    try:
        requests.post(BASE_URL + "sendMessage", json={"chat_id": cid, "text": text, "parse_mode": "Markdown"}, timeout=10)
    except Exception as e:
        print("Ошибка:", e)

print("RPG-бот запущен (Хардкорный режим)!")
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

                    if txt in ["/start", "старт"]:
                        send_response(cid, "Добро пожаловать в Хардкорную RPG! Везде опасно. Команды: фарм, шахта, данж, профиль, топ, магазин, поесть.", name)
                    
                    elif txt in ["фарм"]:
                        current_time = time.time()
                        if uid in last_farm_time and current_time - last_farm_time[uid] < 60:
                            send_response(cid, "Ты слишком устал, подожди минуту.", name)
                        else:
                            last_farm_time[uid] = current_time
                            g = random.randint(10, 30) # Урезали доход
                            p['gold'] += g
                            send_response(cid, f"Ты поработал на полях. Получено: {g} золота.", name)

                    elif txt in ["шахта"]:
                        current_time = time.time()
                        if uid in last_mine_time and current_time - last_mine_time[uid] < 120:
                            send_response(cid, "Шахта нестабильна, подожди 2 минуты.", name)
                        else:
                            last_mine_time[uid] = current_time
                            damage = random.randint(10, 20)
                            p['hp'] -= damage
                            if random.random() < 0.3: # Шанс успеха
                                gold = random.randint(100, 250)
                                p['gold'] += gold
                                send_response(cid, f"В шахте опасно! Ты получил {damage} урона, но нашел {gold} золота!", name)
                            else:
                                send_response(cid, f"Обвал! Ты получил {damage} урона и ничего не нашел.", name)

                    elif txt in ["данж"]:
                        if p['hp'] <= 40:
                            send_response(cid, "Слишком опасно, HP меньше 40!", name)
                        else:
                            p['hp'] -= random.randint(30, 50)
                            loot = random.randint(150, 400)
                            p['gold'] += loot
                            send_response(cid, f"Ты выжил в данже! Получено: {loot} золота.", name)

                    elif txt in ["магазин"]:
                        send_response(cid, "Цены: 🍙 Онигири(500), 🧪 Зелье(2500), ⚔️ Меч(5000), 🛡 Броня(10000). Используй '/buy [предмет]'.", name)

                    elif txt.startswith("/buy "):
                        item = txt.split("/buy ")[1]
                        if item == "онигири" and p['gold'] >= 500:
                            p['gold'] -= 500; p['onigiri'] += 1; send_response(cid, "Куплен Онигири.", name)
                        elif item == "зелье" and p['gold'] >= 2500:
                            p['gold'] -= 2500; p['hp'] = p['max_hp']; send_response(cid, "Зелье выпито, HP полно.", name)
                        elif item == "меч" and p['gold'] >= 5000:
                            p['gold'] -= 5000; p['weapon'] = "Стальной меч"; send_response(cid, "Меч куплен.", name)
                        elif item == "броня" and p['gold'] >= 10000:
                            p['gold'] -= 10000; p['max_hp'] += 100; p['hp'] += 100; send_response(cid, "Броня куплена.", name)
                        else:
                            send_response(cid, "Не хватает золота или неверное название!", name)

                    elif txt in ["поесть"]:
                        if p['onigiri'] > 0:
                            p['onigiri'] -= 1; p['hp'] = min(p['max_hp'], p['hp'] + 50); send_response(cid, "Ты съел Онигири (+50 HP).", name)
                        else:
                            send_response(cid, "Нет еды!", name)
                    
                    elif txt in ["профиль"]:
                        send_response(cid, f"Ур: {p['lvl']}, HP: {p['hp']}/{p['max_hp']}, Золото: {p['gold']}, Еда: {p['onigiri']}", name)
    except Exception as e:
        print("Ошибка:", e)
        time.sleep(2)
