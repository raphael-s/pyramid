from pyramid.view import view_config
from resources import ImageItem, UserItem
from security import b64
from firstpyramid.views.images import votes_presage, get_css_classes


@view_config(route_name='index', renderer='../templates/index.pt')
def home_view(request):
    items = ImageItem().get_items(request)
    ret_items = []
    for id_, item in items.items():
        user = request.authenticated_userid

        if user in item['voters']:
            css_classes = get_css_classes(user, item['voters'][user])
        else:
            css_classes = get_css_classes(user)

        ret_items.append(
            {'title': item['title'],
             'image': b64(item['image']),
             'id': id_,
             'desc': item['description'],
             'votes': votes_presage(item['votes']),
             'css_classes': css_classes,
             'uploader_name': UserItem().get_user(item['uploader'],
                                                  request)['name'],
             'uploader_id': item['uploader'],
             })

    return {'items': chunker(ret_items, 4)}


def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))
