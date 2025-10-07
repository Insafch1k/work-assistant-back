class User:
    def __init__(self, user_data):
        self.user_id = user_data['user_id']
        self.user_role = user_data['user_role']
        self.tg_username = user_data['tg_username']
        self.phone = user_data['phone']
        self.tg = user_data['tg']
        self.rating = user_data['rating']
        self.user_name = user_data['user_name']
        self.photo = user_data['photo']
        self.created_at = user_data['created_at']
        self.last_login_at = user_data['last_login_at']
        self.banned = user_data['banned']
        self.is_admin = user_data['is_admin']
        self.paltform = user_data['paltform']  # Опечатка в названии столбца в БД