from django.shortcuts import redirect

def auth_allowed(backend, details, response, *args, **kwargs):
    if not backend.auth_allowed(response, details):
        return redirect('/login_error')#<-here goes your url as defined on your urls.py