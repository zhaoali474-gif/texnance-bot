"""
TEXNANCE VIP Bot
ربات ثبت‌نام کانال VIP تکسنانس
"""

import logging
import os
from datetime import datetime
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# ─────────────────────────────────────────────
# تنظیمات اصلی
# ─────────────────────────────────────────────
BOT_TOKEN = "8956977415:AAGqyw8U2AOxTM5RzY32RtXRU220DJxcGBQ"
ADMIN_IDS = [1202131448, 6646987873]        # لیست آیدی ادمین‌ها
ADMIN_ID = ADMIN_IDS[0]                     # ادمین اول (برای سازگاری)
SUPPORT_USERNAME = "@tex2453"
WALLET_ADDRESS = "TTH9T3rcvJKWWAkZQ9iA3fWEJK44uih2KT"
CHANNEL_LINK = "https://t.me/+BNevFpj7qhRlNmFk"

PRICE_USDT = 39
NETWORK = "TRC20"

# کدهای تخفیف فعال — کلید: کد ، مقدار: درصد تخفیف
# مثال: {"VIP20": 20, "TEXNANCE10": 10}
DISCOUNT_CODES: dict[str, int] = {}

# ─────────────────────────────────────────────
# State های مکالمه
# ─────────────────────────────────────────────
(
    MAIN_MENU,
    WAITING_DISCOUNT,
    WAITING_RECEIPT,
    SUPPORT_CHAT,
    ADMIN_BROADCAST,
    ADMIN_ADD_DISCOUNT,
    ADMIN_REMOVE_DISCOUNT,
) = range(7)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# کیبوردها
# ─────────────────────────────────────────────
def main_keyboard():
    return ReplyKeyboardMarkup(
        [
            ["💎 خرید اشتراک VIP"],
            ["🎟 کد تخفیف دارم", "📞 پشتیبانی"],
            ["ℹ️ اطلاعات اشتراک"],
        ],
        resize_keyboard=True,
    )


def admin_keyboard():
    return ReplyKeyboardMarkup(
        [
            ["📢 ارسال پیام همگانی"],
            ["➕ افزودن کد تخفیف", "➖ حذف کد تخفیف"],
            ["📋 لیست کدهای تخفیف", "🔙 بازگشت به منوی کاربر"],
        ],
        resize_keyboard=True,
    )


# ─────────────────────────────────────────────
# /start
# ─────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    context.user_data.clear()
    context.user_data["final_price"] = PRICE_USDT

    text = (
        f"👋 سلام {user.first_name} عزیز!\n\n"
        "به ربات رسمی کانال VIP **TEXNANCE** خوش آمدی 🚀\n\n"
        "📊 با اشتراک VIP دریافت می‌کنی:\n"
        "• روزانه ۱ تا ۳ سیگنال حرفه‌ای\n"
        "• دقت سیگنال‌ها: **۷۰٪ و بالاتر**\n"
        "• تحلیل‌های اختصاصی بازار\n\n"
        "💰 قیمت اشتراک ۱ ساله: **۳۹ تتر**\n\n"
        "برای شروع از منوی زیر استفاده کن 👇"
    )
    await update.message.reply_text(text, reply_markup=main_keyboard(), parse_mode="Markdown")
    return MAIN_MENU


