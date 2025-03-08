import os
from telebot import TeleBot, types
from create_db import User, Video, session

API_TOKEN = ''
bot = TeleBot(API_TOKEN)
UPLOAD_FOLDER = 'uploaded_videos'
"--------------------------------------------------------------------------------"
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    parent_id = message.text.split()[1] if len(message.text.split()) > 1 else None
    
    # بررسی وجود کاربر در پایگاه داده
    u = session.query(User).filter_by(user_id=user_id).first()
    if not u:
        if parent_id:
            # اضافه کردن کاربر جدید به پایگاه داده
            row = User(first_name=first_name, user_id=user_id, balance=10, parent_id=parent_id, phone_number="", isAdmin=False)
            session.add(row)
            session.commit()
            
            # اضافه کردن امتیاز به والد
            parent = session.query(User).filter_by(user_id=parent_id).first()
            if parent:
                parent.balance += 10
                session.commit()
                bot.send_message(parent_id, f"کاربر با ایدی عددی {user_id} با لینک شما به ربات اضافه شد و 10 امتیاز به شما اضافه شد")
        
        bot.send_message(message.chat.id, "سلام به ربات ما خوش آمدید!", reply_markup=main_menu())
    else:
        bot.send_message(message.chat.id, "سلام چه کاری میتونم براتون انجام بدم!", reply_markup=main_menu())

def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2)
    markup.add(types.KeyboardButton("آموزش"), types.KeyboardButton("مشاهده ی امتیاز"))
    return markup

@bot.message_handler(func=lambda message: message.text == "آموزش")
def show_videos(message):
    user_id = message.from_user.id
    u = session.query(User).filter_by(user_id=user_id).first()
    
    if u:
        user_points = u.balance
        videos = session.query(Video).filter_by(isActive=True).all()
        if videos:
            # ایجاد دکمه‌های شیشه‌ای برای هر ویدیو
            markup = types.InlineKeyboardMarkup()
            for video in videos:
                title = video.title
                video_id = video.id
                button = types.InlineKeyboardButton(text=title, callback_data=f'video_{video_id}')
                markup.add(button)
            
            bot.send_message(message.chat.id, "لطفاً ویدیو مورد نظر را انتخاب کنید:", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "هیچ ویدیویی در دسترس نیست.")
    else:
        bot.send_message(message.chat.id, "کاربر یافت نشد.")

@bot.message_handler(func=lambda message: message.text == "مشاهده ی امتیاز")
def view_points(message):
    user_id = message.from_user.id
    u = session.query(User).filter_by(user_id=user_id).first()
    
    if u:
        points = u.balance
        referral_link = f"https://t.me/{bot.get_me().username}?start={user_id}"
        bot.send_message(message.chat.id, f"امتیاز فعلی شما: {points}\nبرای دریافت امتیاز بیشتر باید دوستان خود را دعوت کنید: {referral_link}")
    else:
        bot.send_message(message.chat.id, "کاربر یافت نشد.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('video_'))
def handle_video_selection(call):
    video_id = call.data.split('_')[1]
    video = session.query(Video).filter_by(id=int(video_id)).first()
    
    user_id = call.from_user.id
    user = session.query(User).filter_by(user_id=user_id).first()
    
    if video and user:
        file_path = os.path.join(UPLOAD_FOLDER, video.Video)
        
        if os.path.exists(file_path):
            if user.balance >= video.cost:
                # ارسال ویدیو به کاربر
                bot.send_video(call.message.chat.id, video=open(file_path, 'rb'), caption=f"عنوان: {video.title}")
                
                # کاهش امتیاز کاربر
                user.balance -= video.cost
                session.commit()
                
                bot.send_message(call.message.chat.id, f"ویدیو '{video.title}' به شما ارسال شد. امتیاز شما کاهش یافت.")
            else:
                bot.send_message(call.message.chat.id, f"برای مشاهده ویدیو '{video.title}' نیاز به {video.cost} امتیاز دارید.")
        else:
            bot.send_message(call.message.chat.id, f"فایل ویدئویی '{video.title}' پیدا نشد.")
    else:
        bot.send_message(call.message.chat.id, "ویدیو یا کاربر یافت نشد.")

if __name__ == "__main__":
    bot.polling()

