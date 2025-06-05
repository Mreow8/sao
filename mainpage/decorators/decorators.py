from django.http import HttpResponse
from django.core.exceptions import PermissionDenied

def sao_admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.user_type == 'sao admin':
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponse('Permission denied: SAO admin access required.', status=403)
    return _wrapped_view

def medical_admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.user_type == 'medical admin':
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponse('Permission denied: Medical admin access required.', status=403)
    return _wrapped_view
