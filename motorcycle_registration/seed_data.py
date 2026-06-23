"""
大量資料建立腳本 — 20 個活動 + 測試使用者 + 報名資料
用法: python seed_data.py
"""
import sys
import os
import random
sys.path.insert(0, os.path.dirname(__file__))

from datetime import date, timedelta
from werkzeug.security import generate_password_hash
from app import create_app
from models import db, User, Event, Registration, BulletinPost


EVENT_TEMPLATES = [
    {"title": "北宜公路晨跑團", "desc": "經典北宜公路跑山行程，坪林休息站集合"},
    {"title": "台三線重機大會師", "desc": "台三線重機聚會，歡迎各車隊參加"},
    {"title": "西濱快速道路逍遙遊", "desc": "西濱快速道路南下，沿途欣賞海岸風光"},
    {"title": "武嶺追焦攝影團", "desc": "合歡山武嶺拍攝追焦照，專業攝影師隨行"},
    {"title": "南投日月潭環湖", "desc": "日月潭環湖公路，風景優美適合拍照"},
    {"title": "花蓮太魯閣峽谷行", "desc": "太魯閣國家公園峽谷騎行，壯麗景色"},
    {"title": "台東海岸線縱走", "desc": "台東海岸線南北縱走，享受太平洋風光"},
    {"title": "阿里山公路登頂", "desc": "阿里山公路爬坡挑戰，雲海美景"},
    {"title": "桃園復興鄉賞櫻", "desc": "復興鄉櫻花季騎行，賞花兼跑山"},
    {"title": "新竹尖石鄉溫泉行", "desc": "尖石鄉泡湯之旅，山路與溫泉的完美組合"},
    {"title": "苗栗大湖草莓季", "desc": "大湖草莓季騎行，採草莓體驗"},
    {"title": "彰化139縣道晨跑", "desc": "139縣道經典晨跑路線，微熱山丘集合"},
    {"title": "雲林古坑咖啡之旅", "desc": "古坑咖啡產地騎行，品嚐台灣咖啡"},
    {"title": "台南174縣道縱走", "desc": "174縣道蜿蜒山路，適合技術練習"},
    {"title": "高雄壽山觀景台", "desc": "壽山觀景台夜騎，俯瞰高雄夜景"},
    {"title": "屏東墾丁春遊", "desc": "墾丁半島騎行，享受南國陽光"},
    {"title": "宜蘭太平山避暑", "desc": "太平山森林遊樂區避暑騎行"},
    {"title": "基隆北海岸一日遊", "desc": "北海岸濱海公路，野柳、金山、石門"},
    {"title": "台北陽明山花季", "desc": "陽明山花季騎行，竹子湖海芋"},
    {"title": "環島暖身團", "desc": "一週環島暖身行程，四極點挑戰"},
]

TEST_USERS = [
    {"name": "測試車手小明", "plate": "ABC-1234"},
    {"name": "測試車手小華", "plate": "DEF-5678"},
    {"name": "測試車手小美", "plate": "GHI-9012"},
    {"name": "測試車手大偉", "plate": "JKL-3456"},
    {"name": "測試車手小莉", "plate": "MNO-7890"},
]


