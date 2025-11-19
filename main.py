import os
import sys
import json
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait
from datetime import datetime, timedelta
import asyncio

os.makedirs("saved_media/photos", exist_ok=True)
os.makedirs("saved_media/videos", exist_ok=True)

def get_required_env(key, name):
    value = os.getenv(key)
    if not value:
        print(f"[X] Error: {key} environment variable is required")
        print(f"[i] Please set your {name} in the environment variables")
        sys.exit(1)
    return value

api_id = int(get_required_env("TELEGRAM_API_ID", "Telegram API ID"))
api_hash = get_required_env("TELEGRAM_API_HASH", "Telegram API Hash")
phone_number = get_required_env("TELEGRAM_PHONE_NUMBER", "phone number")
base_name = os.getenv("BASE_NAME", "User")

app = Client("telegram_bot", api_id=api_id, api_hash=api_hash, phone_number=phone_number)

spam_active = False
typing_enabled = True
view_once_enabled = True
spam_enabled = True
name_timer_enabled = True
live_typing_enabled = True
auto_reply_enabled = True

auto_reply_data = {
    "greetings": ["سلام", "درود", "hello", "hi", "hey", "سلامت", "هلو", "های", "صبح بخیر", "عصر بخیر", "شب بخیر"],
    "response": "علیک سلام"
}

@app.on_message(filters.command("spam") & filters.me)
async def spam_command(client, message):
    global spam_active

    if not spam_enabled:
        await message.edit("❌ قابلیت اسپم غیرفعال است. برای فعال‌سازی از `/toggle spam` استفاده کنید.")
        return

    try:
        parts = message.text.split(maxsplit=3)

        if len(parts) == 1:
            chat_name = message.chat.title if hasattr(message.chat, 'title') and message.chat.title else (message.chat.first_name or "این چت")
            await message.edit(
                f"📤 **راهنمای استفاده Spam:**\n\n"
                f"**در این چت ({chat_name}):**\n"
                f"`/spam [تعداد] [تاخیر] [متن]`\n"
                f"مثال: `/spam 5 1 سلام به همه`\n\n"
                f"**برای ارسال به Saved Messages:**\n"
                f"`/spam me [تعداد] [تاخیر] [متن]`\n\n"
                f"**توقف ارسال:**\n"
                f"`/stopspam`"
            )
            return

        target_chat = message.chat.id
        offset = 0

        if parts[1].lower() == "me":
            target_chat = "me"
            offset = 1
            if len(parts) < 4:
                await message.edit("❌ فرمت: `/spam me [تعداد] [تاخیر] [متن]`")
                return

        if len(parts) < 3 + offset:
            await message.edit("❌ فرمت: `/spam [تعداد] [تاخیر] [متن]`")
            return

        count = int(parts[1 + offset])
        delay = float(parts[2 + offset])
        spam_message = parts[3 + offset] if len(parts) > 3 + offset else "سلام 👋"

        spam_active = True
        await message.delete()

        for i in range(count):
            if not spam_active:
                await client.send_message("me", "⛔ ارسال پیام متوقف شد!")
                break

            try:
                await client.send_message(target_chat, spam_message)
                print(f"[📤] Sent spam message {i+1}/{count} to chat {target_chat}")

                if i < count - 1:
                    await asyncio.sleep(delay)
            except FloodWait as e:
                print(f"[⏳] FloodWait: sleeping {e.value}s")
                await asyncio.sleep(e.value)
            except Exception as e:
                print(f"[!] Spam error: {e}")
                await client.send_message("me", f"❌ خطا در ارسال: {str(e)}")
                break

        spam_active = False
        await client.send_message("me", f"✅ ارسال {count} پیام به {'Saved Messages' if target_chat == 'me' else 'گروه'} تکمیل شد!")

    except ValueError:
        await message.edit("❌ خطا! تعداد و تاخیر باید عدد باشند!")
    except Exception as e:
        await message.edit(f"❌ خطا: {str(e)}")

@app.on_message(filters.command("stopspam") & filters.me)
async def stop_spam_command(client, message):
    global spam_active
    spam_active = False
    await message.edit("⛔ ارسال پیام‌های تکراری متوقف شد!")

