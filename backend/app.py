from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from flask_mail import Mail, Message
from models import db, User
from config import Config
import random
import string
from datetime import datetime, timedelta
import re
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import base64

app = Flask(__name__)
app.config.from_object(Config)

# 配置CORS，允许前端访问
CORS(app, resources={r"/*": {"origins": "*"}})

# 初始化扩展
db.init_app(app)
mail = Mail(app)

# 存储验证码的简单字典（生产环境应使用Redis等）
verification_codes = {}

def generate_verification_code(length=4):
    """生成指定长度的数字验证码"""
    return ''.join(random.choices(string.digits, k=length))

def generate_captcha_image(code):
    """生成验证码图片"""
    # 创建图像
    width, height = 120, 40
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    
    # 创建绘图对象
    draw = ImageDraw.Draw(image)
    
    # 绘制干扰线
    for _ in range(5):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        draw.line([(x1, y1), (x2, y2)], fill=(random.randint(0, 150), random.randint(0, 150), random.randint(0, 150)), width=1)
    
    # 绘制验证码文字
    try:
        # 尝试使用系统字体
        font = ImageFont.truetype('arial.ttf', 24)
    except IOError:
        # 如果找不到字体，使用默认字体
        font = ImageFont.load_default()
    
    # 计算文字位置，使其居中
    text_width = draw.textlength(code, font=font)
    x = (width - text_width) / 2
    y = (height - 24) / 2
    
    # 绘制文字
    draw.text((x, y), code, fill=(random.randint(0, 100), random.randint(0, 100), random.randint(0, 100)), font=font)
    
    # 添加一些随机点
    for _ in range(50):
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.point((x, y), fill=(random.randint(0, 150), random.randint(0, 150), random.randint(0, 150)))
    
    # 将图像转换为字节流
    img_io = BytesIO()
    image.save(img_io, 'PNG')
    img_io.seek(0)
    
    # 将图片转换为base64编码
    img_base64 = base64.b64encode(img_io.getvalue()).decode('ascii')
    return img_base64

def is_valid_email(email):
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def send_verification_email(email, code):
    """发送验证码邮件"""
    try:
        msg = Message(
            subject='邮箱验证',
            sender=app.config['MAIL_USERNAME'],
            recipients=[email]
        )
        msg.body = f'您的验证码是：{code}，有效期为10分钟。'
        msg.html = f'''
        <h2>邮箱验证</h2>
        <p>您的验证码是：<strong>{code}</strong></p>
        <p>有效期为10分钟，请尽快使用。</p>
        '''
        mail.send(msg)
        return True
    except Exception as e:
        print(f"邮件发送失败: {str(e)}")
        return False

