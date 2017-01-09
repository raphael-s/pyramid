from pyramid.view import view_config
from resources import UploadItem
from security import b64


@view_config(route_name='index', renderer='../templates/index.pt')
def home_view(request):
    items = UploadItem().get_items(request)
    ret_items = []
    for k, v in items.items():
        ret_items.append(
            {'title': v['title'],
             'image': b64(v['image']),
             'id': k,
             'desc': v['description']})
    return {'items': ret_items}