@app.on_message(filters.command("toggle") & filters.me)
async def toggle_command(client, message):
    global typing_enabled, view_once_enabled, spam_active, spam_enabled, name_timer_enabled, live_typing_enabled, auto_reply_enabled

    if len(message.command) < 2:
        await message.edit("❌ استفاده نادرست. مثال: `/toggle typing`, `/toggle livetyping`, `/toggle viewonce`, `/toggle spam`, `/toggle name`, `/toggle autoreply`")
        return

    feature = message.command[1].lower()

    if feature == "typing":
        typing_enabled = not typing_enabled
        status = "فعال شد" if typing_enabled else "غیرفعال شد"
        await message.edit(f"✅ قابلیت تایپ در چت‌ها {status}.")
    elif feature == "livetyping":
        live_typing_enabled = not live_typing_enabled
        status = "فعال شد" if live_typing_enabled else "غیرفعال شد"
        await message.edit(f"✅ قابلیت تایپ زنده {status}.")
    elif feature == "viewonce":
        view_once_enabled = not view_once_enabled
        status = "فعال شد" if view_once_enabled else "غیرفعال شد"
        await message.edit(f"✅ قابلیت ذخیره مدیاهای یکبار مصرف {status}.")
    elif feature == "spam":
        if spam_active:
            await message.edit("⛔ نمی‌توان اسپم را در حین اجرا غیرفعال کرد. ابتدا از `/stopspam` استفاده کنید.")
        else:
            spam_enabled = not spam_enabled
            status = "فعال شد" if spam_enabled else "غیرفعال شد"
            await message.edit(f"✅ قابلیت ارسال اسپم {status}.")
    elif feature == "name":
        name_timer_enabled = not name_timer_enabled
        status = "فعال شد" if name_timer_enabled else "غیرفعال شد"
        await message.edit(f"✅ قابلیت تایمر کنار نام {status}.")
        if not name_timer_enabled:
            try:
                await app.update_profile(first_name=base_name)
                print(f"[✓] Name reset to: {base_name}")
            except Exception as e:
                print(f"[X] Error resetting name: {e}")
    elif feature == "autoreply":
        auto_reply_enabled = not auto_reply_enabled
        status = "فعال شد" if auto_reply_enabled else "غیرفعال شد"
        await message.edit(f"✅ قابلیت پاسخ خودکار به سلام {status}.")
    else:
        await message.edit("❌ قابلیت نامعتبر. قابلیت‌های موجود: `typing`, `livetyping`, `viewonce`, `spam`, `name`, `autoreply`.")

@app.on_message(filters.text & filters.incoming & (filters.private | filters.group) & ~filters.me)
async def auto_reply_handler(client, message):
    if not auto_reply_enabled:
        return

    me = await client.get_me()
    if message.from_user and message.from_user.id == me.id:
        return

    text = message.text.lower().strip() if message.text else ""

    if not text:
        return

    try:
        if text in auto_reply_data["greetings"]:
            await asyncio.sleep(0.5)
            await message.reply(auto_reply_data["response"])
            
            chat_type = "private" if message.chat.type == enums.ChatType.PRIVATE else "group"
            print(f"[✅] Auto-replied 'علیک سلام' to {message.from_user.first_name} in {chat_type}")

    except Exception as e:
        print(f"[!] Auto-reply error: {e}")

@app.on_message(filters.text & filters.outgoing & ~filters.command(["spam", "stopspam", "toggle"]))
async def live_typing_handler(client, message):
    if not live_typing_enabled:
        return

    if not message.text or not message.text.startswith("."):
        return

    text = message.text[1:]

    if not text:
        return

    try:
        current_text = text[0]
        await message.edit(current_text)

        for char in text[1:]:
            await asyncio.sleep(0.1)
            current_text += char
            try:
                await message.edit(current_text)
            except Exception:
                pass

        print(f"[✍️] Live typing completed: {text}")
    except Exception as e:
        print(f"[!] Live typing error: {e}")

@app.on_message(filters.photo | filters.video)
async def message_handler(client, message):
    if not view_once_enabled:
        return

    media_type = None
    has_ttl = False

    if message.photo:
        if hasattr(message.photo, 'ttl_seconds') and message.photo.ttl_seconds:
            media_type = "photo"
            has_ttl = True

    if message.video:
        if hasattr(message.video, 'ttl_seconds') and message.video.ttl_seconds:
            media_type = "video"
            has_ttl = True

    if has_ttl and media_type:
        await save_view_once_media(message, media_type)

