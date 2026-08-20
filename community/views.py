from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import render, redirect, get_object_or_404

from accounts.models import UserSkill, Profile
from posts.models import Post
from reviews.models import Review
from .models import Community, CommunityMembership


def community_list(request):
    """Browse all topic communities. Each card shows a live member count
    (explicit joins + anyone whose skills match the community) and a small
    preview of open posts in that space."""
    communities = Community.objects.annotate(joined_count=Count('members', distinct=True))

    my_joined_ids = set()
    my_skill_qualified_ids = set()
    if request.user.is_authenticated:
        my_joined_ids = set(
            CommunityMembership.objects.filter(user=request.user).values_list('community_id', flat=True)
        )
        my_skill_ids = set(UserSkill.objects.filter(user=request.user).values_list('skill_id', flat=True))
        if my_skill_ids:
            my_skill_qualified_ids = set(
                Community.objects.filter(related_skills__id__in=my_skill_ids)
                .values_list('id', flat=True)
            )

    cards = []
    for c in communities:
        qualifying_users = set(
            Profile.objects.filter(user__user_skills__skill__in=c.related_skills.all())
            .values_list('user_id', flat=True)
        )
        total_members = len(qualifying_users | set(
            CommunityMembership.objects.filter(community=c).values_list('user_id', flat=True)
        ))
        cards.append({
            'community': c,
            'member_count': total_members,
            'open_posts': Post.objects.filter(skills_required__in=c.related_skills.all(), is_completed=False).distinct().count(),
            'is_joined': c.id in my_joined_ids,
            'is_skill_matched': c.id in my_skill_qualified_ids,
        })

    return render(request, 'community/community_list.html', {'cards': cards})


def community_detail(request, slug):
    community = get_object_or_404(Community, slug=slug)
    related_skill_ids = list(community.related_skills.values_list('id', flat=True))

    member_user_ids = set(
        UserSkill.objects.filter(skill_id__in=related_skill_ids).values_list('user_id', flat=True)
    ) | set(
        CommunityMembership.objects.filter(community=community).values_list('user_id', flat=True)
    )

    member_profiles = (
        Profile.objects.filter(user_id__in=member_user_ids)
        .select_related('user')
        .distinct()
    )

    members = []
    for profile in member_profiles:
        rating = Review.average_for(profile.user)
        members.append({
            'profile': profile,
            'rating': rating,
            'shared_skills': UserSkill.objects.filter(user=profile.user, skill_id__in=related_skill_ids)
                                               .select_related('skill'),
        })
    members.sort(key=lambda m: (m['rating']['average'] or 0), reverse=True)

    open_posts = (
        Post.objects.filter(skills_required__id__in=related_skill_ids, is_completed=False)
        .exclude(author=request.user if request.user.is_authenticated else None)
        .distinct()
        .order_by('-created_at')[:6]
    )

    is_joined = False
    if request.user.is_authenticated:
        is_joined = CommunityMembership.objects.filter(community=community, user=request.user).exists()

    return render(request, 'community/community_detail.html', {
        'community': community,
        'members': members,
        'member_count': len(members),
        'open_posts': open_posts,
        'is_joined': is_joined,
    })


@login_required
def toggle_join(request, slug):
    community = get_object_or_404(Community, slug=slug)
    membership, created = CommunityMembership.objects.get_or_create(community=community, user=request.user)
    if not created:
        membership.delete()
        messages.info(request, f'You left the {community.name} community.')
    else:
        messages.success(request, f'Welcome to the {community.name} community!')
    return redirect('community_detail', slug=slug)
