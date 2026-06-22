from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, TextAreaField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo


class LoginForm(FlaskForm):
    username = StringField("帳號", validators=[DataRequired(message="請輸入帳號")])
    password = PasswordField("密碼", validators=[DataRequired(message="請輸入密碼")])
    submit = SubmitField("登入")


class RegisterForm(FlaskForm):
    username = StringField("帳號", validators=[DataRequired(message="請輸入帳號"), Length(min=3, max=80)])
    password = PasswordField("密碼", validators=[DataRequired(message="請輸入密碼"), Length(min=4, max=100)])
    confirm_password = PasswordField("確認密碼", validators=[DataRequired(), EqualTo("password", message="密碼不一致")])
    name = StringField("姓名", validators=[DataRequired(message="請輸入姓名"), Length(max=100)])
    license_plate = StringField("車牌號碼", validators=[DataRequired(message="請輸入車牌號碼"), Length(max=20)])
    submit = SubmitField("註冊")


class EventForm(FlaskForm):
    title = StringField("活動名稱", validators=[DataRequired(message="請輸入活動名稱")])
    description = TextAreaField("活動內容概述", validators=[DataRequired(message="請輸入活動內容")])
    event_date = DateField("活動日期", validators=[DataRequired(message="請選擇活動日期")])
    max_attendees = IntegerField("人數上限（留空表示無限制）", validators=[])
    google_maps_embed_url = TextAreaField("Google Maps 嵌入網址", validators=[])
    route_waypoints = TextAreaField("路線途經點（每行一個）", validators=[])
    submit = SubmitField("儲存")


class RegistrationForm(FlaskForm):
    attendees_count = IntegerField("出席人數", default=1)
    submit = SubmitField("確認報名")


class BulletinForm(FlaskForm):
    content = TextAreaField("公告內容", validators=[DataRequired(message="請輸入公告內容")])
    submit = SubmitField("發布公告")


class SettingsForm(FlaskForm):
    name = StringField("姓名", validators=[DataRequired(message="請輸入姓名"), Length(max=100)])
    license_plate = StringField("車牌號碼", validators=[DataRequired(message="請輸入車牌號碼"), Length(max=20)])
    submit = SubmitField("儲存設定")


class PasswordForm(FlaskForm):
    old_password = PasswordField("目前密碼", validators=[DataRequired(message="請輸入目前密碼")])
    new_password = PasswordField("新密碼", validators=[DataRequired(message="請輸入新密碼"), Length(min=4, max=100)])
    confirm_password = PasswordField("確認新密碼", validators=[DataRequired(), EqualTo("new_password", message="密碼不一致")])
    submit = SubmitField("更新密碼")


class MessageForm(FlaskForm):
    subject = StringField("主旨", validators=[Length(max=200)])
    content = TextAreaField("訊息內容", validators=[DataRequired(message="請輸入訊息內容")])
    event_id = SelectField("關聯活動（選填）", coerce=int, validators=[])
    submit = SubmitField("送出訊息")
