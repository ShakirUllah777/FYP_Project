from posts.forms import PostForm


def global_forms(request):
    if request.user.is_authenticated:
        return {'global_post_form': PostForm()}
    return {}
