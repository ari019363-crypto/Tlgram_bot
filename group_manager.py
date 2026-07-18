from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Group(Base):
    __tablename__ = 'groups'
    
    id = Column(Integer, primary_key=True)
    group_id = Column(BigInteger, unique=True)  # آیدی عددی گروه
    group_name = Column(String(200))
    join_date = Column(DateTime, default=datetime.now)
    is_active = Column(Boolean, default=True)
    welcome_enabled = Column(Boolean, default=True)
    roast_enabled = Column(Boolean, default=True)
    auto_mood_change = Column(Boolean, default=True)
    
class GroupManager:
    def __init__(self, db_session):
        self.session = db_session
    
    def add_group(self, group_id, group_name):
        """اضافه کردن گروه جدید به دیتابیس"""
        group = self.session.query(Group).filter_by(group_id=group_id).first()
        if not group:
            group = Group(group_id=group_id, group_name=group_name)
            self.session.add(group)
            self.session.commit()
            return group
        return group
    
    def get_group(self, group_id):
        """گرفتن اطلاعات گروه"""
        return self.session.query(Group).filter_by(group_id=group_id).first()
    
    def get_all_groups(self):
        """گرفتن همه گروه‌های فعال"""
        return self.session.query(Group).filter_by(is_active=True).all()
