# ==============================================
# 💎 Power Point Break Store Bot V2 (Smart Edition)
# Admin: @MinexxProo | Payment: 01877576843
# ==============================================

import json, asyncio, datetime
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8347151795:AAGjhhVBd8t_CJ90BKm6nM2ZyMg6kvDvg2M"   # <-- এখানে তোমার BotFather token বসাও
ADMIN = "@MinexxProo"
PAYMENT_NUMBER = "01877576843"

USERS_FILE = "users.json"
PRODUCTS_FILE = "products.json"

# ---------------- JSON Loader -----------------
def load_json(file):
    try:
        with open(file, "r") as f: return json.load(f)
    except: return {}

def save_json(file, data):
    with open(file, "w") as f: json.dump(data, f, indent=4)

users = load_json(USERS_FILE)
products = load_json(PRODUCTS_FILE)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# ---------------- User Register -----------------
def register_user(user):
    uid = str(user.id)
    if uid not in users:
        users[uid] = {
            "username": user.username or "unknown",
            "balance": 0,
            "ref": None,
            "join": str(datetime.date.today()),
            "user_no": len(users)+1,
            "bonus_date": ""
        }
        save_json(USERS_FILE, users)

# ---------------- /start -----------------
@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    args = msg.get_args()
    register_user(msg.from_user)

    # Referral tracking
    if args.startswith("ref_"):
        ref_id = args.split("_")[1]
        if ref_id != str(msg.from_user.id) and users[str(msg.from_user.id)]["ref"] is None:
            users[str(msg.from_user.id)]["ref"] = ref_id
            if ref_id in users:
                users[ref_id]["balance"] += 20
                await bot.send_message(ref_id, f"🎉 You got 20৳ bonus from referral @{msg.from_user.username}!")
            save_json(USERS_FILE, users)

    u = users[str(msg.from_user.id)]

    # Admin welcome
    if msg.from_user.username == ADMIN.replace("@", ""):
        await msg.answer(
            f"👑 Welcome back {ADMIN}\n━━━━━━━━━━━━━━━━━━━━━━\nUse /adminpanel to view admin commands."
        )
        return

    text = (
        f"┏━━━━━━━━━━━━━━━━━━━━━━┓\n"
        f"👤 @{u['username']}\n"
        f"🆔 {msg.from_user.id}\n"
        f"💰 Balance: {u['balance']}৳\n"
        f"👥 User No: {u['user_no']}\n"
        f"┗━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        "🛍️ Power Point Break Store 🏪\n━━━━━━━━━━━━━━━━━━━━━━"
    )
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🛒 Store", callback_data="store"),
        InlineKeyboardButton("💰 Deposit", callback_data="deposit"),
        InlineKeyboardButton("🎁 Bonus", callback_data="bonus"),
        InlineKeyboardButton("👥 Invite", callback_data="ref"),
    )
    await msg.answer(text, reply_markup=kb)

# ---------------- Deposit -----------------
@dp.callback_query_handler(lambda c: c.data == "deposit")
async def deposit(call: types.CallbackQuery):
    await call.message.answer(
        f"📥 Send Money to any of these ↓\n"
        f"📱 bKash: {PAYMENT_NUMBER}\n"
        f"💸 Nagad: {PAYMENT_NUMBER}\n"
        f"💰 Upay: {PAYMENT_NUMBER}\n"
        f"🏦 Rocket: {PAYMENT_NUMBER}\n\n"
        f"Then send your TRX ID here 👇\nExample: TXN987654321"
    )

@dp.message_handler(lambda m: m.text.startswith("TXN") or m.text.startswith("txn"))
async def handle_trx(msg: types.Message):
    await bot.send_message(
        ADMIN.replace("@", ""),
        f"💸 New Deposit Request\n👤 @{msg.from_user.username}\n🆔 {msg.from_user.id}\n🧾 TRX: {msg.text}\n🏦 Payment: {PAYMENT_NUMBER}"
    )
    await msg.reply("✅ Deposit request sent! Wait for admin approval.")

# ---------------- Store -----------------
@dp.callback_query_handler(lambda c: c.data == "store")
async def open_store(call: types.CallbackQuery):
    if not products:
        await call.message.answer("🛍️ No products available.")
        return
    txt = "🛍️ Power Point Break Store\n━━━━━━━━━━━━━━━━━━━━━━\n"
    kb = InlineKeyboardMarkup(row_width=1)
    for name, data in products.items():
        stock = "🟢" if len(data["stock"])>0 else "🔴"
        txt += f"{stock} {name} — {data['price']}৳\n"
        kb.add(InlineKeyboardButton(f"💎 Buy {name}", callback_data=f"buy_{name}"))
    await call.message.answer(txt, reply_markup=kb)

