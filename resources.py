from persistent import Persistent
from persistent.mapping import PersistentMapping
from ZODB.blob import Blob
import firstpyramid
import transaction

from security import hash_password, check_password


class Folder(PersistentMapping):

    def __init__(self, title):
        PersistentMapping.__init__(self)
        self.title = title


class Root(Folder):
    __name__ = None
    __parent__ = None


class UploadItem(Persistent):

    def add_item(self, new_item, request):
        root = firstpyramid.root_factory(request)

        storage = root['images']
        if storage:
            new_key = sorted(storage.keys())[-1] + 1
        else:
            new_key = 1

        new_item['image'] = Blob(new_item['image'].file.read())

        root['images'].update({new_key: new_item})
        transaction.commit()
        return new_key

    def get_item(self, item_id, request):
        root = firstpyramid.root_factory(request)
        return root['images'][item_id]

    def get_items(self, request):
        root = firstpyramid.root_factory(request)
        return dict(root['images'])


class UserItem(Persistent):

    def get_user(self, userid, request):
        users = self.get_users(request)
        user = users.get(userid, False)

        if not user:
            return {}

        return dict(userid=userid, pw=user['password'], name=user['name'])

    def get_users(self, request):
        root = firstpyramid.root_factory(request)
        return dict(root['users'])

    def add_user(self, new_user, request):
        root = firstpyramid.root_factory(request)

        root['users'].update({new_user['username']: {
            'password': hash_password(new_user['password']),
            'name': new_user['name']
        }
        })

        transaction.commit()

    def check_pw(self, pw, hashed_pw):
        return check_password(pw, hashed_pw)


def bootstrap(zodb_root):
    if 'my_zodb' not in zodb_root:
        root = Root('firstpyramid')
        root['users'] = PersistentMapping()
        root['images'] = PersistentMapping()
        zodb_root['my_zodb'] = root
        transaction.commit()
    return zodb_root['my_zodb']
