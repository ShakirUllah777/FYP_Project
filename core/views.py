from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm
from .models import Profile, Skill, UserSkill, Post, Message
from .forms import RegisterForm, PostForm
import json
from django.http import JsonResponse


def home(request):
    return render(request, 'home.html')


def register(request):
    if request.user.is_authenticated:
        return redirect('tasks')
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created! Please login.')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('tasks')
    if request.method == 'POST':
        email    = request.POST.get('email')
        password = request.POST.get('password')
        try:
            username = User.objects.get(email=email).username
            user     = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('tasks')
        except User.DoesNotExist:
            pass
        messages.error(request, 'Invalid email or password.')
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def tasks(request):
    return render(request, 'tasks.html')


@login_required
def my_profile(request):
    profile     = request.user.profile
    user_skills = UserSkill.objects.filter(user=request.user).select_related('skill')
    posts       = Post.objects.filter(author=request.user)
    return render(request, 'profile.html', {
        'profile':     profile,
        'user_skills': user_skills,
        'posts':       posts,
        'is_own':      True,
    })


@login_required
def user_profile(request, username):
    viewed_user = get_object_or_404(User, username=username)
    profile     = viewed_user.profile
    user_skills = UserSkill.objects.filter(user=viewed_user).select_related('skill')
    posts       = Post.objects.filter(author=viewed_user)
    return render(request, 'profile.html', {
        'profile':     profile,
        'user_skills': user_skills,
        'posts':       posts,
        'is_own':      False,
        'viewed_user': viewed_user,
    })


@login_required
def add_skills(request):
    categories  = Skill.CATEGORY_CHOICES
    all_skills  = Skill.objects.all().order_by('category', 'name')
    user_skills = UserSkill.objects.filter(user=request.user)
    user_skill_ids = list(user_skills.values_list('skill_id', flat=True))
    user_skill_prof = {us.skill_id: us.proficiency for us in user_skills}

    if request.method == 'POST':
        UserSkill.objects.filter(user=request.user).delete()
        skill_ids = request.POST.getlist('skills')
        for sid in skill_ids:
            skill       = get_object_or_404(Skill, id=sid)
            proficiency = request.POST.get(f'proficiency_{sid}', 'beginner')
            UserSkill.objects.create(
                user=request.user, skill=skill, proficiency=proficiency
            )
        messages.success(request, 'Skills updated!')
        return redirect('my_profile')

    return render(request, 'add_skills.html', {
        'categories':      categories,
        'all_skills':      all_skills,
        'user_skill_ids':  user_skill_ids,
        'user_skill_prof': user_skill_prof,
    })



@login_required
def add_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post        = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            messages.success(request, 'Post created successfully!')
            return redirect('tasks')
    else:
        form = PostForm()
    return render(request, 'add_post.html', {'form': form, 'editing': False})


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
    return render(request, 'add_post.html', {'form': form, 'editing': True})


@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted.')
    return redirect('my_posts')


@login_required
def my_posts(request):
    posts = Post.objects.filter(author=request.user)
    return render(request, 'my_posts.html', {'posts': posts})


@login_required
def tasks(request):
    posts        = Post.objects.exclude(author=request.user).select_related('author__profile')
    skill_filter = request.GET.get('skill')
    type_filter  = request.GET.get('type')
    if skill_filter:
        posts = posts.filter(skills_required__name=skill_filter)
    if type_filter:
        posts = posts.filter(post_type=type_filter)
    skills = Skill.objects.all()
    return render(request, 'tasks.html', {'posts': posts, 'skills': skills})

@login_required
def inbox(request):
    sent     = Message.objects.filter(sender=request.user).values_list('receiver', flat=True)
    received = Message.objects.filter(receiver=request.user).values_list('sender', flat=True)
    user_ids = set(list(sent) + list(received))
    contacts = User.objects.filter(id__in=user_ids)

    # Build list of (contact, unread_count) tuples
    contacts_data = []
    for c in contacts:
        unread = Message.objects.filter(
            sender=c, receiver=request.user, is_read=False
        ).count()
        contacts_data.append((c, unread))

    return render(request, 'messages_inbox.html', {
        'contacts_data': contacts_data,
    })


@login_required
def chat(request, username):
    other_user = get_object_or_404(User, username=username)

    # Mark messages as read
    Message.objects.filter(
        sender=other_user, receiver=request.user, is_read=False
    ).update(is_read=True)

    messages_qs = Message.objects.filter(
        sender__in=[request.user, other_user],
        receiver__in=[request.user, other_user]
    ).order_by('sent_at')

    return render(request, 'chat.html', {
        'other_user':    other_user,
        'messages':      messages_qs,
        'other_profile': other_user.profile,
    })


