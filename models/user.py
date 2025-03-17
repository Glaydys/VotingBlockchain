from datetime import datetime
class User:
    def __init__(self, fullname, date_of_birth, hometown, phone, password, id_document_path, personal_id, blockchain_hash,is_approved=False,is_admin =False):
        self.fullname = fullname
        self.date_of_birth = date_of_birth
        self.hometown = hometown
        self.phone  = phone
        self.password = password
        self.id_document_path = id_document_path
        self.blockchain_hash = blockchain_hash
        self.is_approved = is_approved 
        self.is_admin = is_admin 
        self.personal_id = personal_id # <-- Thêm thuộc tính cccd
    def to_dict(self):
        return {
            'fullname': self.fullname,
            'date_of_birth': datetime.combine(self.date_of_birth, datetime.min.time()),
            'hometown': self.hometown,
            'phone': self.phone,
            'password': self.password,
            'id_document_path': self.id_document_path,
            'blockchain_hash': self.blockchain_hash,
            'is_approved': self.is_approved,
            'is_admin': self.is_admin,
            'personal_id': self.personal_id
        }