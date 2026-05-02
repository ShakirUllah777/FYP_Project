from .models import Message
from .forms import PostForm

def unread_messages(request):
    if request.user.is_authenticated:
        count = Message.objects.filter(
            receiver=request.user, is_read=False
        ).count()
        return {'unread_count': count}
    return {'unread_count': 0}

def global_forms(request):
    if request.user.is_authenticated:
        return {'global_post_form': PostForm()}
    return {}