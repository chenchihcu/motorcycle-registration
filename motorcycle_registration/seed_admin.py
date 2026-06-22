\"\"\"建立初始管理員帳號\"\"\"
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from models import db, User
from werkzeug.security import generate_password_hash


def seed_admin():
    app = create_app()
    with app.app_context():
        admin = User.query.filter_by(role='admin').first()
        if admin:
            print(f'管理員帳號已存在：{admin.username}')
            return
        
        username = input('請輸入管理員帳號（預設 admin）：').strip() or 'admin'
        password = input('請輸入管理員密碼（預設 admin123）：').strip() or 'admin123'
        name = input('請輸入管理員姓名（預設 管理員）：').strip() or '管理員'
        plate = input('請輸入車牌號碼（預設 ADMIN-001）：').strip() or 'ADMIN-001'
        
        admin = User(
            username=username,
            password_hash=generate_password_hash(password),
            name=name,
            license_plate=plate,
            role='admin',
        )
        db.session.add(admin)
        db.session.commit()
        print(f'✅ 管理員帳號建立成功！')
        print(f'   帳號：{username}')
        print(f'   密碼：{password}')
        print(f'   姓名：{name}')


if __name__ == '__main__':
    seed_admin()