def seed(app=None):
    """建立測試資料。可傳入已初始化 Flask app，否則自動建立。"""
    if app is None:
        app = create_app()
    with app.app_context():
        # 清理舊資料
        Registration.query.delete()
        Event.query.delete()
        User.query.filter(User.role != "admin").delete()
        db.session.commit()
        print("[OK] 已清除舊資料")

        # 建立測試使用者
        users = []
        for i, t in enumerate(TEST_USERS, 1):
            u = User(
                username=f"test{i:02d}",
                password_hash=generate_password_hash("test1234"),
                name=t["name"],
                license_plate=t["plate"],
                role="user",
            )
            db.session.add(u)
            users.append(u)
        db.session.commit()
        print(f"[OK] 建立 {len(users)} 位測試使用者 (密碼: test1234)")

        admin = User.query.filter_by(username="admin").first()

        # 建立 20 個活動（10 過去 + 10 未來）
        today = date.today()
        events = []
        for i, tmpl in enumerate(EVENT_TEMPLATES):
            if i < 10:
                # 過去活動（隨機 5-90 天前）
                d = today - timedelta(days=random.randint(5, 90))
            else:
                # 未來活動（隨機 7-120 天後）
                d = today + timedelta(days=random.randint(7, 120))

            ev = Event(
                title=tmpl["title"],
                description=tmpl["desc"],
                event_date=d,
                event_date_start=d,
                event_date_end=d + timedelta(days=random.randint(0, 2)),
                max_attendees=60,
                max_vehicles=40,
                created_by=admin.id,
            )
            db.session.add(ev)
            events.append(ev)
        db.session.commit()
        print(f"[OK] 建立 {len(events)} 個活動 (10 過去, 10 未來)")

        # 建立報名資料
        reg_count = 0
        for ev in events:
            # 隨機 10-40 輛車報名
            num_vehicles = random.randint(10, 40)
            selected_users = random.sample(users, min(num_vehicles, len(users)))

            used_ips = set()
            for u in selected_users:
                # 每人 1-3 位出席
                attendees = random.choices([1, 1, 1, 1, 1, 2, 2, 3], k=1)[0]
                # 隨機 IP 避免 uq_event_ip 衝突
                ip = f"10.0.0.{random.randint(2, 254)}"
                while ip in used_ips:
                    ip = f"10.0.0.{random.randint(2, 254)}"
                used_ips.add(ip)
                reg = Registration(
                    event_id=ev.id,
                    user_id=u.id,
                    attendees_count=attendees,
                    ip_address=ip,
                )
                db.session.add(reg)
                reg_count += 1
        db.session.commit()
        print(f"[OK] 建立 {reg_count} 筆報名資料")

        # 建立管理員公告 (post_type='manual') + 系統通知 (post_type='system')
        manual_posts = [
            "歡迎新車友加入！每月第一週日定期車聚請踴躍參加",
            "安全宣導：山區騎行請務必配戴完整護具",
            "車隊 Logo 徵稿活動開跑",
        ]
        system_posts = [
            "系統已完成版本更新",
            f"新活動已建立：{events[-1].title}" if events else "新活動已建立",
            "報名系統維護公告",
            "車隊年度統計資料已更新",
        ]
        for content in manual_posts:
            db.session.add(BulletinPost(
                content=content, post_type="manual", created_by=admin.id,
            ))
        for content in system_posts:
            db.session.add(BulletinPost(
                content=content, post_type="system", created_by=admin.id,
            ))
        db.session.commit()
        print(f"[OK] 建立 {len(manual_posts)} 筆管理員公告 + {len(system_posts)} 筆系統通知")

        print("\n=== 資料建立完成！ ===")
        print(f"   測試帳號密碼: test01 ~ test05 / test1234")
        print(f"   管理員: admin / admin123")


def seed_with_current_app():
    """供 create_app() 呼叫版：不使用 app context，直接操作 db.session"""
    # 清理舊資料
    Registration.query.delete()
    Event.query.delete()
    User.query.filter(User.role != "admin").delete()
    db.session.commit()

    # 建立測試使用者
    users = []
    for i, t in enumerate(TEST_USERS, 1):
        u = User(
            username=f"test{i:02d}",
            password_hash=generate_password_hash("test1234"),
            name=t["name"],
            license_plate=t["plate"],
            role="user",
        )
        db.session.add(u)
        users.append(u)
    db.session.commit()

    admin = User.query.filter_by(username="admin").first()
    today = date.today()
    events = []
    for i, tmpl in enumerate(EVENT_TEMPLATES):
        if i < 10:
            d = today - timedelta(days=random.randint(5, 90))
        else:
            d = today + timedelta(days=random.randint(7, 120))
        ev = Event(
            title=tmpl["title"],
            description=tmpl["desc"],
            event_date=d,
            event_date_start=d,
            event_date_end=d + timedelta(days=random.randint(0, 2)),
            max_attendees=60,
            max_vehicles=40,
            created_by=admin.id,
        )
        db.session.add(ev)
        events.append(ev)
    db.session.commit()

    reg_count = 0
    for ev in events:
        num_vehicles = random.randint(10, 40)
        selected_users = random.sample(users, min(num_vehicles, len(users)))
        used_ips = set()
        for u in selected_users:
            attendees = random.choices([1, 1, 1, 1, 1, 2, 2, 3], k=1)[0]
            ip = f"10.0.0.{random.randint(2, 254)}"
            while ip in used_ips:
                ip = f"10.0.0.{random.randint(2, 254)}"
            used_ips.add(ip)
            reg = Registration(
                event_id=ev.id,
                user_id=u.id,
                attendees_count=attendees,
                ip_address=ip,
            )
            db.session.add(reg)
            reg_count += 1
    db.session.commit()

    # 建立管理員公告 + 系統通知
    manual_posts = [
        "歡迎新車友加入！每月第一週日定期車聚請踴躍參加",
        "安全宣導：山區騎行請務必配戴完整護具",
        "車隊 Logo 徵稿活動開跑",
    ]
    system_posts = [
        "系統已完成版本更新",
        f"新活動已建立：{events[-1].title}" if events else "新活動已建立",
        "報名系統維護公告",
        "車隊年度統計資料已更新",
    ]
    for content in manual_posts:
        db.session.add(BulletinPost(
            content=content, post_type="manual", created_by=admin.id,
        ))
    for content in system_posts:
        db.session.add(BulletinPost(
            content=content, post_type="system", created_by=admin.id,
        ))
    db.session.commit()


if __name__ == "__main__":
    seed()