async def save_view_once_media(message, media_type):
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        from_user = message.from_user.username if message.from_user and message.from_user.username else "unknown"
        from_name = message.from_user.first_name if message.from_user and message.from_user.first_name else "Unknown"
        chat_name = message.chat.title or message.chat.first_name or "Unknown"
        filename = f"{timestamp}_{from_user}_{message.id}"

        if media_type == "photo":
            file_path = f"saved_media/photos/{filename}.jpg"
            await message.download(file_path)

            caption = f"📸 **عکس یکبار مصرف دریافت شد**\n\n"
            caption += f"👤 از: {from_name} (@{from_user})\n"
            caption += f"💬 چت: {chat_name}\n"
            caption += f"📅 تاریخ: {message.date.strftime('%Y-%m-%d %H:%M:%S')}\n"
            if message.caption:
                caption += f"📝 کپشن: {message.caption}"

            await app.send_photo("me", file_path, caption=caption)

        elif media_type == "video":
            file_path = f"saved_media/videos/{filename}.mp4"
            await message.download(file_path)

            caption = f"🎥 **ویدیو یکبار مصرف دریافت شد**\n\n"
            caption += f"👤 از: {from_name} (@{from_user})\n"
            caption += f"💬 چت: {chat_name}\n"
            caption += f"📅 تاریخ: {message.date.strftime('%Y-%m-%d %H:%M:%S')}\n"
            if message.caption:
                caption += f"📝 کپشن: {message.caption}"

            await app.send_video("me", file_path, caption=caption, supports_streaming=True)

        metadata = {
            "message_id": message.id,
            "from": from_user,
            "from_name": from_name,
            "chat": chat_name,
            "date": str(message.date),
            "caption": message.caption or "",
            "file_path": file_path
        }

        with open(f"{file_path}.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        print(f"[💾] Saved and sent view-once {media_type} to Saved Messages: {filename}")
    except Exception as e:
        print(f"[!] Error saving view-once media: {e}")

async def always_typing():
    dialogs_cache = []
    cache_time = 0

    while True:
        if not typing_enabled:
            await asyncio.sleep(1)
            continue

        try:
            current_time = asyncio.get_event_loop().time()

            if current_time - cache_time > 300:
                dialogs_cache = []
                async for dialog in app.get_dialogs(limit=50):
                    if dialog.chat.type in [enums.ChatType.PRIVATE, enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
                        dialogs_cache.append(dialog.chat.id)
                cache_time = current_time
                print(f"[🔄] Cached {len(dialogs_cache)} chats for typing")

            for chat_id in dialogs_cache:
                try:
                    await app.send_chat_action(chat_id, enums.ChatAction.TYPING)
                except FloodWait as e:
                    print(f"[⏳] FloodWait: sleeping {e.value}s")
                    await asyncio.sleep(e.value)
                except Exception:
                    pass

            await asyncio.sleep(5)

        except Exception as e:
            print(f"[!] Typing error: {e}")
            await asyncio.sleep(10)

async def update_name():
    while True:
        if not name_timer_enabled:
            await asyncio.sleep(1)
            continue

        try:
            now = datetime.utcnow() + timedelta(hours=4, minutes=30)
            current_time = now.strftime("%I:%M %p")
            beautiful_time = current_time.replace('0', '𝟎').replace('1', '𝟏').replace('2', '𝟐').replace('3', '𝟑').replace('4', '𝟒').replace('5', '𝟓').replace('6', '𝟔').replace('7', '𝟕').replace('8', '𝟖').replace('9', '𝟗')
            new_name = f"{base_name} • {beautiful_time}"

            await app.update_profile(first_name=new_name)
            print(f"[✓] Updated name to: {new_name}")
        except Exception as e:
            print(f"[X] Name update error: {e}")

        await asyncio.sleep(60)

async def main():
    async with app:
        print("[✓] Bot started successfully!")
        print(f"[⌨️] Always-typing feature: {'ACTIVE' if typing_enabled else 'DISABLED'}")
        print(f"[✍️] Live-typing feature: {'ACTIVE' if live_typing_enabled else 'DISABLED'}")
        print(f"[💾] View-once media saver: {'ACTIVE' if view_once_enabled else 'DISABLED'}")
        print(f"[📤] Spam feature: {'ACTIVE' if spam_enabled else 'DISABLED'}")
        print(f"[⏰] Name timer: {'ACTIVE' if name_timer_enabled else 'DISABLED'}")
        print(f"[👋] Auto-reply feature: {'ACTIVE' if auto_reply_enabled else 'DISABLED'}")

        await asyncio.gather(
            always_typing(),
            update_name()
        )

if __name__ == "__main__":
    app.run(main())