# ─────────────────────────────────────────────
# منوی اصلی
# ─────────────────────────────────────────────
async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "💎 خرید اشتراک VIP":
        return await show_payment_info(update, context)

    elif text == "🎟 کد تخفیف دارم":
        await update.message.reply_text(
            "🎟 کد تخفیف خود را وارد کنید:",
            reply_markup=ReplyKeyboardMarkup([["❌ انصراف"]], resize_keyboard=True),
        )
        return WAITING_DISCOUNT

    elif text == "📞 پشتیبانی":
        await update.message.reply_text(
            f"📞 **پشتیبانی TEXNANCE**\n\n"
            f"برای ارتباط با پشتیبانی پیام خود را همین‌جا بنویس،\n"
            f"یا مستقیم با {SUPPORT_USERNAME} در ارتباط باش.\n\n"
            "✍️ پیامت رو بنویس:",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup([["❌ انصراف"]], resize_keyboard=True),
        )
        return SUPPORT_CHAT

    elif text == "ℹ️ اطلاعات اشتراک":
        await update.message.reply_text(
            "📋 **اطلاعات اشتراک VIP TEXNANCE**\n\n"
            "⏳ مدت: ۱ سال\n"
            "💰 قیمت: ۳۹ تتر\n"
            "🌐 شبکه پرداخت: TRC20\n"
            f"📊 سیگنال: روزانه ۱-۳ سیگنال با دقت ۷۰٪+\n\n"
            "📌 بعد از پرداخت و تأیید ادمین، لینک کانال VIP برایت ارسال می‌شود.",
            parse_mode="Markdown",
            reply_markup=main_keyboard(),
        )
        return MAIN_MENU

    # ادمین
    elif text == "🔐 پنل ادمین" and update.effective_user.id in ADMIN_IDS:
        await update.message.reply_text("پنل مدیریت:", reply_markup=admin_keyboard())
        return MAIN_MENU

    elif text == "📢 ارسال پیام همگانی" and update.effective_user.id in ADMIN_IDS:
        await update.message.reply_text(
            "📢 متن پیام همگانی را وارد کنید:",
            reply_markup=ReplyKeyboardMarkup([["❌ انصراف"]], resize_keyboard=True),
        )
        return ADMIN_BROADCAST

    elif text == "➕ افزودن کد تخفیف" and update.effective_user.id in ADMIN_IDS:
        await update.message.reply_text(
            "➕ کد تخفیف را به فرمت زیر وارد کنید:\n`CODE:PERCENT`\nمثال: `VIP20:20`",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup([["❌ انصراف"]], resize_keyboard=True),
        )
        return ADMIN_ADD_DISCOUNT

    elif text == "➖ حذف کد تخفیف" and update.effective_user.id in ADMIN_IDS:
        if not DISCOUNT_CODES:
            await update.message.reply_text("هیچ کد تخفیفی وجود ندارد.", reply_markup=admin_keyboard())
            return MAIN_MENU
        await update.message.reply_text(
            "➖ کد تخفیفی که می‌خواهید حذف شود را وارد کنید:",
            reply_markup=ReplyKeyboardMarkup([["❌ انصراف"]], resize_keyboard=True),
        )
        return ADMIN_REMOVE_DISCOUNT

    elif text == "📋 لیست کدهای تخفیف" and update.effective_user.id in ADMIN_IDS:
        if not DISCOUNT_CODES:
            msg = "هیچ کد تخفیف فعالی وجود ندارد."
        else:
            msg = "🎟 **کدهای تخفیف فعال:**\n\n"
            for code, pct in DISCOUNT_CODES.items():
                msg += f"• `{code}` — {pct}٪ تخفیف\n"
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=admin_keyboard())
        return MAIN_MENU

    elif text == "🔙 بازگشت به منوی کاربر" and update.effective_user.id in ADMIN_IDS:
        await update.message.reply_text("منوی اصلی:", reply_markup=main_keyboard())
        return MAIN_MENU

    return MAIN_MENU


# ─────────────────────────────────────────────
# نمایش اطلاعات پرداخت
# ─────────────────────────────────────────────
async def show_payment_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    final_price = context.user_data.get("final_price", PRICE_USDT)
    discount_pct = context.user_data.get("discount_pct", 0)

    discount_text = ""
    if discount_pct:
        saved = PRICE_USDT - final_price
        discount_text = f"🎟 تخفیف اعمال شده: **{discount_pct}٪** (صرفه‌جویی: {saved} تتر)\n"

    text = (
        "💎 **خرید اشتراک VIP TEXNANCE**\n\n"
        f"⏳ مدت اشتراک: ۱ سال\n"
        f"📊 روزانه ۱-۳ سیگنال با دقت ۷۰٪+\n\n"
        f"💰 مبلغ قابل پرداخت: **{final_price} تتر**\n"
        f"{discount_text}"
        f"🌐 شبکه: **TRC20 (TRON)**\n\n"
        f"📋 **آدرس کیف پول:**\n"
        f"`{WALLET_ADDRESS}`\n\n"
        "⚠️ **توجه مهم:**\n"
        "• فقط از شبکه TRC20 واریز کنید\n"
        "• پس از واریز، اسکرین‌شات فیش را ارسال کنید\n"
        "• تأیید توسط ادمین انجام می‌شود\n\n"
        "📸 **اسکرین‌شات پرداخت را ارسال کنید:**"
    )

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup([["❌ انصراف"]], resize_keyboard=True),
    )
    return WAITING_RECEIPT


# ─────────────────────────────────────────────
# کد تخفیف
# ─────────────────────────────────────────────
async def handle_discount_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "❌ انصراف":
        await update.message.reply_text("برگشت به منوی اصلی.", reply_markup=main_keyboard())
        return MAIN_MENU

    code = update.message.text.strip().upper()

    if code in DISCOUNT_CODES:
        pct = DISCOUNT_CODES[code]
        discounted = round(PRICE_USDT * (1 - pct / 100), 2)
        context.user_data["discount_pct"] = pct
        context.user_data["final_price"] = discounted
        context.user_data["discount_code"] = code

        await update.message.reply_text(
            f"✅ کد تخفیف **{code}** اعمال شد!\n"
            f"💰 قیمت جدید: **{discounted} تتر** (به جای {PRICE_USDT} تتر)\n\n"
            "برای ادامه خرید روی «💎 خرید اشتراک VIP» بزنید.",
            parse_mode="Markdown",
            reply_markup=main_keyboard(),
        )
    else:
        await update.message.reply_text(
            "❌ کد تخفیف نامعتبر است.\n"
            "لطفاً کد را بررسی کرده و دوباره وارد کنید.",
            reply_markup=ReplyKeyboardMarkup([["❌ انصراف"]], resize_keyboard=True),
        )
        return WAITING_DISCOUNT

    return MAIN_MENU