@login_required
def send_message(request):
    if request.method == 'POST':
        receiver_username = request.POST.get('receiver')
        content           = request.POST.get('content', '').strip()
        if content:
            receiver = get_object_or_404(User, username=receiver_username)
            Message.objects.create(
                sender=request.user,
                receiver=receiver,
                content=content
            )
        return redirect('chat', username=receiver_username)
    return redirect('inbox')


@login_required
def ai_suggest(request):
    if request.method == 'POST':
        data     = json.loads(request.body)
        keywords = data.get('keywords', '').lower()

        # ── DUMMY RESPONSES ──────────────────────────────
        # Later: replace this whole block with real API call
        suggestions = {
            'machine learning': {
                'title': 'AI-Powered Prediction System Using Machine Learning',
                'description': 'This project focuses on building an intelligent prediction system using machine learning algorithms. The system will analyse historical data, identify patterns, and provide accurate predictions to help users make better decisions.'
            },
            'web': {
                'title': 'Full Stack Web Application with Modern Technologies',
                'description': 'A complete web-based platform built using modern frontend and backend technologies. The application will include user authentication, real-time data handling, and a clean responsive interface.'
            },
            'mobile': {
                'title': 'Cross-Platform Mobile Application for Students',
                'description': 'A mobile application developed for university students to manage their daily academic activities. The app will support both Android and iOS platforms with an intuitive user interface.'
            },
            'database': {
                'title': 'Intelligent Database Management and Analytics System',
                'description': 'A robust database management system with built-in analytics and reporting features. The project will handle large datasets efficiently and provide visual insights through interactive dashboards.'
            },
            'chatbot': {
                'title': 'AI Chatbot for University Student Support',
                'description': 'An intelligent conversational chatbot designed to assist university students with their queries. The system uses natural language processing to understand questions and provide helpful, accurate responses.'
            },
            'ecommerce': {
                'title': 'E-Commerce Platform with Smart Recommendation Engine',
                'description': 'A fully functional online shopping platform with an AI-powered product recommendation engine. The system will personalise user experience based on browsing history and purchase patterns.'
            },
            'security': {
                'title': 'Network Security Monitoring and Threat Detection System',
                'description': 'A cybersecurity tool that continuously monitors network traffic to detect and alert on potential threats. The system uses pattern recognition to identify suspicious activities in real time.'
            },
            'image': {
                'title': 'Image Recognition and Classification System Using Deep Learning',
                'description': 'A deep learning based image recognition system capable of classifying objects with high accuracy. The project will use convolutional neural networks trained on large image datasets.'
            },
            'healthcare': {
                'title': 'Smart Healthcare Management System with Patient Analytics',
                'description': 'A digital healthcare platform that manages patient records, appointments, and medical history. The system includes analytics to help doctors identify health trends and improve patient care.'
            },
            'default': {
                'title': 'Innovative Software Solution for Real World Problem',
                'description': 'A well-structured software project that addresses a real world challenge using modern technologies. The system will be designed with scalability, performance, and user experience as core priorities.'
            },
        }

        # Match keywords to a suggestion
        result = suggestions['default']
        for key in suggestions:
            if key in keywords:
                result = suggestions[key]
                break

        return JsonResponse(result)

    return JsonResponse({'error': 'Invalid request'}, status=400)

    '''
    # REPLACE THIS in ai_suggest view:
    result = suggestions['default']
    for key in suggestions:
        if key in keywords:
            result = suggestions[key]
            break

    # WITH THIS (real API):
    client   = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model    = "gpt-3.5-turbo",
        messages = [{"role":"user","content":f"Generate a project title and description for: {keywords}"}],
        max_tokens = 200
    )
    # parse response...
    '''

@login_required
def seniors(request):
    search   = request.GET.get('search', '').strip()
    semester = request.GET.get('semester', '').strip()

    seniors_qs = Profile.objects.filter(
        semester__in=[6, 7, 8]
    ).exclude(
        user=request.user
    ).select_related('user')

    # Search by name or username
    if search:
        seniors_qs = seniors_qs.filter(
            user__first_name__icontains=search
        ) | seniors_qs.filter(
            user__last_name__icontains=search
        ) | seniors_qs.filter(
            user__username__icontains=search
        )

    # Filter by semester
    if semester:
        seniors_qs = seniors_qs.filter(semester=semester)

    seniors_qs = seniors_qs[:10]

    return render(request, 'seniors.html', {
        'seniors':  seniors_qs,
        'search':   search,
        'semester': semester,
    })



