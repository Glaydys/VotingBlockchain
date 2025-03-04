from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
import bcrypt
import os
import hashlib
from werkzeug.utils import secure_filename
from datetime import datetime
from models.user import User

app = Flask(__name__)
app.secret_key = os.urandom(24)

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
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Hàm xử lý đăng ký
def register_user(request):
    fullname = request.form['fullname']
    dob_str = request.form['dob']
    hometown = request.form['hometown']
    phone = request.form['phone']
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    id_document = request.files['id_document']

    print(f"Thông tin form: fullname={fullname}, phone={phone}") # In thông tin

    if password != confirm_password:
        print("Lỗi: Mật khẩu không khớp") 
        return False

    try:
        dob = datetime.strptime(dob_str, '%Y-%m-%d')
        print(f"Ngày sinh: {dob}")
    except ValueError:
        print("Lỗi: Định dạng ngày không hợp lệ")
        return False

    if users_collection.find_one({'phone': phone}):
        print("Lỗi: Số điện thoại đã được đăng ký") 
        return False
    
    if id_document:
        try:
            filename = secure_filename(id_document.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename) #Sửa ở đây
            print(f"Đường dẫn file: {file_path}") 
            
            id_document.save(file_path)  # Lưu file
            id_document_path = file_path.replace("\\", "/")
        except Exception as e:
            print(f"Lỗi lưu file: {e}") 
            return False
    else:
        print("Lỗi: Vui lòng tải lên giấy tờ tùy thân") 
        return False

    data_string = f"{fullname}{dob}{hometown}{phone}{password}{id_document_path}"
    blockchain_hash = hashlib.sha256(data_string.encode('utf-8')).hexdigest()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user = User(fullname, dob, hometown, phone, hashed_password, id_document_path, blockchain_hash)

    try:
        users_collection.insert_one(user.to_dict())
        print("Đăng ký thành công vào MongoDB") # In thông báo
        return user
    except Exception as e:
        print(f"Lỗi lưu vào database: {e}")
        return False

#Hàm xử lý đăng nhập
def login_user(request):
    phone = request.form['phone']
    password = request.form['password']
    print(f"Thông tin đăng nhập: phone={phone}, password={password}")

    user = users_collection.find_one({'phone': phone})
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        print("Đăng nhập thành công")
        return user # Trả về thông tin user
    else:
        print('Không tìm thấy user')
        return None

@app.route("/update_avatar", methods=["POST"])
def update_avatar():
    if "avatar" not in request.files:
        print("Không có tệp nào được chọn!")
        return redirect(url_for("profile"))

    avatar = request.files["avatar"]

    if avatar.filename == "":
        print("Chưa chọn ảnh!")
        return redirect(url_for("profile"))

    if avatar:
        try:
            # Đảm bảo thư mục tồn tại
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)

            # Lưu file với tên an toàn
            filename = secure_filename(avatar.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            avatar.save(file_path)

            # Chuyển đổi đường dẫn thành dạng Flask có thể đọc
            session["filepath"] = file_path.replace("\\", "/")

            print("Cập nhật ảnh đại diện thành công!")
            return redirect(url_for("home"))
        except Exception as e:
            print(f"Lỗi khi cập nhật ảnh: {e}")
            return redirect(url_for("home"))
        
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        action = request.form['action']

        if action == 'register':
            user = register_user(request)
            if user:
                try:
                    users_collection.insert_one(user.to_dict())
                    session['phone'] = user['phone']
                    session['date_of_birth'] = str(user['dob']) 
                    session['hometown'] = user['hometown'] 
                    session['fullname'] = user['fullname'] 
                    session['filepath'] = user['id_document_path'] 
                    print("Đăng ký thành công!")
                    return redirect(url_for('home'))
                except Exception as e:
                    return render_template('index.html')
            else:
                print('user không có gì')
                return render_template('index.html')

        elif action == 'login':
            user = login_user(request)
            if user:
                session['phone'] = user['phone']  
                session['date_of_birth'] = str(user['date_of_birth'])  
                session['hometown'] = user['hometown']  
                session['fullname'] = user['fullname']  
                session['filepath'] = user['id_document_path']  
                print("Đăng nhập thành công!")
                print(session)
                return redirect(url_for('home'))
            else:
                print('login thất bại ở main')
                return render_template('index.html')

    return render_template('index.html')

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
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=False, use_reloader=False)