# ─────────────────────────────────────────────
# دریافت فیش پرداخت
# ─────────────────────────────────────────────
async def handle_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text and update.message.text == "❌ انصراف":
        await update.message.reply_text("برگشت به منوی اصلی.", reply_markup=main_keyboard())
        return MAIN_MENU

    if not update.message.photo and not update.message.document:
        await update.message.reply_text(
            "⚠️ لطفاً **تصویر** اسکرین‌شات پرداخت را ارسال کنید.",
            parse_mode="Markdown",
        )
        return WAITING_RECEIPT

    user = update.effective_user
    final_price = context.user_data.get("final_price", PRICE_USDT)
    discount_code = context.user_data.get("discount_code", "—")

    # پیام به ادمین
    admin_text = (
        f"🔔 **درخواست اشتراک جدید**\n\n"
        f"👤 نام: {user.full_name}\n"
        f"🆔 یوزرنیم: @{user.username or '—'}\n"
        f"🔢 آیدی: `{user.id}`\n"
        f"💰 مبلغ پرداختی: {final_price} تتر\n"
        f"🎟 کد تخفیف: {discount_code}\n"
        f"🕐 زمان: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        f"برای تأیید یا رد کردن از دکمه‌ها استفاده کنید:"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ تأیید و ارسال لینک", callback_data=f"approve_{user.id}"),
            InlineKeyboardButton("❌ رد کردن", callback_data=f"reject_{user.id}"),
        ]
    ])

    for admin in ADMIN_IDS:
        try:
            if update.message.photo:
                await context.bot.send_photo(
                    chat_id=admin,
                    photo=update.message.photo[-1].file_id,
                    caption=admin_text,
                    parse_mode="Markdown",
                    reply_markup=keyboard,
                )
            else:
                await context.bot.send_document(
                    chat_id=admin,
                    document=update.message.document.file_id,
                    caption=admin_text,
                    parse_mode="Markdown",
                    reply_markup=keyboard,
                )
        except Exception as e:
            logger.error(f"Error sending to admin {admin}: {e}")

    await update.message.reply_text(
        "✅ **فیش پرداخت دریافت شد!**\n\n"
        "⏳ در حال بررسی توسط ادمین...\n"
        "معمولاً ظرف چند ساعت تأیید می‌شود.\n\n"
        "پس از تأیید، لینک کانال VIP برایتان ارسال می‌شود 🎉",
        parse_mode="Markdown",
        reply_markup=main_keyboard(),
    )
    context.user_data.clear()
    context.user_data["final_price"] = PRICE_USDT
    return MAIN_MENU


# ─────────────────────────────────────────────
# تأیید / رد توسط ادمین (Callback)
# ─────────────────────────────────────────────
async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if update.effective_user.id not in ADMIN_IDS:
        await query.answer("شما دسترسی ادمین ندارید.", show_alert=True)
        return

    data = query.data
    action, user_id_str = data.split("_", 1)
    user_id = int(user_id_str)

    if action == "approve":
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    "🎉 **تبریک! پرداخت شما تأیید شد.**\n\n"
                    "💎 به کانال VIP TEXNANCE خوش آمدید!\n\n"
                    f"🔗 لینک کانال اختصاصی شما:\n{CHANNEL_LINK}\n\n"
                    "📊 روزانه ۱-۳ سیگنال با دقت ۷۰٪+ دریافت خواهید کرد.\n"
                    f"📞 پشتیبانی: {SUPPORT_USERNAME}"
                ),
                parse_mode="Markdown",
            )
            await query.edit_message_caption(
                caption=query.message.caption + "\n\n✅ **تأیید شد — لینک ارسال گردید**",
                parse_mode="Markdown",
            )
        except Exception as e:
            await query.message.reply_text(f"خطا در ارسال پیام: {e}")

    elif action == "reject":
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    "❌ **پرداخت شما تأیید نشد.**\n\n"
                    "ممکن است مشکلی در فیش یا مبلغ وجود داشته باشد.\n"
                    f"لطفاً با پشتیبانی تماس بگیرید: {SUPPORT_USERNAME}"
                ),
                parse_mode="Markdown",
            )
            await query.edit_message_caption(
                caption=query.message.caption + "\n\n❌ **رد شد**",
                parse_mode="Markdown",
            )
        except Exception as e:
            await query.message.reply_text(f"خطا: {e}")