@login_required
def chatbot(request):
    if request.method == 'POST':
        data     = json.loads(request.body)
        question = data.get('question', '').lower().strip()

        # ── DUMMY RESPONSES ──────────────────────────
        # Later: replace with real Claude/OpenAI API call
        responses = {
            # About the platform
            'what is collabspace': 'CollabSpace is a platform built for Pakistani university students to find partners for their Final Year Projects (FYP) and paid tasks. You can post your project, browse others, and message students directly.',
            'what is this website': 'This is CollabSpace — a student collaboration platform where you can find FYP partners, post paid tasks, and connect with skilled students at your university.',
            'how does it work': 'It is simple! Register → Add your skills → Post your FYP idea or browse others → Message the right student → Collaborate. Everything happens right here on the platform.',

            # Registration / Login
            'how to register': 'Click the Register button at the top. Fill in your name, email, university details, program, and semester. After registering, login and add your skills from your profile page.',
            'how to login': 'Click the Login button at the top. Enter your email and password. You will be redirected to the Tasks feed after logging in.',
            'forgot password': 'Currently password reset is not available. Please contact your administrator or create a new account.',

            # Posts
            'how to post': 'After logging in, click Add Post in the navbar. Fill in the title, type (FYP or Paid Task), description, required skills, and deadline. Then submit!',
            'how to add post': 'Go to Add Post from the navbar. Fill in your project details and click Create Post. Your post will appear in the Tasks feed for other students.',
            'what is fyp': 'FYP stands for Final Year Project. It is the major project every university student completes in their final year. CollabSpace helps you find the right teammates for it.',
            'what is paid task': 'A Paid Task is a project where you pay a skilled student to complete specific work — like building a website, making a mobile app, or analysing data.',

            # Skills
            'how to add skills': 'Go to your Profile page and click Edit Skills. You will see skills grouped by category — Programming, Frameworks, AI/Data, Databases, and Others. Check the ones you know and set your proficiency level.',
            'what skills are available': 'We have skills in 5 categories: Programming Languages (Python, Java, C++), Frameworks (Django, React, Flutter), AI/Data (Machine Learning, NLP), Databases (PostgreSQL, MySQL), and Others (DevOps, UI/UX, Git).',

            # Messaging
            'how to message': 'Find a post you like in the Tasks feed and click the Message button on that post. You can also click on a student username to view their profile and message them from there.',
            'how to chat': 'Click Messages in the navbar to see your inbox. Click any contact to open the chat. Type your message and press Send.',
            'how to find messages': 'Click Messages in the top navbar to open your inbox. All your conversations will be listed there.',

            # Profile
            'how to edit profile': 'Currently you can update your skills from the Edit Skills button on your profile page. Full profile editing will be available soon.',
            'how to view profile': 'Click on any student username in the Tasks feed to view their full profile — skills, posts, department, and contact info.',

            # AI feature
            'what is ai suggest': 'The AI Suggester on the Add Post page helps you write a professional title and description. Just type a few keywords like "machine learning healthcare" and click Suggest!',
            'how does ai work': 'Type keywords about your project in the AI Suggester box on the Add Post page. The AI will generate a professional title and description for you automatically.',

            # General
            'is it free': 'Yes! CollabSpace is completely free for all university students. Just register and start collaborating.',
            'which universities': 'CollabSpace is open to students from all Pakistani universities — FAST, NUST, COMSATS, UET, IBA, LUMS and more.',
            'hello': 'Hello! 👋 Welcome to CollabSpace. I am here to help you. Ask me anything about how to use the platform!',
            'hi': 'Hi there! 👋 I am the CollabSpace assistant. How can I help you today?',
            'help': 'Sure! Here are some things I can help with:\n• How to register or login\n• How to post a project\n• How to find and message students\n• How to add your skills\n• What FYP and Paid Tasks mean\n\nJust ask your question!',
            'thank you': 'You are welcome! 😊 Feel free to ask if you need anything else.',
            'thanks': 'Happy to help! 😊 Good luck with your FYP!',
        }

        # Find best matching response
        reply = None
        for key in responses:
            if key in question:
                reply = responses[key]
                break

        # Default response
        if not reply:
            reply = "I am not sure about that yet. Here are some things I can help with: registering, adding skills, posting a project, messaging students, or understanding FYP vs Paid Tasks. Try asking one of those!"

        return JsonResponse({'reply': reply})

    return JsonResponse({'error': 'Invalid'}, status=400)

    '''
        # REPLACE dummy block with:
        from anthropic import Anthropic
        client   = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        message  = client.messages.create(
            model      = "claude-opus-4-6",
            max_tokens = 300,
            messages   = [{"role":"user","content": question}]
        )
        reply = message.content[0].text
    '''


