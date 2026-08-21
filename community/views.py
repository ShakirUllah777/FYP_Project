from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .models import Community, CommunityMembership, CommunityPost, CommunityPostLike
from .forms import CommunityForm, CommunityPostForm


def community_list(request):
    """Main Communities page displaying My Communities, Explore Communities, and Create Community modal."""
    user = request.user
    my_communities = []
    explore_communities = []

    if user.is_authenticated:
        joined_ids = CommunityMembership.objects.filter(user=user).values_list('community_id', flat=True)
        my_communities_qs = Community.objects.filter(id__in=joined_ids).annotate(
            member_count_num=Count('memberships', distinct=True),
            post_count_num=Count('posts', distinct=True)
        )
        explore_communities_qs = Community.objects.exclude(id__in=joined_ids).annotate(
            member_count_num=Count('memberships', distinct=True),
            post_count_num=Count('posts', distinct=True)
        )
    else:
        my_communities_qs = Community.objects.none()
        explore_communities_qs = Community.objects.annotate(
            member_count_num=Count('memberships', distinct=True),
            post_count_num=Count('posts', distinct=True)
        )

    # Active tab logic
    active_tab = request.GET.get('tab', '')
    if not active_tab:
        if user.is_authenticated and my_communities_qs.exists():
            active_tab = 'my'
        else:
            active_tab = 'explore'

    form = CommunityForm()

    return render(request, 'community/community_list.html', {
        'my_communities': my_communities_qs,
        'explore_communities': explore_communities_qs,
        'active_tab': active_tab,
        'form': form,
    })


@login_required
@require_POST
def create_community(request):
    """Allows a logged-in user to create a new community."""
    form = CommunityForm(request.POST, request.FILES)
    if form.is_valid():
        community = form.save(commit=False)
        community.creator = request.user
        community.save()
        
        # Creator automatically becomes a member of the community
        CommunityMembership.objects.get_or_create(community=community, user=request.user)
        
        messages.success(request, f'Community "{community.name}" created successfully!')
        return redirect('community_detail', slug=community.slug)
    else:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{field.title()}: {error}")
        return redirect('community_list')


def community_detail(request, slug):
    """Detailed page for a specific community showing logo, details, creator, members, and post feed."""
    community = get_object_or_404(Community, slug=slug)
    
    # Check if logged in user is joined
    is_joined = False
    if request.user.is_authenticated:
        is_joined = CommunityMembership.objects.filter(community=community, user=request.user).exists()

    # Members list
    memberships = CommunityMembership.objects.filter(community=community).select_related('user__profile')
    member_count = memberships.count()

    # Community posts feed
    posts_qs = CommunityPost.objects.filter(community=community).select_related('author__profile').prefetch_related('likes')
    
    posts = []
    for p in posts_qs:
        posts.append({
            'post': p,
            'likes_count': p.likes.count(),
            'is_liked': p.is_liked_by(request.user) if request.user.is_authenticated else False,
        })

    post_form = CommunityPostForm()

    return render(request, 'community/community_detail.html', {
        'community': community,
        'is_joined': is_joined,
        'memberships': memberships,
        'member_count': member_count,
        'posts': posts,
        'post_form': post_form,
    })


@login_required
def toggle_join(request, slug):
    """Join or leave a community."""
    community = get_object_or_404(Community, slug=slug)
    membership, created = CommunityMembership.objects.get_or_create(community=community, user=request.user)
    
    if not created:
        membership.delete()
        messages.info(request, f'You left the {community.name} community.')
    else:
        messages.success(request, f'Welcome to the {community.name} community!')

    next_url = request.META.get('HTTP_REFERER')
    if next_url and 'community' in next_url:
        return redirect(next_url)
    return redirect('community_detail', slug=slug)


@login_required
@require_POST
def create_community_post(request, slug):
    """Create a post inside a community (only allowed for joined members)."""
    community = get_object_or_404(Community, slug=slug)
    
    is_joined = CommunityMembership.objects.filter(community=community, user=request.user).exists()
    if not is_joined:
        messages.error(request, 'You must join this community before you can post.')
        return redirect('community_detail', slug=slug)

    form = CommunityPostForm(request.POST, request.FILES)
    if form.is_valid():
        post = form.save(commit=False)
        post.community = community
        post.author = request.user
        post.save()
        messages.success(request, 'Your post has been published to the community feed!')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{field.title()}: {error}")

    return redirect('community_detail', slug=slug)


@login_required
def toggle_post_like(request, post_id):
    """Toggle like on a community post."""
    post = get_object_or_404(CommunityPost, id=post_id)
    like_obj, created = CommunityPostLike.objects.get_or_create(post=post, user=request.user)
    
    if not created:
        like_obj.delete()

    next_url = request.META.get('HTTP_REFERER')
    if next_url:
        return redirect(next_url)
    return redirect('community_detail', slug=post.community.slug)

