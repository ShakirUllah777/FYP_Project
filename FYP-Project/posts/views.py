from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import Post, Bookmark
from .forms import PostForm
from accounts.models import Skill, UserSkill
from assistant import services


def _match_score(post, user_skill_ids, user_skill_prof):
    """Weighted skill-match percentage between a post's required skills and
    the logged-in user's own skills (weighted by proficiency level)."""
    required_ids = list(post.skills_required.values_list('id', flat=True))
    if not required_ids:
        return None  # no skills specified on the post -> no meaningful score

    weight = {'beginner': 1, 'intermediate': 2, 'advanced': 3}
    total_possible = len(required_ids) * 3
    earned = 0
    for skill_id in required_ids:
        if skill_id in user_skill_ids:
            earned += weight.get(user_skill_prof.get(skill_id, 'beginner'), 1)

    return round((earned / total_possible) * 100) if total_possible else None


@login_required
def tasks(request):
    posts        = Post.objects.exclude(author=request.user).select_related('author__profile').prefetch_related('skills_required')
    skill_filter = request.GET.get('skill')
    type_filter  = request.GET.get('type')
    sort_by      = request.GET.get('sort', 'recent')

    if skill_filter:
        posts = posts.filter(skills_required__name=skill_filter)
    if type_filter:
        posts = posts.filter(post_type=type_filter)

    skills = Skill.objects.all()

    # --- Weighted skill-match score (feature #6) ---
    my_skills = UserSkill.objects.filter(user=request.user)
    user_skill_ids = set(my_skills.values_list('skill_id', flat=True))
    user_skill_prof = {us.skill_id: us.proficiency for us in my_skills}

    posts = list(posts.distinct())
    for post in posts:
        post.match_score = _match_score(post, user_skill_ids, user_skill_prof)

    if sort_by == 'match':
        posts.sort(key=lambda p: (p.match_score is None, -(p.match_score or 0)))

    # --- Bookmarks (feature: Saved Posts) ---
    bookmarked_ids = set(Bookmark.objects.filter(user=request.user).values_list('post_id', flat=True))
    for post in posts:
        post.is_bookmarked = post.id in bookmarked_ids

    return render(request, 'posts/tasks.html', {
        'posts': posts, 'skills': skills, 'sort_by': sort_by,
    })


@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post.objects.select_related('author__profile').prefetch_related('skills_required'), pk=pk)

    my_skills = UserSkill.objects.filter(user=request.user)
    user_skill_ids = set(my_skills.values_list('skill_id', flat=True))
    user_skill_prof = {us.skill_id: us.proficiency for us in my_skills}
    match_score = _match_score(post, user_skill_ids, user_skill_prof) if post.author_id != request.user.id else None

    # --- Similar projects (feature #9) ---
    similar_posts = Post.objects.filter(
        post_type=post.post_type
    ).exclude(pk=post.pk).filter(
        Q(skills_required__in=post.skills_required.all())
    ).distinct()[:3]

    from reviews.models import Review
    author_rating = Review.average_for(post.author)

    team = getattr(post, 'team', None)
    milestones = post.milestones.all()
    endorsements = post.endorsements.all() if post.post_type == 'fyp' else []

    is_bookmarked = Bookmark.objects.filter(user=request.user, post=post).exists()

    return render(request, 'posts/post_detail.html', {
        'post': post,
        'match_score': match_score,
        'similar_posts': similar_posts,
        'author_rating': author_rating,
        'team': team,
        'milestones': milestones,
        'endorsements': endorsements,
        'is_author': post.author_id == request.user.id,
        'is_bookmarked': is_bookmarked,
    })


def public_post(request, pk):
    """Public, non-authenticated view of an open post with Open Graph meta
    tags so posts can be shared with a rich preview on WhatsApp/LinkedIn
    (feature: SEO-friendly public post pages)."""
    post = get_object_or_404(Post.objects.select_related('author').prefetch_related('skills_required'), pk=pk)
    return render(request, 'posts/public_post.html', {'post': post})


@login_required
def add_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post        = form.save(commit=False)
            post.author = request.user

            # --- AI project-scope estimate (feature #23) ---
            complexity, timeline = services.estimate_complexity(post.description)
            post.estimated_complexity = complexity
            post.estimated_timeline = timeline

            post.save()
            form.save_m2m()

            # --- Duplicate / similar-idea checker (feature #24) ---
            if post.post_type == 'fyp':
                candidates = Post.objects.filter(post_type='fyp').exclude(pk=post.pk)
                similar = services.find_similar_posts(post.title, post.description, candidates)
                if similar:
                    names = ', '.join(f'"{p.title}" ({score}% similar)' for p, score in similar)
                    messages.warning(
                        request,
                        f'Heads up: your post looks similar to existing FYP idea(s): {names}. '
                        f'Consider narrowing your scope so your committee sees it as original.'
                    )

            messages.success(request, 'Post created successfully!')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
        return redirect(request.META.get('HTTP_REFERER', 'tasks'))
    else:
        form = PostForm()
    return render(request, 'posts/add_post.html', {'form': form, 'editing': False})


@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated!')
            return redirect('my_posts')
    else:
        form = PostForm(instance=post)
    return render(request, 'posts/add_post.html', {'form': form, 'editing': True})


@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    post.delete()
    messages.success(request, 'Post deleted successfully.')
    return redirect('my_posts')


@login_required
def toggle_complete(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    post.is_completed = not post.is_completed
    post.save()
    status = 'marked as completed' if post.is_completed else 'reopened'
    messages.success(request, f'Post {status}.')
    return redirect('post_detail', pk=pk)


@login_required
def my_posts(request):
    posts = Post.objects.filter(author=request.user)
    return render(request, 'posts/my_posts.html', {'posts': posts})


@login_required
def toggle_bookmark(request, pk):
    """Save/unsave a post for later (feature: Saved Posts / Bookmarks)."""
    post = get_object_or_404(Post, pk=pk)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, post=post)
    if not created:
        bookmark.delete()
        messages.info(request, 'Removed from your saved posts.')
    else:
        messages.success(request, 'Saved! Find it anytime under More \u2192 Saved Posts.')
    return redirect(request.META.get('HTTP_REFERER', 'tasks'))


@login_required
def my_bookmarks(request):
    bookmarks = Bookmark.objects.filter(user=request.user).select_related(
        'post__author__profile'
    ).prefetch_related('post__skills_required')
    return render(request, 'posts/my_bookmarks.html', {'bookmarks': bookmarks})
