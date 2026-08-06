import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required


@login_required
def ai_suggest(request):
    if request.method == 'POST':
        data     = json.loads(request.body)
        keywords = data.get('keywords', '').lower()

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

        result = suggestions['default']
        for key in suggestions:
            if key in keywords:
                result = suggestions[key]
                break

        return JsonResponse(result)

    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def chatbot(request):
    if request.method == 'POST':
        data     = json.loads(request.body)
        question = data.get('question', '').lower().strip()

        responses = {
            'what is collabspace': 'CollabSpace is a platform built for Pakistani university students to find partners for their Final Year Projects (FYP) and paid tasks. You can post your project, browse others, and message students directly.',
            'what is this website': 'This is CollabSpace — a student collaboration platform where you can find FYP partners, post paid tasks, and connect with skilled students at your university.',
            'how does it work': 'It is simple! Register → Add your skills → Post your FYP idea or browse others → Message the right student → Collaborate. Everything happens right here on the platform.',

            'how to register': 'Click the Register button at the top. Fill in your name, email, university details, program, and semester. After registering, login and add your skills from your profile page.',
            'how to login': 'Click the Login button at the top. Enter your email and password. You will be redirected to the Tasks feed after logging in.',
            'forgot password': 'Currently password reset is not available. Please contact your administrator or create a new account.',

            'how to post': 'After logging in, click Add Post in the navbar. Fill in the title, type (FYP or Paid Task), description, required skills, and deadline. Then submit!',
            'how to add post': 'Go to Add Post from the navbar. Fill in your project details and click Create Post. Your post will appear in the Tasks feed for other students.',
            'what is fyp': 'FYP stands for Final Year Project. It is the major project every university student completes in their final year. CollabSpace helps you find the right teammates for it.',
            'what is paid task': 'A Paid Task is a project where you pay a skilled student to complete specific work — like building a website, making a mobile app, or analysing data.',

            'how to add skills': 'Go to your Profile page and click Edit Skills. You will see skills grouped by category — Programming, Frameworks, AI/Data, Databases, and Others. Check the ones you know and set your proficiency level.',
            'what skills are available': 'We have skills in 5 categories: Programming Languages (Python, Java, C++), Frameworks (Django, React, Flutter), AI/Data (Machine Learning, NLP), Databases (PostgreSQL, MySQL), and Others (DevOps, UI/UX, Git).',

            'how to message': 'Find a post you like in the Tasks feed and click the Message button on that post. You can also click on a student username to view their profile and message them from there.',
            'how to chat': 'Click Messages in the navbar to see your inbox. Click any contact to open the chat. Type your message and press Send.',
            'how to find messages': 'Click Messages in the top navbar to open your inbox. All your conversations will be listed there.',

            'how to edit profile': 'Currently you can update your skills from the Edit Skills button on your profile page. Full profile editing will be available soon.',
            'how to view profile': 'Click on any student username in the Tasks feed to view their full profile — skills, posts, department, and contact info.',

            'what is ai suggest': 'The AI Suggester on the Add Post page helps you write a professional title and description. Just type a few keywords like "machine learning healthcare" and click Suggest!',
            'how does ai work': 'Type keywords about your project in the AI Suggester box on the Add Post page. The AI will generate a professional title and description for you automatically.',

            'is it free': 'Yes! CollabSpace is completely free for all university students. Just register and start collaborating.',
            'which universities': 'CollabSpace is open to students from all Pakistani universities — FAST, NUST, COMSATS, UET, IBA, LUMS and more.',
            'hello': 'Hello! 👋 Welcome to CollabSpace. I am here to help you. Ask me anything about how to use the platform!',
            'hi': 'Hi there! 👋 I am the CollabSpace assistant. How can I help you today?',
            'help': 'Sure! Here are some things I can help with:\n• How to register or login\n• How to post a project\n• How to find and message students\n• How to add your skills\n• What FYP and Paid Tasks mean\n\nJust ask your question!',
            'thank you': 'You are welcome! 😊 Feel free to ask if you need anything else.',
            'thanks': 'Happy to help! 😊 Good luck with your FYP!',
        }

        reply = None
        for key in responses:
            if key in question:
                reply = responses[key]
                break

        if not reply:
            reply = "I am not sure about that yet. Here are some things I can help with: registering, adding skills, posting a project, messaging students, or understanding FYP vs Paid Tasks. Try asking one of those!"

        return JsonResponse({'reply': reply})

    return JsonResponse({'error': 'Invalid'}, status=400)