@app.route('/api/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '请求数据不能为空'}), 400
    
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    code = data.get('code', '')
    
    # 验证输入
    if not email or not password or not code:
        return jsonify({'error': '邮箱、密码和验证码不能为空'}), 400
    
    if not is_valid_email(email):
        return jsonify({'error': '邮箱格式不正确'}), 400
    
    if len(password) < 6:
        return jsonify({'error': '密码长度至少6位'}), 400
    
    # 检查邮箱是否已存在
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': '该邮箱已被注册'}), 400
    
    # 验证验证码
    if email not in verification_codes:
        return jsonify({'error': '请先获取验证码'}), 400
    
    stored_code, expiry_time = verification_codes[email]
    if datetime.now(timezone.utc)() > expiry_time:
        if email in verification_codes:
            del verification_codes[email]
        return jsonify({'error': '验证码已过期'}), 400
    
    if stored_code != code:
        return jsonify({'error': '验证码错误'}), 400
    
    # 创建用户
    user = User(email=email)
    user.set_password(password)
    
    try:
        db.session.add(user)
        db.session.commit()
        # 注册成功后删除验证码
        if email in verification_codes:
            del verification_codes[email]
        return jsonify({'message': '注册成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '注册失败，请稍后重试'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '请求数据不能为空'}), 400
    
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    code = data.get('code', '')
    
    # 验证输入
    if not email or not password or not code:
        return jsonify({'error': '邮箱、密码和验证码不能为空'}), 400
    
    if not is_valid_email(email):
        return jsonify({'error': '邮箱格式不正确'}), 400
    
    # 验证图形验证码
    # 从前端获取的应该是验证码键值
    # 这里假设前端发送的是图形验证码的键值
    # 验证码键值应该在登录请求中以 captcha_key 字段传递
    captcha_key = data.get('captcha_key', '')
    
    if not captcha_key:
        return jsonify({'error': '请提供图形验证码键值'}), 400
    
    if captcha_key not in verification_codes:
        return jsonify({'error': '图形验证码无效'}), 400
    
    stored_code, expiry_time = verification_codes[captcha_key]
    if datetime.now(timezone.utc)() > expiry_time:
        if captcha_key in verification_codes:
            del verification_codes[captcha_key]
        return jsonify({'error': '图形验证码已过期'}), 400
    
    if stored_code != code:
        return jsonify({'error': '图形验证码错误'}), 400
    
    # 验证码正确，删除已使用的验证码
    if captcha_key in verification_codes:
        del verification_codes[captcha_key]
    
    # 验证用户凭据
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'error': '邮箱或密码错误'}), 400
    
    return jsonify({'message': '登录成功', 'user': {'email': user.email}}), 200

@app.route('/api/send-verification-code', methods=['POST'])
def send_verification_code():
    """发送验证码"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '请求数据不能为空'}), 400
    
    email = data.get('email', '').strip().lower()
    purpose = data.get('purpose', 'register')  # 'register' 或 'login'
    
    if not email:
        return jsonify({'error': '邮箱不能为空'}), 400
    
    if not is_valid_email(email):
        return jsonify({'error': '邮箱格式不正确'}), 400
    
    # 限制发送频率
    current_time = datetime.now(timezone.utc)()
    last_sent = verification_codes.get(f"last_sent_{email}", None)
    if last_sent and current_time - last_sent < timedelta(minutes=1):
        return jsonify({'error': '验证码发送过于频繁，请稍后再试'}), 429
    
    # 生成验证码
    code = generate_verification_code(4)
    expiry_time = current_time + timedelta(minutes=10)  # 10分钟有效期
    
    # 根据用途存储验证码
    if purpose == 'register':
        verification_codes[email] = (code, expiry_time)
    else:  # login
        verification_codes[f"login_{email}"] = (code, expiry_time)
    
    # 记录发送时间以限制频率
    verification_codes[f"last_sent_{email}"] = current_time
    
    # 发送邮件
    if send_verification_email(email, code):
        return jsonify({'message': '验证码已发送，请查收邮件'}), 200
    else:
        return jsonify({'error': '验证码发送失败，请稍后重试'}), 500

@app.route('/api/generate-captcha', methods=['GET'])
def generate_captcha():
    """生成图形验证码"""
    code = generate_verification_code(4)
    
    # 生成图片验证码
    img_base64 = generate_captcha_image(code)
    
    # 存储验证码到会话或内存中（这里使用简单的内存存储）
    captcha_key = f"captcha_{datetime.now(timezone.utc)().timestamp()}"
    expiry_time = datetime.now(timezone.utc)() + timedelta(minutes=5)  # 5分钟有效期
    verification_codes[captcha_key] = (code, expiry_time)
    
    return jsonify({
        'captcha_key': captcha_key,
        'image': f'data:image/png;base64,{img_base64}',
        'message': '图形验证码生成成功'
    })

@app.route('/api/refresh-captcha', methods=['POST'])
def refresh_captcha():
    """刷新图形验证码"""
    code = generate_verification_code(4)
    
    # 生成图片验证码
    img_base64 = generate_captcha_image(code)
    
    # 存储验证码到会话或内存中
    captcha_key = f"captcha_{datetime.now(timezone.utc)().timestamp()}"
    expiry_time = datetime.now(timezone.utc)() + timedelta(minutes=5)  # 5分钟有效期
    verification_codes[captcha_key] = (code, expiry_time)
    
    return jsonify({
        'captcha_key': captcha_key,
        'image': f'data:image/png;base64,{img_base64}',
        'message': '图形验证码已刷新'
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)