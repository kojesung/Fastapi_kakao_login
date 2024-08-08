from tinydb import TinyDB, Query

class UserModel:
    def __init__(self, path="db.json"):
        self.db = TinyDB(path)

    def upsert(self, user):
        if not self.db.search(Query().id == user.id):
            self.db.insert(user.serialize())

    def get_user(self, user_id):
        user = self.db.search(Query().id == user_id)
        return UserData.deserialize(user[0])

    def remove_user(self, user_id):
        self.db.remove(Query().id == user_id)


class UserData:
    def __init__(self, user=None):
        if user:
            user_info = user['kakao_account']['profile']
            self.id = user['id']
            self.nickname = user_info['nickname']#kakao_account.profile.nickname에 해당
            self.profile = user_info['profile_image_url']
            self.thumbnail = user_info['thumbnail_image_url']
        else:
            self.id = None
            self.nickname = None
            self.profile = None
            self.thumbnail = None

    def __str__(self):#사용자의 id와 nickname을 문자열로 반환
        return "<UserData>(id:%s, nickname:%s)" % (self.id, self.nickname)

    def serialize(self):#UserData의 데이터를 딕셔너리 형식으로 변환
        return{
            'id': self.id,
            'nickname': self.nickname,
            'profile': self.profile,
            'thumbnail': self.thumbnail
        }

    @staticmethod
    def deserialize(user_data):
        user = UserData()
        user.id = user_data['id']
        user.nickname = user_data['nickname']
        user.profile = user_data['profile']
        user.thumbnail = user_data['thumbnail']
        return user

