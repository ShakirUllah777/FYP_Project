import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from .models import Profile, Skill, UserSkill, EmailVerification, SavedSearch
from posts.models import Post


def _send_verification_email(user):
    verification, _ = EmailVerification.objects.get_or_create(
        user=user, defaults={'token': EmailVerification.generate_token()}
    )
    if not verification.token:
        verification.token = EmailVerification.generate_token()
        verification.save()
    verify_url = f"/verify-email/{verification.token}/"
    send_mail(
        subject='Verify your CollabSpace account',
        message=(
            f"Hi {user.first_name},\n\n"
            f"Welcome to CollabSpace! Please verify your university email by opening this link:\n"
            f"{verify_url}\n\n"
            f"If you did not create this account, you can ignore this email."
        ),
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@collabspace.local'),
        recipient_list=[user.email],
        fail_silently=True,
    )


def register(request):
    if request.user.is_authenticated:
        return redirect('tasks')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        email      = request.POST.get('email', '').strip()
        password   = request.POST.get('password', '')
        confirm    = request.POST.get('confirm_password', '')

        form_data = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
        }

        if not (first_name and last_name and email and password and confirm):
            messages.error(request, 'All fields are required.')
            return render(request, 'accounts/register.html', {'form_data': form_data})

        if password != confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/register.html', {'form_data': form_data})

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'This email is already registered.')
            return render(request, 'accounts/register.html', {'form_data': form_data})

        missing_requirements = []
        if len(password) < 8:
            missing_requirements.append('at least 8 characters')
        if not re.search(r'[A-Z]', password):
            missing_requirements.append('at least one capital letter (A-Z)')
        if not re.search(r'[a-z]', password):
            missing_requirements.append('at least one lowercase letter (a-z)')
        if not re.search(r'\d', password):
            missing_requirements.append('at least one number (0-9)')
        if not re.search(r'[\W_]', password):
            missing_requirements.append('at least one special symbol (!@#$%^&* etc.)')

        if missing_requirements:
            if len(missing_requirements) == 1:
                msg = f"Password requirements not met: {missing_requirements[0]} is missing."
            else:
                msg = f"Password requirements not met: {', '.join(missing_requirements[:-1])} and {missing_requirements[-1]} are missing."
            messages.error(request, msg)
            return render(request, 'accounts/register.html', {'form_data': form_data})

        base_username = f"{first_name.lower()}_{last_name.lower()}"
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        Profile.objects.get_or_create(user=user)
        _send_verification_email(user)

        messages.success(request, 'Account created successfully! Check your email to verify your account, then login.')
        return redirect('login')

    return render(request, 'accounts/register.html')


def verify_email(request, token):
    verification = EmailVerification.objects.filter(token=token).select_related('user', 'user__profile').first()
    if not verification:
        messages.error(request, 'Invalid or expired verification link.')
        return redirect('login')

    profile, _ = Profile.objects.get_or_create(user=verification.user)
    profile.is_verified = True
    profile.save()
    verification.verified_at = timezone.now()
    verification.save()

    messages.success(request, 'Your email is verified! You can now login.')
    return redirect('login')


