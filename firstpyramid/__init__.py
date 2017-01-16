from pyramid.config import Configurator
from pyramid_zodbconn import get_connection

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from resources import bootstrap


def root_factory(request):
    conn = get_connection(request)
    return bootstrap(conn.root())


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings,
                          root_factory=root_factory)
    config.include('pyramid_chameleon')
    config.include('pyramid_layout')

    # Security policies
    authn_policy = AuthTktAuthenticationPolicy(
        settings['login.secret'], hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('index', '/')
    config.add_static_view('deform_static', 'deform:static/')

    # Image routes
    config.add_route('upload', '/upload')
    config.add_route('images', '/images/{id}')

    # User routes
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('register', '/register')
    config.add_route('user', '/user/{userid}')

    # Data routes
    config.add_route('upvote', '/upvote/{image_id}')
    config.add_route('downvote', '/downvote/{image_id}')

    config.add_panel('firstpyramid.layout.nav_panel', 'navigation',
                     renderer='firstpyramid.layout:templates/panels/navigation.pt')
    config.add_panel('firstpyramid.layout.header_panel', 'header',
                     renderer='firstpyramid.layout:templates/panels/header.pt')
    config.add_panel('firstpyramid.layout.deform_panel', 'deform',
                     renderer='firstpyramid.layout:templates/panels/deform.pt')
    config.scan()
    return config.make_wsgi_app()