# ─────────────────────────────────────────────
# پشتیبانی
# ─────────────────────────────────────────────
async def handle_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "❌ انصراف":
        await update.message.reply_text("برگشت به منوی اصلی.", reply_markup=main_keyboard())
        return MAIN_MENU

    user = update.effective_user
    support_msg = (
        f"📩 **پیام پشتیبانی جدید**\n\n"
        f"👤 {user.full_name} | @{user.username or '—'} | `{user.id}`\n\n"
        f"💬 {update.message.text}"
    )

    try:
        for admin in ADMIN_IDS:
            await context.bot.send_message(chat_id=admin, text=support_msg, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Support message error: {e}")

    await update.message.reply_text(
        "✅ پیام شما به پشتیبانی ارسال شد.\n"
        f"همچنین می‌توانید مستقیم با {SUPPORT_USERNAME} در ارتباط باشید.",
        reply_markup=main_keyboard(),
    )
    return MAIN_MENU


# ─────────────────────────────────────────────
# پنل ادمین — Broadcast
# ─────────────────────────────────────────────
async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "❌ انصراف":
        await update.message.reply_text("لغو شد.", reply_markup=admin_keyboard())
        return MAIN_MENU

    # ذخیره یوزرآیدی‌ها نیاز به دیتابیس دارد — این نمونه‌ای ساده است
    await update.message.reply_text(
        "⚠️ برای broadcast نیاز به دیتابیس کاربران دارید.\n"
        "در نسخه پیشرفته با SQLite یا PostgreSQL قابل پیاده‌سازی است.",
        reply_markup=admin_keyboard(),
    )
    return MAIN_MENU


# ─────────────────────────────────────────────
# ادمین — افزودن کد تخفیف
# ─────────────────────────────────────────────
async def admin_add_discount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "❌ انصراف":
        await update.message.reply_text("لغو شد.", reply_markup=admin_keyboard())
        return MAIN_MENU

    try:
        parts = update.message.text.strip().upper().split(":")
        code = parts[0].strip()
        pct = int(parts[1].strip())
        if not (1 <= pct <= 100):
            raise ValueError
        DISCOUNT_CODES[code] = pct
        await update.message.reply_text(
            f"✅ کد تخفیف **{code}** با **{pct}٪** تخفیف اضافه شد.",
            parse_mode="Markdown",
            reply_markup=admin_keyboard(),
        )
    except Exception:
        await update.message.reply_text(
            "❌ فرمت اشتباه. مثال: `VIP20:20`",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup([["❌ انصراف"]], resize_keyboard=True),
        )
        return ADMIN_ADD_DISCOUNT

    return MAIN_MENU


# ─────────────────────────────────────────────
# ادمین — حذف کد تخفیف
# ─────────────────────────────────────────────
async def admin_remove_discount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "❌ انصراف":
        await update.message.reply_text("لغو شد.", reply_markup=admin_keyboard())
        return MAIN_MENU

    code = update.message.text.strip().upper()
    if code in DISCOUNT_CODES:
        del DISCOUNT_CODES[code]
        await update.message.reply_text(
            f"✅ کد تخفیف **{code}** حذف شد.",
            parse_mode="Markdown",
            reply_markup=admin_keyboard(),
        )
    else:
        await update.message.reply_text(
            f"❌ کد **{code}** یافت نشد.",
            parse_mode="Markdown",
            reply_markup=admin_keyboard(),
        )
    return MAIN_MENU


# ─────────────────────────────────────────────
# دستور /admin
# ─────────────────────────────────────────────
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("⛔ دسترسی مجاز نیست.")
        return MAIN_MENU
    await update.message.reply_text("🔐 پنل مدیریت TEXNANCE:", reply_markup=admin_keyboard())
    return MAIN_MENU


# ─────────────────────────────────────────────
# راه‌اندازی
# ─────────────────────────────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MAIN_MENU: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_handler),
            ],
            WAITING_DISCOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_discount_code),
            ],
            WAITING_RECEIPT: [
                MessageHandler(filters.PHOTO | filters.Document.ALL, handle_receipt),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_receipt),
            ],
            SUPPORT_CHAT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_support),
            ],
            ADMIN_BROADCAST: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_broadcast),
            ],
            ADMIN_ADD_DISCOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_add_discount),
            ],
            ADMIN_REMOVE_DISCOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_remove_discount),
            ],
        },
        fallbacks=[CommandHandler("start", start), CommandHandler("admin", admin_command)],
    )

    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(admin_callback, pattern=r"^(approve|reject)_\d+$"))
    app.add_handler(CommandHandler("admin", admin_command))

    print("✅ ربات TEXNANCE در حال اجراست...")
    app.run_polling()


if __name__ == "__main__":
    main()