@login_required
def resend_verification(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if profile.is_verified:
        messages.info(request, 'Your account is already verified.')
    else:
        _send_verification_email(request.user)
        messages.success(request, 'Verification email re-sent.')
    return redirect('my_profile')


def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('/admin/')
        return redirect('tasks')
    if request.method == 'POST':
        email_or_username = request.POST.get('email', '').strip()
        password          = request.POST.get('password')
        user = None
        try:
            # 1. Try to authenticate directly as username
            user = authenticate(request, username=email_or_username, password=password)

            # 2. If not found, try as email
            if not user:
                users = User.objects.filter(email__iexact=email_or_username)
                for u in users:
                    authenticated_user = authenticate(request, username=u.username, password=password)
                    if authenticated_user:
                        user = authenticated_user
                        break

            if user:
                login(request, user)
                if user.is_superuser:
                    return redirect('/admin/')
                return redirect('tasks')
        except Exception:
            pass
        messages.error(request, 'Invalid email or password.')
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def my_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    user_skills = UserSkill.objects.filter(user=request.user).select_related('skill')
    posts       = Post.objects.filter(author=request.user)
    from reviews.models import Review
    reviews = Review.objects.filter(reviewed_user=request.user).select_related('reviewer')
    rating  = Review.average_for(request.user)
    return render(request, 'accounts/profile.html', {
        'profile':     profile,
        'user_skills': user_skills,
        'posts':       posts,
        'is_own':      True,
        'reviews':     reviews,
        'rating':      rating,
    })


@login_required
def user_profile(request, username):
    viewed_user = get_object_or_404(User, username=username)
    profile, created = Profile.objects.get_or_create(user=viewed_user)
    user_skills = UserSkill.objects.filter(user=viewed_user).select_related('skill')
    posts       = Post.objects.filter(author=viewed_user)
    from reviews.models import Review
    reviews = Review.objects.filter(reviewed_user=viewed_user).select_related('reviewer')
    rating  = Review.average_for(viewed_user)
    return render(request, 'accounts/profile.html', {
        'profile':     profile,
        'user_skills': user_skills,
        'posts':       posts,
        'is_own':      False,
        'viewed_user': viewed_user,
        'reviews':     reviews,
        'rating':      rating,
    })


@login_required
def add_skills(request):
    categories  = Skill.CATEGORY_CHOICES
    all_skills  = Skill.objects.all().order_by('category', 'name')
    user_skills = UserSkill.objects.filter(user=request.user)
    user_skill_ids = list(user_skills.values_list('skill_id', flat=True))
    user_skill_prof = {us.skill_id: us.proficiency for us in user_skills}

    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', request.user.first_name)
        request.user.last_name = request.POST.get('last_name', request.user.last_name)
        request.user.save()

        profile.department = request.POST.get('department')
        profile.program = request.POST.get('program')

        sem = request.POST.get('semester')
        if sem and sem.isdigit():
            profile.semester = int(sem)

        profile.bio = request.POST.get('bio', '')
        profile.github = request.POST.get('github', '')
        profile.linkedin = request.POST.get('linkedin', '')
        profile.looking_for = request.POST.get('looking_for')
        profile.availability = request.POST.get('availability')
        profile.batch = request.POST.get('batch', profile.batch)

        if 'photo' in request.FILES:
            profile.photo = request.FILES['photo']

        if 'id_card' in request.FILES:
            profile.id_card = request.FILES['id_card']
            profile.is_id_verified = False  # re-upload needs re-approval

        profile.save()

        UserSkill.objects.filter(user=request.user).delete()
        skill_ids = request.POST.getlist('skills')
        for sid in skill_ids:
            if sid and sid.isdigit():
                skill = get_object_or_404(Skill, id=int(sid))
                UserSkill.objects.create(
                    user=request.user, skill=skill, proficiency='beginner'
                )

        custom_skill_name = request.POST.get('custom_skill', '').strip()
        if custom_skill_name:
            custom_skill, _ = Skill.objects.get_or_create(
                name=custom_skill_name,
                defaults={'category': 'others'}
            )
            UserSkill.objects.get_or_create(
                user=request.user, skill=custom_skill, defaults={'proficiency': 'beginner'}
            )

        messages.success(request, 'Profile and skills updated!')
        return redirect('my_profile')

    return render(request, 'accounts/add_skills.html', {
        'categories':      categories,
        'all_skills':      all_skills,
        'user_skill_ids':  user_skill_ids,
        'user_skill_prof': user_skill_prof,
        'profile':         profile,
        'departments':     Profile.DEPARTMENT_CHOICES,
        'programs':        Profile.PROGRAM_CHOICES,
        'semesters':       Profile.SEMESTER_CHOICES,
        'looking_fors':    Profile.LOOKING_FOR,
        'availabilities':  Profile.AVAILABILITY,
    })


@login_required
def seniors(request):
    search   = request.GET.get('search', '').strip()
    semester = request.GET.get('semester', '').strip()
    batch    = request.GET.get('batch', '').strip()

    seniors_qs = Profile.objects.filter(
        semester__in=[6, 7, 8]
    ).exclude(
        user=request.user
    ).select_related('user')

    if search:
        seniors_qs = seniors_qs.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(user__username__icontains=search)
        )

    if semester:
        seniors_qs = seniors_qs.filter(semester=semester)

    if batch:
        seniors_qs = seniors_qs.filter(batch__iexact=batch)

    seniors_qs = seniors_qs[:20]

    from reviews.models import Review
    seniors_with_ratings = []
    for profile in seniors_qs:
        rating = Review.average_for(profile.user)
        seniors_with_ratings.append((profile, rating))

    return render(request, 'accounts/seniors.html', {
        'seniors':  seniors_with_ratings,
        'search':   search,
        'semester': semester,
        'batch':    batch,
    })


# ---------------------------------------------------------------------
# Saved searches / job alerts
# ---------------------------------------------------------------------

@login_required
def save_search(request):
    if request.method == 'POST':
        SavedSearch.objects.create(
            user=request.user,
            label=request.POST.get('label', '').strip() or 'Saved search',
            skill=request.POST.get('skill', ''),
            post_type=request.POST.get('post_type', ''),
        )
        messages.success(request, 'Search saved! We will surface matches here.')
    return redirect(request.META.get('HTTP_REFERER', 'tasks'))


@login_required
def my_saved_searches(request):
    searches = SavedSearch.objects.filter(user=request.user)
    results = [(s, s.matching_posts()) for s in searches]
    return render(request, 'accounts/saved_searches.html', {'results': results})


@login_required
def delete_saved_search(request, pk):
    SavedSearch.objects.filter(pk=pk, user=request.user).delete()
    messages.success(request, 'Saved search removed.')
    return redirect('my_saved_searches')


# ---------------------------------------------------------------------
# Recommended teammates (complementary skill matching)
# ---------------------------------------------------------------------

