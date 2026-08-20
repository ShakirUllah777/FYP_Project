import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.contrib import messages

from . import services


@login_required
def ai_suggest(request):
    """Generates a project title + description from keywords. Uses a real
    LLM call (Claude) when ANTHROPIC_API_KEY is configured, otherwise
    falls back to the platform's built-in rule-based suggestions."""
    if request.method == 'POST':
        data = json.loads(request.body)
        keywords = data.get('keywords', '')

        result = services.generate_post_suggestion(keywords)

        # Bonus: also estimate scope so the Add Post modal can preview it.
        complexity, timeline = services.estimate_complexity(result.get('description', ''))
        result['estimated_complexity'] = complexity
        result['estimated_timeline'] = timeline

        return JsonResponse(result)

    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def chatbot(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        question = data.get('question', '').strip()
        reply = services.chatbot_reply(question)
        return JsonResponse({'reply': reply})

    return JsonResponse({'error': 'Invalid'}, status=400)


@login_required
def resume_skill_extractor(request):
    """AI CV/resume skill extractor: upload your resume file (PDF/DOCX/TXT)
    or paste the text directly, and get back matching platform skills plus
    an auto-filled bio, GitHub and LinkedIn — reviewable before it's applied
    to your profile in one click (feature: Smart Profile Auto-Fill)."""
    from accounts.models import Skill, UserSkill

    extracted = []
    profile_details = None
    resume_text = ''

    if request.method == 'POST':
        uploaded_file = request.FILES.get('resume_file')
        resume_text = request.POST.get('resume_text', '').strip()

        if uploaded_file:
            resume_text = services.extract_text_from_resume_file(uploaded_file)
            if not resume_text.strip():
                file_name = (uploaded_file.name or '').lower()
                if file_name.endswith('.doc'):
                    messages.error(
                        request,
                        "That's an old-style .doc file, which isn't supported. Please save it as "
                        ".docx or .pdf, or paste your resume text directly instead."
                    )
                else:
                    messages.error(
                        request,
                        "Couldn't read that file. Please try a PDF/DOCX with selectable text, "
                        "or paste your resume text directly instead."
                    )

        if resume_text:
            known_names = list(Skill.objects.values_list('name', flat=True))
            matched_names = services.extract_skills_from_text(resume_text, known_names)
            extracted = Skill.objects.filter(name__in=matched_names)
            profile_details = services.extract_profile_details_from_resume(resume_text)

        if 'confirm' in request.POST:
            resume_text = request.POST.get('resume_text_hidden', resume_text)
            selected_ids = request.POST.getlist('selected_skills')
            added = 0
            for sid in selected_ids:
                skill = Skill.objects.filter(pk=sid).first()
                if skill:
                    proficiency = services.guess_skill_proficiency(resume_text, skill.name)
                    _, created = UserSkill.objects.get_or_create(
                        user=request.user, skill=skill, defaults={'proficiency': proficiency}
                    )
                    added += 1 if created else 0

            # --- Auto-fill the rest of the profile (bio / GitHub / LinkedIn) ---
            profile = request.user.profile
            filled_fields = []
            if request.POST.get('apply_bio') and request.POST.get('bio_value'):
                profile.bio = request.POST.get('bio_value')[:200]
                filled_fields.append('bio')
            if request.POST.get('apply_github') and request.POST.get('github_value'):
                profile.github = request.POST.get('github_value')
                filled_fields.append('GitHub')
            if request.POST.get('apply_linkedin') and request.POST.get('linkedin_value'):
                profile.linkedin = request.POST.get('linkedin_value')
                filled_fields.append('LinkedIn')

            if uploaded_file:
                profile.resume = uploaded_file
                from django.utils import timezone
                profile.resume_updated_at = timezone.now()

            profile.save()

            summary = f'{added} new skill(s) added'
            if filled_fields:
                summary += f', and {", ".join(filled_fields)} auto-filled'
            messages.success(request, summary + ' on your profile.')
            return redirect('my_profile')

    return render(request, 'assistant/resume_extractor.html', {
        'extracted': extracted,
        'profile_details': profile_details,
        'resume_text': resume_text,
    })
