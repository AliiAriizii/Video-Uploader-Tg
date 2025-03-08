from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime

# تعریف پایه برای کلاس‌های دکوراتور
Base = declarative_base()

# تعریف مدل کاربر
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String)
    user_id = Column(Integer, unique=True, nullable=False)
    balance = Column(Integer)
    parent_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # تغییر به nullable=True
    phone_number = Column(String, nullable=False)
    isAdmin = Column(Boolean)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)

# تعریف مدل دسته‌بندی
class Catgory(Base):
    __tablename__ = 'Catgories'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    slug = Column(String, nullable=False)
    isActive = Column(Boolean)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)

# تعریف مدل ویدیو
class Video(Base):
    __tablename__ = 'videos'
    id = Column(Integer, primary_key=True, autoincrement=True)
    Video = Column(String, unique=True, nullable=False)
    Catgory_id = Column(Integer, ForeignKey("Catgories.id"))
    title = Column(String)
    cost = Column(Integer)
    isActive = Column(Boolean)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)

# ایجاد موتور و نشست پایگاه داده
engine = create_engine('sqlite:///telgrambot.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