@login_required
def recommended_teammates(request):
    """Suggest students whose skill set complements (not duplicates) the
    logged-in user's own skills - a lightweight recommender using simple
    set overlap, no external ML infrastructure required. Falls back to
    showing top-rated/most-active students when the user has no skills
    yet or no scored matches exist, so the page is never a blank wall."""
    from reviews.models import Review
    from accounts.models import Skill

    my_skill_ids = set(UserSkill.objects.filter(user=request.user).values_list('skill_id', flat=True))

    candidates = Profile.objects.exclude(user=request.user).select_related('user')
    scored = []
    for profile in candidates:
        their_skill_ids = set(UserSkill.objects.filter(user=profile.user).values_list('skill_id', flat=True))
        if not their_skill_ids:
            continue
        complementary = their_skill_ids - my_skill_ids
        overlap = their_skill_ids & my_skill_ids
        # Favor people who bring NEW skills to the table, small bonus for shared ground.
        score = (len(complementary) * 2) + len(overlap)
        if score > 0:
            scored.append((profile, score, complementary, overlap))

    scored.sort(key=lambda t: t[1], reverse=True)
    top = scored[:8]

    fallback_mode = False
    if not top:
        # No skills on file yet (or nobody scored) - surface the platform's
        # most active/highest-rated students instead of an empty page.
        fallback_mode = True
        fallback_profiles = list(candidates)
        fallback_profiles.sort(
            key=lambda p: (
                Review.average_for(p.user)['average'] or 0,
                Post.objects.filter(author=p.user).count(),
            ),
            reverse=True,
        )
        top = [(p, 0, set(), set()) for p in fallback_profiles[:8]]

    recommendations = []
    for profile, score, complementary_ids, overlap_ids in top:
        skills = Skill.objects.filter(id__in=complementary_ids)
        shared = Skill.objects.filter(id__in=overlap_ids)
        rating = Review.average_for(profile.user)

        if fallback_mode:
            reason = 'Active on the platform with strong ratings'
        elif complementary_ids and overlap_ids:
            reason = f'Brings {len(complementary_ids)} new skill(s), shares {len(overlap_ids)} with you'
        elif complementary_ids:
            reason = f'Brings {len(complementary_ids)} skill(s) you don\u2019t have yet'
        else:
            reason = f'Shares {len(overlap_ids)} skill(s) with you'

        recommendations.append({
            'profile': profile,
            'score': score,
            'complementary_skills': skills,
            'shared_skills': shared,
            'rating': rating,
            'reason': reason,
        })

    return render(request, 'accounts/recommended_teammates.html', {
        'recommendations': recommendations,
        'fallback_mode': fallback_mode,
        'has_skills': bool(my_skill_ids),
    })


# ---------------------------------------------------------------------
# Leaderboard
# ---------------------------------------------------------------------

@login_required
def leaderboard(request):
    """Ranks every student by a holistic Activity Score - posts created,
    completed collaborations, team memberships, and review rating/count -
    instead of only listing students who have already made a post. This
    keeps the leaderboard populated and meaningful even early on, rather
    than showing an empty table."""
    from django.db.models import Count
    from reviews.models import Review
    from collaboration.models import TeamMembership

    dept = request.GET.get('department', '')
    profiles = Profile.objects.select_related('user')
    if dept:
        profiles = profiles.filter(department=dept)

    rows = []
    for profile in profiles:
        post_count = Post.objects.filter(author=profile.user).count()
        completed_count = Post.objects.filter(author=profile.user, is_completed=True).count()
        team_count = TeamMembership.objects.filter(user=profile.user).count()
        rating = Review.average_for(profile.user)
        avg_rating = rating['average'] or 0
        review_count = rating['count']

        # Weighted composite score - completed work and trust (ratings) count
        # for more than raw post volume.
        activity_score = (
            (post_count * 4) +
            (completed_count * 8) +
            (team_count * 3) +
            (review_count * 2) +
            (avg_rating * 5)
        )

        if activity_score <= 0 and post_count == 0 and team_count == 0:
            continue  # skip totally inactive/never-onboarded accounts

        rows.append({
            'profile': profile,
            'post_count': post_count,
            'completed_count': completed_count,
            'team_count': team_count,
            'avg_rating': avg_rating,
            'review_count': review_count,
            'activity_score': round(activity_score, 1),
        })

    rows.sort(key=lambda r: r['activity_score'], reverse=True)

    for i, row in enumerate(rows, start=1):
        row['rank'] = i
        if i == 1:
            row['tier'] = 'gold'
        elif i == 2:
            row['tier'] = 'silver'
        elif i == 3:
            row['tier'] = 'bronze'
        else:
            row['tier'] = ''

    return render(request, 'accounts/leaderboard.html', {
        'rows': rows[:25],
        'top3': rows[:3],
        'rest': rows[3:25],
        'departments': Profile.DEPARTMENT_CHOICES,
        'active_department': dept,
    })
