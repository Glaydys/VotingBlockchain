class User:
    def __init__(self, fullname, date_of_birth, hometown, phone, password, id_document_path, blockchain_hash):
        self.fullname = fullname
        self.date_of_birth = date_of_birth
        self.hometown = hometown
        self.phone  = phone
        self.password = password
        self.id_document_path = id_document_path
        self.blockchain_hash = blockchain_hash

    def to_dict(self):
        return self.__dict__