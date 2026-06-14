import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

TOKEN = "8660485711:AAEh7iKcMFbH5G1yE8P3scZtFAgL_V7eyMs"

logging.basicConfig(level=logging.INFO)

# ── WORD GAME DATA ──
WORDS = [
    "سیب","باران","کتاب","دریا","آسمان","گربه","خورشید","ماه","ستاره","درخت",
    "گل","برگ","پرنده","آتش","یخ","باد","صخره","رودخانه","کوه","جنگل",
    "شیر","ببر","فیل","اسب","گرگ","روباه","خرگوش","ماهی","عقاب","پروانه"
]

RIDDLES = [
    {"q":"هر چی بیشتر ازش بکشی، بزرگ‌تر میشه. چیه؟","a":"چاه"},
    {"q":"دندون داره ولی گاز نمیگیره. چیه؟","a":"شانه"},
    {"q":"همیشه جلوته ولی نمیتونی ببینیش. چیه؟","a":"آینده"},
    {"q":"هر چی بیشتر خشک بشه، بیشتر تر میشه. چیه؟","a":"حوله"},
    {"q":"بدون در و پنجره داره ولی همه توش زندگی میکنن. چیه؟","a":"تخم مرغ"},
    {"q":"می‌ره ولی هیچ‌وقت برنمیگرده. چیه؟","a":"وقت"},
    {"q":"سبکه ولی هیچکس نمیتونه زیاد نگهش داره. چیه؟","a":"نفس"},
    {"q":"صدا داره ولی دهن نداره. چیه؟","a":"طبل"},
]

# user game states
user_states = {}

# ── HELPERS ──
def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎯 حدس عدد", callback_data="game_number"),
         InlineKeyboardButton("❓ معما", callback_data="game_riddle")],
        [InlineKeyboardButton("🔤 بازی کلمه", callback_data="game_word"),
         InlineKeyboardButton("🎲 تاس", callback_data="game_dice")],
        [InlineKeyboardButton("🏆 امتیاز من", callback_data="score")],
    ])

def get_score(ctx, uid):
    return ctx.bot_data.get(f"score_{uid}", 0)

def add_score(ctx, uid, n):
    ctx.bot_data[f"score_{uid}"] = get_score(ctx, uid) + n

# ── COMMANDS ──
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name
    await update.message.reply_text(
        f"سلام {name}! 👋\nبه ربات بازی Mury خوش اومدی 🎮\n\nیه بازی انتخاب کن:",
        reply_markup=main_menu_keyboard()
    )

async def menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("منوی اصلی:", reply_markup=main_menu_keyboard())

# ── CALLBACKS ──
async def callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    data = q.data

    # ── NUMBER GAME ──
    if data == "game_number":
        n = random.randint(1, 100)
        user_states[uid] = {"game": "number", "answer": n, "tries": 0}
        await q.edit_message_text(
            "🎯 یه عدد بین ۱ تا ۱۰۰ انتخاب کردم!\nحدس بزن چنده؟ (عدد بفرست)",
        )

    # ── RIDDLE ──
    elif data == "game_riddle":
        riddle = random.choice(RIDDLES)
        user_states[uid] = {"game": "riddle", "answer": riddle["a"]}
        await q.edit_message_text(
            f"❓ معما:\n\n{riddle['q']}\n\nجوابت رو بنویس 👇",
        )

    # ── WORD GAME ──
    elif data == "game_word":
        word = random.choice(WORDS)
        user_states[uid] = {"game": "word", "current": word, "used": [word]}
        await q.edit_message_text(
            f"🔤 بازی کلمه!\nقانون: کلمه‌ای بفرست که با آخرین حرف کلمه قبلی شروع بشه.\n\n"
            f"من شروع می‌کنم: **{word}**\n\nحرف بعدی: **{word[-1]}**",
            parse_mode="Markdown"
        )

    # ── DICE ──
    elif data == "game_dice":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎲 رول کن!", callback_data="dice_roll"),
             InlineKeyboardButton("🔮 شانست رو ببین", callback_data="dice_luck")],
            [InlineKeyboardButton("🔙 منو", callback_data="main_menu")]
        ])
        await q.edit_message_text("🎲 بازی تاس!\nچیکار کنم؟", reply_markup=keyboard)

    elif data == "dice_roll":
        d1, d2 = random.randint(1,6), random.randint(1,6)
        total = d1+d2
        msg = f"🎲 {d1} + 🎲 {d2} = **{total}**\n"
        if total == 12: msg += "\n🏆 عالیه! ماکزیمم!"
        elif total >= 10: msg += "\n🔥 خیلی خوب!"
        elif total <= 3: msg += "\n😬 بدشانسی!"
        else: msg += "\n😊 بد نیست!"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎲 دوباره", callback_data="dice_roll"),
             InlineKeyboardButton("🔙 منو", callback_data="main_menu")]
        ])
        await q.edit_message_text(msg, reply_markup=keyboard, parse_mode="Markdown")

    elif data == "dice_luck":
        fortunes = [
            "⭐ امروز روزت خوبه! ریسک کن!",
            "🌧️ یه کم محتاط باش امروز...",
            "🚀 انرژیت بالاست، بزن بریم!",
            "😴 امروز استراحت کن بهتره",
            "💰 احتمال موفقیتت زیاده!",
            "🎯 تمرکزت عالیه، هر کاری بکنی موفق میشی!",
        ]
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔮 دوباره", callback_data="dice_luck"),
             InlineKeyboardButton("🔙 منو", callback_data="main_menu")]
        ])
        await q.edit_message_text(
            f"🔮 فال امروزت:\n\n{random.choice(fortunes)}",
            reply_markup=keyboard
        )

    # ── SCORE ──
    elif data == "score":
        s = get_score(ctx, uid)
        await q.edit_message_text(
            f"🏆 امتیاز تو: **{s}** امتیاز\n\n"
            f"{'🥇 عالی!' if s>=50 else '🎮 بیشتر بازی کن تا امتیاز بگیری!'}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 منو", callback_data="main_menu")]]),
            parse_mode="Markdown"
        )

    elif data == "main_menu":
        await q.edit_message_text("منوی اصلی:", reply_markup=main_menu_keyboard())

