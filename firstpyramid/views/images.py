from deform.schema import FileData
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from resources import ImageItem
from security import b64
import colander
import deform
import deform.widget as w
import firstpyramid


class Storage(dict):

    def preview_url(self, name):
        return ""


class Tags(colander.SequenceSchema):
    tag = colander.SchemaNode(colander.String())


class UploadSchema(colander.MappingSchema):
    title = colander.SchemaNode(colander.String())
    description = colander.SchemaNode(colander.String())
    file = colander.SchemaNode(FileData(),
                               widget=w.FileUploadWidget(Storage()))
    tags = Tags()


def upload_form():
    schema = UploadSchema()
    form = deform.Form(schema, buttons=('submit', 'cancel'))
    form['tags'].widget = w.SequenceWidget(min_len=1)
    return form


@view_config(route_name='upload', renderer='../templates/upload.pt')
def upload_view(request):
    form = upload_form().render()

    if not request.authenticated_userid:
        return {'form': False}

    if 'upload' in request.params:
        controls = request.POST.items()
        try:
            upload_form().validate(controls)
        except deform.ValidationFailure as e:
            # Form is NOT valid
            return {'form': e.render()}

        img = request.params['upload']

        if 'image' not in img.type:
            raise deform.ValidationFailure('File is not of type image')

        new_item = {
            'title': request.params.get('title'),
            'image': request.params.get('upload'),
            'uploader': request.authenticated_userid,
            'description': request.params.get('description'),
            'tags': request.params.getall('tag'),
            'votes': 1,
            'voters': {request.authenticated_userid: 'up'}
        }

        new_key = ImageItem().add_item(new_item, request)
        url = request.route_url('images', id=new_key)

        return HTTPFound(url)

    return {'form': form}


@view_config(route_name='images', renderer='../templates/detail.pt')
def detail_view(request):
    item_id = request.url.split('/')[-1]
    user = request.authenticated_userid

    root = firstpyramid.root_factory(request)

    item = root['images'].get(int(item_id))

    if user in item['voters']:
        css_classes = get_css_classes(user, item['voters'][user])
    else:
        css_classes = get_css_classes(user)

    return {'item': {'title': item['title'],
                     'image': b64(item['image']),
                     'id': item_id,
                     'uploader_name': root['users'][item['uploader']]['name'],
                     'uploader_id': item['uploader'],
                     'votes': votes_presage(item['votes']),
                     'desc': item['description'],
                     'tags': item['tags'],
                     'css_classes': css_classes}}


@view_config(route_name='full_image', renderer='../templates/full_image.pt')
def full_image_view(request):
    root = firstpyramid.root_factory(request)
    item_id = request.url.split('/')[-1]
    item = root['images'].get(int(item_id))
    return{'image': b64(item['image'])}


@view_config(route_name='upvote', renderer='json')
def upvote_data(request):
    image_id = int(request.path.split('/')[-1])
    if ImageItem().exists(request, image_id):
        votes = ImageItem().update_votes(image_id, 1, request)
        return{'votes': votes_presage(votes)}
    else:
        return 'The requested image does not exist'


@view_config(route_name='downvote', renderer='json')
def downvote_data(request):
    image_id = int(request.path.split('/')[-1])
    if ImageItem().exists(request, image_id):
        votes = ImageItem().update_votes(image_id, -1, request)
        return{'votes': votes_presage(votes)}
    else:
        return 'The requested image does not exist'


def votes_presage(votes):
    pre = '+/- '
    if votes > 0:
        pre = '+ '
    elif votes < 0:
        pre = '- '
        # Remove "-" from number
        votes = -votes
    return pre + str(votes)


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
