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


def _send_verification_email(user, request=None):
    try:
        verification, _ = EmailVerification.objects.get_or_create(
            user=user, defaults={'token': EmailVerification.generate_token()}
        )
        if not verification.token:
            verification.token = EmailVerification.generate_token()
            verification.save()
        
        if request:
            domain = request.build_absolute_uri('/')[:-1]
        else:
            domain = getattr(settings, 'SITE_DOMAIN', 'http://127.0.0.1:8000')

        verify_url = f"{domain}/verify-email/{verification.token}/"
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
    except Exception:
        pass



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
        _send_verification_email(user, request)

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
        _send_verification_email(request.user, request)
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