# ---------------- Buy Product -----------------
@dp.callback_query_handler(lambda c: c.data.startswith("buy_"))
async def buy_item(call: types.CallbackQuery):
    pname = call.data.replace("buy_","")
    uid = str(call.from_user.id)
    u = users[uid]
    if pname not in products: return await call.answer("Product not found.")
    item = products[pname]
    if u["balance"] < item["price"]: return await call.message.answer("❌ Not enough balance.")
    if not item["stock"]: return await call.message.answer("🚫 Out of stock!")

    product = item["stock"].pop(0)
    u["balance"] -= item["price"]
    save_json(USERS_FILE, users)
    save_json(PRODUCTS_FILE, products)

    await call.message.answer(
        f"✅ Purchase Successful!\n🎁 {pname}\n{product}\n━━━━━━━━━━━━━━━━━━━━━━\n💬 Support: {ADMIN}"
    )

# ---------------- Bonus -----------------
@dp.callback_query_handler(lambda c: c.data == "bonus")
async def daily_bonus(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    today = str(datetime.date.today())
    if users[uid]["bonus_date"] == today:
        await call.message.answer("❌ You already claimed your daily bonus today!")
        return
    users[uid]["bonus_date"] = today
    users[uid]["balance"] += 5
    save_json(USERS_FILE, users)
    await call.message.answer("🎁 Daily Bonus Added +5৳")

# ---------------- Referral -----------------
@dp.callback_query_handler(lambda c: c.data == "ref")
async def ref_link(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    link = f"https://t.me/PowerPointStoreBot?start=ref_{uid}"
    await call.message.answer(f"👥 Invite & Earn 20৳!\nYour link: {link}")

# ---------------- Admin Commands -----------------
@dp.message_handler(commands=["adminpanel"])
async def admin_panel(msg: types.Message):
    if msg.from_user.username != ADMIN.replace("@",""): return
    await msg.reply(
        "👑 ADMIN PANEL\n━━━━━━━━━━━━━━━━━━━━━━\n"
        "📦 /addproduct <name> <price>\n"
        "📥 /addstock <name> + lines\n"
        "💰 /approve <id> <amount>\n"
        "🔍 /checkuser <id>\n"
        "📢 /broadcast <msg>\n"
        "📊 /stats\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )

@dp.message_handler(commands=["addproduct"])
async def add_product(msg: types.Message):
    if msg.from_user.username != ADMIN.replace("@",""): return
    try:
        _, name, price = msg.text.split(" ",2)
        products[name] = {"price": int(price), "stock":[]}
        save_json(PRODUCTS_FILE, products)
        await msg.reply(f"✅ Added {name} for {price}৳")
    except: await msg.reply("Usage: /addproduct Name Price")

@dp.message_handler(commands=["addstock"])
async def add_stock(msg: types.Message):
    if msg.from_user.username != ADMIN.replace("@",""): return
    lines = msg.text.split("\n")
    if len(lines)<2: return await msg.reply("Usage:\n/addstock Product\nitem1\nitem2")
    name = lines[0].split(" ")[1]
    if name not in products: return await msg.reply("Product not found.")
    for i in lines[1:]: products[name]["stock"].append(i)
    save_json(PRODUCTS_FILE, products)
    await msg.reply(f"✅ Added {len(lines)-1} stock to {name}")

@dp.message_handler(commands=["approve"])
async def approve(msg: types.Message):
    if msg.from_user.username != ADMIN.replace("@",""): return
    try:
        _, uid, amt = msg.text.split(" ")
        users[uid]["balance"] += int(amt)
        save_json(USERS_FILE, users)
        await msg.reply(f"✅ Added {amt}৳ to {uid}")
        await bot.send_message(uid, f"✅ Deposit Approved!\n💰 +{amt}৳ added to your balance.")
    except: await msg.reply("Usage: /approve <id> <amount>")

@dp.message_handler(commands=["checkuser"])
async def check_user(msg: types.Message):
    if msg.from_user.username != ADMIN.replace("@",""): return
    try:
        _, uid = msg.text.split(" ")
        u = users[uid]
        await msg.reply(
            f"👤 @{u['username']}\n💰 {u['balance']}৳\n👥 User #{u['user_no']}\n📅 {u['join']}\n🎁 Ref: {u['ref']}"
        )
    except: await msg.reply("Usage: /checkuser <id>")

@dp.message_handler(commands=["broadcast"])
async def broadcast(msg: types.Message):
    if msg.from_user.username != ADMIN.replace("@",""): return
    text = msg.text.replace("/broadcast","").strip()
    if not text: return await msg.reply("Usage: /broadcast message")
    c=0
    for uid in users:
        try:
            await bot.send_message(uid,text)
            c+=1
            await asyncio.sleep(0.05)
        except: pass
    await msg.reply(f"📢 Broadcast sent to {c} users.")

@dp.message_handler(commands=["stats"])
async def stats(msg: types.Message):
    if msg.from_user.username != ADMIN.replace("@",""): return
    total_users = len(users)
    total_products = len(products)
    total_stock = sum(len(p['stock']) for p in products.values())
    await msg.reply(
        f"📊 Stats\n━━━━━━━━━━━━━━━━━━━━━━\n👥 Users: {total_users}\n📦 Products: {total_products}\n🧾 Stock Items: {total_stock}"
    )

# ---------------- Run -----------------
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
