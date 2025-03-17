from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory,flash, jsonify ,flash,get_flashed_messages
from pymongo import MongoClient
import bcrypt
import os
import hashlib
from werkzeug.utils import secure_filename
from datetime import datetime,date
from models.user import User
import cloudinary
import cloudinary.uploader


app = Flask(__name__)
app.secret_key = os.urandom(24)

cloudinary.config(
    cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key = os.environ.get("CLOUDINARY_API_KEY"),
    api_secret = os.environ.get("CLOUDINARY_API_SECRET")
)

# Cấu hình MongoDB
app.config['MONGO_URI'] = "mongodb+srv://Nhom07:Nhom07VAA@cluster0.fg6a2.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(app.config['MONGO_URI'])
db = client["Block"]
users_collection = db["users"]

    
# Kiểm tra kết nối MongoDB
try:
    print(f"Database: {db.name}")
    print(f"Collection: {users_collection.name}")
    client.admin.command('ping')
    print("Kết nối thành công đến MongoDB!")
except Exception as e:
    print(f"Không thể kết nối đến MongoDB: {e}")

# Đường dẫn thư mục lưu trữ ảnh

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'} 

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
           
# Hàm xử lý đăng ký
def register_user(request):
    fullname = request.form.get('fullname') 
    personal_id = request.form.get('personal_id')
    dob_str = request.form.get('dob')
    hometown = request.form.get('hometown')
    phone = request.form.get('phone')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    id_document = request.files.get('id_document')

    print(f"Thông tin form: fullname={fullname}, phone={phone}") # In thông tin
    
    if not fullname or not dob_str or not hometown or not phone or not password or not confirm_password or not id_document or not personal_id:
        return {'success': False, 'message': 'Vui lòng điền đầy đủ thông tin'}

    if password != confirm_password:
        return {'success': False, 'message': 'Mật khẩu không khớp'}

    if len(password) < 8:
        return {'success': False, 'message': 'Mật khẩu phải có ít nhất 8 ký tự'}
     # **Kiểm tra định dạng ngày sinh và tuổi**
    try:
        dob = datetime.strptime(dob_str, '%Y-%m-%d').date()  
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))  # Tính tuổi
        if age < 18:
            return {'success': False, 'message': 'Bạn phải trên 18 tuổi để đăng ký'}
        print(f"Ngày sinh: {dob}, Tuổi: {age}")
    except ValueError:
        return {'success': False, 'message': 'Định dạng ngày sinh không hợp lệ (YYYY-MM-DD)'}

    if not phone.isdigit() or len(phone) != 10:
        return {'success': False, 'message': 'Số điện thoại không hợp lệ. Phải là 10 chữ số.'}
    
    if users_collection.find_one({'phone': phone}):
        return {'success': False, 'message': 'Số điện thoại đã được đăng ký'}
    
    if users_collection.find_one({'personal_id': personal_id}):
        return {'success': False, 'message': 'Số Căn cước công dân đã được đăng ký'}
    id_document = request.files.get('id_document')

    if id_document:
        filename = secure_filename(id_document.filename)
        if allowed_file(filename):
            try:
                # **Upload file lên Cloudinary**
                upload_result = cloudinary.uploader.upload(id_document, 
                                                            folder="Blockchain") # Thư mục trên Cloudinary (tùy chọn)
                # **Lấy URL an toàn của ảnh từ Cloudinary response**
                id_document_url = upload_result.get('secure_url')
                print(f"Upload lên Cloudinary thành công. URL: {id_document_url}")
                id_document_path = id_document_url # Lưu Cloudinary URL vào biến id_document_path

            except Exception as e:
                print(f"Lỗi upload lên Cloudinary: {e}")
                return {'success': False, 'message': 'Lỗi khi tải lên giấy tờ tùy thân lên Cloudinary'}

        else:
            return {'success': False, 'message': 'Loại file giấy tờ tùy thân không được phép'}
    else:
        return {'success': False, 'message': 'Vui lòng tải lên giấy tờ tùy thân'}


    data_string = f"{fullname}{dob}{hometown}{phone}{password}{id_document_path}{personal_id}"
    blockchain_hash = hashlib.sha256(data_string.encode('utf-8')).hexdigest()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user = User(fullname, dob, hometown, phone, hashed_password, id_document_path, personal_id, blockchain_hash)

    try:
        users_collection.insert_one(user.to_dict())
        flash("Đăng ký thành công vui lo chờ Admin duyệt ", 'success')
        return {'success': True, 'message': 'Đăng ký thành công! Vui lòng chờ quản trị viên phê duyệt tài khoản.'}  # Trả về dict thành công
    except Exception as e:
        
        print(f"Lỗi lưu vào database: {e}")
        return {'success': False, 'message': 'Lỗi khi lưu thông tin đăng ký vào hệ thống'}  # Trả về dict lỗi
def login_user(request):
    phone = request.form['phone']
    password = request.form['password']
    print(f"Thông tin đăng nhập: phone={phone}, password={password}")
    
    user_data = users_collection.find_one({'phone': phone})
    if user_data:
        if bcrypt.checkpw(password.encode('utf-8'), user_data['password']):
            if user_data.get('is_approved', False):
                print("Đăng nhập thành công")
                return user_data
            else:
                return {'success': False, 'message': 'Tài khoản chưa được quản trị viên xác thực'}
        else:
            print("DEBUG in login_user: Incorrect password detected")
            return {'success': False, 'message': 'Mật khẩu không chính xác'}
    else:
        return {'success': False, 'message': 'Không tìm thấy tài khoản với số điện thoại này'}
    
@app.route('/', methods=['GET', 'POST'])
def index():
    messages = {}
    if request.method == 'POST':
        action = request.form['action']

        if action == 'register':
            register_result = register_user(request)
            if register_result['success']:
                flash(register_result['message'], 'success')
            else:
                flash(register_result['message'], 'error')

        elif action == 'login':
            user = login_user(request)
            if isinstance(user, dict) and 'success' in user:
                flash(user['message'], 'error')
            else:
                session['phone'] = user['phone']
                session['date_of_birth'] = str(user['date_of_birth'])
                session['hometown'] = user['hometown']
                session['fullname'] = user['fullname']
                session['filepath'] = user['id_document_path']
                return redirect(url_for('home')) # No flash here now in / route

    messages_list = get_flashed_messages(with_categories=True)
    messages = {}
    for category, message in messages_list:
        messages[category] = message

    return render_template('index.html', messages=messages)


@app.route('/logout')
def logout():
    session.pop('phone', None)
    return redirect(url_for('index'))

@app.route('/vote')
def vote():
    return render_template('vote.html')

@app.route('/result')
def result():
    return render_template('results.html')

@app.route('/home')
def home():
    print("Entering /home route")  # DEBUG PRINT 1
    flash('Đăng nhập thành công!', 'success')
    print("Flash message 'Đăng nhập thành công!' flashed") # DEBUG PRINT 2
    messages_list = get_flashed_messages(with_categories=True)
    print(f"Flashed messages in /home route: {messages_list}") # DEBUG PRINT 3
    messages = {}
    for category, message in messages_list:
        messages[category] = message

    return render_template('home.html', messages=messages) 

if __name__ == '__main__':
    app.run(debug=True)