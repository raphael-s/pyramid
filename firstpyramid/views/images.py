from deform.schema import FileData
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from resources import UploadItem
import colander
from security import b64
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
            'tags': request.params.getall('tag')
        }

        new_key = UploadItem().add_item(new_item, request)
        url = request.route_url('images', id=new_key)

        return HTTPFound(url)

    return {'form': form}


@view_config(route_name='images', renderer='../templates/detail.pt')
def detail_view(request):
    item_id = request.url.split('/')[-1]

    root = firstpyramid.root_factory(request)

    item = root['images'].get(int(item_id))

    return{'item': {'title': item['title'],
                    'image': b64(item['image']),
                    'id': item_id,
                    'uploader': item['uploader']}}
