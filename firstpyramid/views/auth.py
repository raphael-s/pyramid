from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from resources import UserItem
from pyramid.security import remember, forget
import colander
import deform


class LoginSchema(colander.MappingSchema):
    username = colander.SchemaNode(colander.String())
    password = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.PasswordWidget())


def login_form():
    schema = LoginSchema()
    return deform.Form(schema, buttons=('login',))


class UserNameNode(colander.SchemaNode):
    schema_type = colander.String
    title = 'User Name'

    @colander.deferred
    def validator(self, node):
        request = self.bindings['request']
        if not request:
            raise colander.Invalid(node, 'No request')


class RegisterSchema(colander.MappingSchema):
    username = UserNameNode(
        colander.String()
    ).bind(request='request')
    password = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.PasswordWidget(),
        validator=colander.All(
            colander.Length(min=8),
            colander.Regex('.*\d', msg='Use at least one number'),
            colander.Regex('.*[a-z]', msg='Use at least one lowercase char'),
            colander.Regex('.*[A-Z]', msg='Use at least one uppercase char'),
            colander.Regex('.*[^\s]', msg='Dont use whitespaces'),
        )
    )
    real_name = colander.SchemaNode(colander.String())


def register_form():
    schema = RegisterSchema()
    return deform.Form(schema, buttons=('register',))


@view_config(route_name='login', renderer='../templates/auth/login.pt')
def login_view(request):
    form = login_form().render()

    if 'login' in request.params:
        controls = request.POST.items()
        try:
            login_form().validate(controls)
        except deform.ValidationFailure as e:
            # Form is NOT valid
            return {'form': e.render()}

        params = request.params
        input_user = params.get('username')
        input_pw = params.get('password')

        user = UserItem().get_user(input_user, request)

        if not user or not UserItem().check_pw(input_pw, user['pw']):
            return{'form': form, 'error': 'Wrong login!'}

        headers = remember(request, user.get('userid'))

        url = request.route_url('index')
        return HTTPFound(url, headers=headers)

    return {'form': form}


@view_config(route_name='logout')
def logout_view(request):
    headers = forget(request)
    url = request.route_url('index')
    return HTTPFound(url, headers=headers)


@view_config(route_name='register', renderer='../templates/auth/register.pt')
def register_view(request):
    form = register_form().render()

    if 'register' in request.params:
        controls = request.POST.items()
        try:
            register_form().validate(controls)
        except deform.ValidationFailure as e:
            # Form is NOT valid
            return {'form': e.render()}

        params = request.params
        name = params.get('real_name')
        username = params.get('username')
        pw = params.get('password')

        user = UserItem().get_user(username, request)

        if user:
            return{'form': form, 'error': 'Username already taken'}

        new_user = {'username': username, 'password': pw, 'name': name}

        UserItem().add_user(new_user, request)

        headers = remember(request, username)

        url = request.route_url('index')
        return HTTPFound(url, headers=headers)

    return{'form': form}


@view_config(route_name='user', renderer='../templates/auth/user.pt')
def user_view(request):
    userid = request.url.split('/')[-1]

    user = UserItem().get_user(userid, request)

    return{'user': user}
