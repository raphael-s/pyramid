from pyramid.view import view_config
from resources import ImageItem
from security import b64
from firstpyramid.views.images import votes_presage


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
             'uploader': item['uploader'],
             'css_classes': css_classes
             })
    return {'items': ret_items}


def get_css_classes(userid, vote=''):
    base_classes = ['btn', 'btn-lg', 'btn-default', 'vote-button']

    if vote or not userid:
        base_classes.append('disabled')

    up_classes = base_classes + ['btn-success']
    down_classes = base_classes + ['btn-warning']

    if vote == 'up':
        up_classes.append('voted')
    elif vote == 'down':
        down_classes.append('voted')

    return {'up_classes': ' '.join(up_classes),
            'down_classes': ' '.join(down_classes)}
