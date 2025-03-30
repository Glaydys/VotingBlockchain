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
from bson.objectid import ObjectId
from web3 import Web3
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)

cloudinary.config(
    cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key = os.environ.get("CLOUDINARY_API_KEY"),
    api_secret = os.environ.get("CLOUDINARY_API_SECRET")
)

# Cấu hình MongoDB
app.config['MONGO_URI'] = os.environ.get("MONGO_URI")
client = MongoClient(app.config['MONGO_URI'])
db = client["Block"]
users_collection = db["users"]
elections_collection = db["elections"]  
candidates_collection = db["candidates"]  

    
# Kiểm tra kết nối MongoDB
try:
    print(f"Database: {db.name}")
    print(f"Collection: {users_collection.name}")
    client.admin.command('ping')
    print("Kết nối thành công đến MongoDB!")
except Exception as e:
    print(f"Không thể kết nối đến MongoDB: {e}")
    
# ganache_url = os.environ.get("GANACHE_URL") 
ganache_url = "http://127.0.0.1:7545" # Nếu bạn dùng giá trị cứng

web3 = Web3(Web3.HTTPProvider(ganache_url))

# Kiểm tra kết nối Web3
if web3.is_connected():
    print("Kết nối thành công đến Ganache!")
else:
    print("Không thể kết nối đến Ganache!")

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
    election_id = request.args.get('cuocBauCu')
    user_phone = session.get('phone') # Lấy số điện thoại người dùng từ session (ví dụ)
    user_data = users_collection.find_one({'phone': user_phone})
    user_id = str(user_data['_id']) if user_data else "unknown" 
    
    return render_template('vote.html', user_id=user_id, election_id=election_id)

@app.route('/result')
def result():
    return render_template('results.html')

@app.route('/home')
def home():
    print("Entering /home route")  # DEBUG PRINT 1
    flash('Đăng nhập thành công!', 'success')
    messages_list = get_flashed_messages(with_categories=True)
    messages = {}
    for category, message in messages_list:
        messages[category] = message

    return render_template('home.html', messages=messages) 

@app.route('/get_elections', methods=['GET'])
def get_elections():
    tinh = request.args.get('tinh')  # Giờ tinh, quan, phuong phải là tên (Ví dụ: "Hà Nội")
    quan = request.args.get('quan')  
    phuong = request.args.get('phuong')  

    query = {}
    if tinh:
        query["tinh"] = tinh  # Tìm theo tên thay vì mã
    if quan:
        query["quan"] = quan
    if phuong:
        query["phuong"] = phuong

    elections = list(elections_collection.find(query, {"_id": 1, "tenCuocBauCu": 1}))

    for election in elections:
        election["_id"] = str(election["_id"])

    return jsonify({"status": "success", "elections": elections})


