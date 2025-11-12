# ===============================================
# 💎 Power Point Break Store Bot
# Fully Custom Telegram Store System
# By @MinexxProo
# ===============================================

import json, asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

TOKEN = "8347151795:AAGjhhVBd8t_CJ90BKm6nM2ZyMg6kvDvg2M"  # তোমার BotFather token এখানে দিও
ADMIN = "@MinexxProo"
PAYMENT_NUMBER = "01877576843"

# Database ফাইল
USERS_FILE = "users.json"
PRODUCTS_FILE = "products.json"

# -----------------------------------------------
# JSON Load & Save
# -----------------------------------------------
def load_json(file):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return {}

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

users = load_json(USERS_FILE)
products = load_json(PRODUCTS_FILE)

# -----------------------------------------------
# Aiogram Setup
# -----------------------------------------------
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# -----------------------------------------------
# Helper Functions
# -----------------------------------------------
def user_register(user):
    uid = str(user.id)
    if uid not in users:
        users[uid] = {
            "username": user.username or "unknown",
            "balance": 0,
            "orders": [],
            "user_no": len(users) + 1
        }
        save_json(USERS_FILE, users)

# -----------------------------------------------
# /start
# -----------------------------------------------
@dp.message_handler(commands=["start"])
async def start_cmd(msg: types.Message):
    user_register(msg.from_user)
    u = users[str(msg.from_user.id)]
    text = (
        f"┏━━━━━━━━━━━━━━━━━━━━━━┓\n"
        f"👤 @{u['username']}\n"
        f"🆔 ID: {msg.from_user.id}\n"
        f"💰 Balance: {u['balance']}৳\n"
        f"👥 User No: {u['user_no']}\n"
        f"┗━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"🛍️ Welcome to Power Point Break Store 🏪\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Choose an option 👇"
    )

    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🛒 Store", callback_data="store"),
        InlineKeyboardButton("💰 Deposit", callback_data="deposit"),
        InlineKeyboardButton("📦 My Orders", callback_data="orders"),
        InlineKeyboardButton("📩 Support", url=f"https://t.me/{ADMIN.replace('@','')}")
    )
    await msg.answer(text, reply_markup=kb)

# -----------------------------------------------
# Store View
# -----------------------------------------------
@dp.callback_query_handler(lambda c: c.data == "store")
async def open_store(call: types.CallbackQuery):
    if not products:
        await call.message.edit_text("🛍️ Store is empty.\nAdd products from admin panel.")
        return

    txt = "🛍️ Power Point Break Store\n━━━━━━━━━━━━━━━━━━━━━━\n"
    kb = InlineKeyboardMarkup(row_width=1)
    for name, data in products.items():
        txt += f"🎁 {name} — {data['price']}৳\n"
        kb.add(InlineKeyboardButton(f"💎 Buy {name}", callback_data=f"buy_{name}"))
    await call.message.edit_text(txt, reply_markup=kb)

# -----------------------------------------------
# Deposit System
# -----------------------------------------------
@dp.callback_query_handler(lambda c: c.data == "deposit")
async def deposit_menu(call: types.CallbackQuery):
    text = (
        f"📥 Send Money to any of the following ↓\n\n"
        f"📱 bKash (Send Money): {PAYMENT_NUMBER}\n"
        f"💸 Nagad (Send Money): {PAYMENT_NUMBER}\n"
        f"💰 Upay (Send Money): {PAYMENT_NUMBER}\n"
        f"🏦 Rocket (Send Money): {PAYMENT_NUMBER}\n\n"
        "Then type your Transaction ID below 👇\n"
        "Example: TXN987654321"
    )
    await call.message.edit_text(text)

@dp.message_handler(lambda m: m.text.startswith("TXN") or m.text.startswith("txn"))
async def handle_trx(msg: types.Message):
    uid = str(msg.from_user.id)
    user_register(msg.from_user)
    trx = msg.text.strip()
    text = (
        f"💸 New Deposit Request\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 @{msg.from_user.username}\n"
        f"🆔 {msg.from_user.id}\n"
        f"💰 Pending amount (manual check)\n"
        f"🏦 Payment Number: {PAYMENT_NUMBER}\n"
        f"🧾 TRX ID: {trx}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"[Admin please verify manually]"
    )
    await bot.send_message(ADMIN.replace("@", ""), text)
    await msg.reply("✅ Deposit request sent! Please wait for admin approval.")

# -----------------------------------------------
# Buy Product
# -----------------------------------------------
@dp.callback_query_handler(lambda c: c.data.startswith("buy_"))
async def buy_product(call: types.CallbackQuery):
    product_name = call.data.replace("buy_", "")
    uid = str(call.from_user.id)
    user_register(call.from_user)
    user = users[uid]

    if product_name not in products:
        await call.answer("Product not found.", show_alert=True)
        return

    product = products[product_name]
    price = product["price"]

    if user["balance"] < price:
        await call.message.answer("❌ Not enough balance.\nPlease deposit first.")
        return

    if not product["stock"]:
        await call.message.answer("🚫 Out of stock!")
        return

    # Deliver first item
    item = product["stock"].pop(0)
    user["balance"] -= price
    user["orders"].append({"item": product_name, "price": price})
    save_json(USERS_FILE, users)
    save_json(PRODUCTS_FILE, products)

    await call.message.answer(
        f"✅ Payment Successful!\n🎁 Product: {product_name}\n{item}\n\n"
        f"💬 Support: {ADMIN}\n⚡ Hosted by Power Point Break"
    )

# -----------------------------------------------
# Admin Commands
# -----------------------------------------------
@dp.message_handler(commands=["addproduct"])
async def add_product(msg: types.Message):
    if msg.from_user.username != ADMIN.replace("@", ""):
        return
    try:
        _, name, price = msg.text.split(" ", 2)
        products[name] = {"price": int(price), "stock": []}
        save_json(PRODUCTS_FILE, products)
        await msg.reply(f"✅ Added {name} for {price}৳")
    except:
        await msg.reply("Usage: /addproduct Name Price")

@dp.message_handler(commands=["addstock"])
async def add_stock(msg: types.Message):
    if msg.from_user.username != ADMIN.replace("@", ""):
        return
    try:
        _, name, *lines = msg.text.split("\n")
        if name not in products:
            await msg.reply("❌ Product not found.")
            return
        for l in lines:
            products[name]["stock"].append(l)
        save_json(PRODUCTS_FILE, products)
        await msg.reply(f"✅ Added {len(lines)} stock items to {name}")
    except:
        await msg.reply("Usage:\n/addstock ProductName\nemail:pass\nemail2:pass2")

@dp.message_handler(commands=["checkuser"])
async def check_user(msg: types.Message):
    if msg.from_user.username != ADMIN.replace("@", ""):
        return
    try:
        _, uid = msg.text.split(" ", 1)
        u = users.get(uid.strip())
        if not u:
            await msg.reply("❌ User not found.")
            return
        await msg.reply(
            f"👤 @{u['username']}\n🆔 {uid}\n💰 Balance: {u['balance']}৳\n"
            f"📦 Orders: {len(u['orders'])}\n🏅 User No: {u['user_no']}"
        )
    except:
        await msg.reply("Usage: /checkuser <id>")

# -----------------------------------------------
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
