from django.contrib.auth import get_user_model

def user_info(request):
    """
    A context processor that provides safe access to user information.
    """
    context = {}
    if hasattr(request, 'user') and request.user.is_authenticated:
        User = get_user_model()
        try:
            # This will raise User.DoesNotExist if user doesn't exist
            user = User.objects.get(pk=request.user.pk)
            context['user_display'] = user.get_username()
            if hasattr(user, 'get_full_name') and user.get_full_name():
                context['user_display'] = user.get_full_name()
            elif hasattr(user, 'email'):
                context['user_display'] = user.email
        except User.DoesNotExist:
            context['user_display'] = 'Usuario'
    return context