# ── MESSAGE HANDLER ──
async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text.strip()
    state = user_states.get(uid)

    if not state:
        await update.message.reply_text("از منو یه بازی انتخاب کن 👇", reply_markup=main_menu_keyboard())
        return

    game = state["game"]

    # ── NUMBER GAME ──
    if game == "number":
        try:
            guess = int(text)
        except:
            await update.message.reply_text("❌ لطفاً یه عدد بفرست!")
            return
        answer = state["answer"]
        state["tries"] += 1
        tries = state["tries"]

        if guess == answer:
            pts = max(10, 50 - tries*5)
            add_score(ctx, uid, pts)
            user_states.pop(uid)
            await update.message.reply_text(
                f"🎉 آفرین! درسته! عدد {answer} بود!\n"
                f"در {tries} تلاش پیداش کردی!\n+{pts} امتیاز 🏆",
                reply_markup=main_menu_keyboard()
            )
        elif tries >= 10:
            user_states.pop(uid)
            await update.message.reply_text(
                f"😢 تموم شد! عدد {answer} بود!\nدوباره امتحان کن 👇",
                reply_markup=main_menu_keyboard()
            )
        elif guess < answer:
            await update.message.reply_text(f"📈 بیشتر! ({tries}/10 تلاش)")
        else:
            await update.message.reply_text(f"📉 کمتر! ({tries}/10 تلاش)")

    # ── RIDDLE ──
    elif game == "riddle":
        answer = state["answer"].lower().strip()
        if text.lower().strip() == answer or answer in text.lower():
            add_score(ctx, uid, 20)
            user_states.pop(uid)
            await update.message.reply_text(
                f"✅ آفرین! درسته! جواب «{state['answer']}» بود!\n+20 امتیاز 🏆",
                reply_markup=main_menu_keyboard()
            )
        else:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("💡 جواب رو ببین", callback_data="riddle_answer"),
                 InlineKeyboardButton("🔙 منو", callback_data="main_menu")]
            ])
            await update.message.reply_text("❌ اشتباهه! دوباره فکر کن 🤔", reply_markup=keyboard)

    # ── WORD GAME ──
    elif game == "word":
        current = state["current"]
        last_char = current[-1]
        used = state["used"]

        if not text[0] == last_char:
            await update.message.reply_text(
                f"❌ باید با حرف «{last_char}» شروع بشه!\nدوباره امتحان کن 👇"
            )
            return
        if text in used:
            await update.message.reply_text("❌ این کلمه قبلاً استفاده شده!")
            return
        if len(text) < 2:
            await update.message.reply_text("❌ کلمه باید حداقل ۲ حرف داشته باشه!")
            return

        # bot responds
        used.append(text)
        add_score(ctx, uid, 5)
        bot_last = text[-1]
        candidates = [w for w in WORDS if w[0]==bot_last and w not in used]

        if not candidates:
            user_states.pop(uid)
            await update.message.reply_text(
                f"🎉 بردی! من کلمه‌ای با «{bot_last}» ندارم!\n+10 امتیاز اضافه 🏆",
                reply_markup=main_menu_keyboard()
            )
            add_score(ctx, uid, 10)
            return

        bot_word = random.choice(candidates)
        used.append(bot_word)
        state["current"] = bot_word

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🏳️ تسلیم", callback_data="main_menu")]
        ])
        await update.message.reply_text(
            f"✅ قبول!\nمن: **{bot_word}**\n\nحالا کلمه‌ای با «{bot_word[-1]}» بفرست 👇",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )

async def riddle_answer_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    state = user_states.get(uid)
    if state and state["game"] == "riddle":
        ans = state["answer"]
        user_states.pop(uid)
        await q.edit_message_text(
            f"💡 جواب: **{ans}**\n\nدفعه بعد بهتر میشی! 💪",
            reply_markup=main_menu_keyboard(),
            parse_mode="Markdown"
        )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CallbackQueryHandler(riddle_answer_cb, pattern="riddle_answer"))
    app.add_handler(CallbackQueryHandler(callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Mury Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