@app.route('/get_candidates', methods=['GET'])
def get_candidates():
    cuoc_bau_cu_id = request.args.get("cuocBauCu")

    if not cuoc_bau_cu_id:
        return jsonify({"status": "error", "message": "Thiếu tham số cuocBauCu"}), 400

    if not ObjectId.is_valid(cuoc_bau_cu_id):
        return jsonify({"status": "error", "message": "ID không hợp lệ"}), 400

    try:
        election = elections_collection.find_one(
            {"_id": ObjectId(cuoc_bau_cu_id)},
            {"_id": 0, "ungCuVien": 1}
        )
        if not election or "ungCuVien" not in election:
            return jsonify({"status": "error", "message": "Không tìm thấy cuộc bầu cử hoặc không có ứng cử viên"}), 404

        candidates_data = []
        for candidate in election["ungCuVien"]:
            candidates_data.append({
                "id": str(candidate.get("_id")),  # **Lấy _id của ứng viên và convert to string**
                "full_name": candidate.get("full_name", "Không rõ")
            })

        return jsonify({"status": "success", "candidates": candidates_data})

    except Exception as e:
        print(f"Lỗi khi lấy danh sách ứng cử viên: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
    
    
    

contract_abi_path = os.path.join(os.path.dirname(__file__), 'build', 'contracts', 'VotingContract.json')
with open(contract_abi_path, 'r', encoding='utf-8') as f:
    contract_abi = json.load(f)['abi']

# **Địa chỉ Contract đã triển khai (CẬP NHẬT ĐỊA CHỈ MỚI)**
contract_address = os.environ.get("CONTRACT_ADDRESS") 
# Tạo đối tượng contract
voting_contract = web3.eth.contract(address=contract_address, abi=contract_abi)


@app.route('/submit_vote', methods=['POST'])
def submit_vote():
    if not session.get('phone'): # Kiểm tra đăng nhập (nếu cần)
        return jsonify({'status': 'error', 'message': 'Bạn cần đăng nhập để bỏ phiếu'}), 401

    try:
        user_id_str = request.form.get('userId') # **Lấy userId từ form dưới dạng chuỗi**
        candidate_id_str = request.form.get('candidateId') # **Lấy candidateId từ form dưới dạng chuỗi**
        election_id_str = request.form.get('electionId') # **Lấy electionId từ form dưới dạng chuỗi**

        print(f"Raw userId (string): {user_id_str}, candidateId (string): {candidate_id_str}, electionId (string): {election_id_str}") # In ra giá trị chuỗi gốc để debug

        # **Chuyển đổi chuỗi hex sang số nguyên (uint256)**
        try:
            user_id = int(user_id_str, 16) if user_id_str else 0 # Chuyển từ chuỗi hex sang số nguyên, nếu chuỗi rỗng thì để là 0
            candidate_id = int(candidate_id_str, 16) if candidate_id_str else 0 # Chuyển từ chuỗi hex sang số nguyên, nếu chuỗi rỗng thì để là 0
            election_id = int(election_id_str, 16) if election_id_str else 0 # Chuyển từ chuỗi hex sang số nguyên, nếu chuỗi rỗng thì để là 0
        except ValueError as e:
            print(f"Error converting IDs to integers: {e}") # In lỗi nếu chuyển đổi không thành công
            return jsonify({'status': 'error', 'message': 'Lỗi chuyển đổi ID sang số nguyên. Vui lòng kiểm tra lại ID.'}), 400 # Trả về lỗi cho frontend

        print(f"userId (int): {user_id}, candidateId (int): {candidate_id}, electionId (int): {election_id}") # In ra giá trị số nguyên sau chuyển đổi để debug

        # Lấy danh sách tài khoản Ganache (CHỈ DÙNG CHO TEST)
        accounts = web3.eth.accounts
        voter_account = accounts[0] # Sử dụng tài khoản đầu tiên làm người bỏ phiếu (cho mục đích test)
        
        print(f"Kiểm tra hasVoted - userId: {user_id}, electionId: {election_id}")
        
         # **Kiểm tra xem người dùng đã bỏ phiếu trong cuộc bầu cử này chưa (gọi hàm checkHasVoted của smart contract)**
        already_voted = voting_contract.functions.checkHasVoted(user_id, election_id).call()
        if already_voted:
            print("DEBUG: Phát hiện đã bỏ phiếu rồi!")
            print(f"Giá trị already_voted: {already_voted}")
            return jsonify({'status': 'error', 'message': 'Bạn đã bỏ phiếu trong cuộc bầu cử này rồi.'}), 400 # Trả về lỗi nếu đã bỏ phiếu
        
        # Gọi hàm castVote trong smart contract, truyền vào các giá trị số nguyên đã chuyển đổi
        tx_hash = voting_contract.functions.castVote(user_id, candidate_id, election_id).transact({'from': voter_account})

        # Chờ transaction được mine
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

        return jsonify({'status': 'success', 'message': 'Bỏ phiếu thành công! '}), 200

    except Exception as e:
        print(f"Lỗi khi bỏ phiếu: {e}")
        return jsonify({'status': 'error', 'message': f'Lỗi khi bỏ phiếu: {str(e)}'}), 500
    
@app.route('/get_vote_count')
def get_vote_count():
    try:
        vote_count = voting_contract.functions.getVoteCount().call()
        return jsonify({'status': 'success', 'vote_count': vote_count}), 200
    except Exception as e:
        print(f"Lỗi khi lấy số lượng phiếu bầu: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)