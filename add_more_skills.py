import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'collabspace.settings')
django.setup()

from core.models import Skill

skills_to_add = [
    # Frameworks / Tools
    ('Docker', 'frameworks'),
    ('Kubernetes', 'frameworks'),
    ('React Native', 'frameworks'),
    ('Node.js', 'frameworks'),
    ('Next.js', 'frameworks'),
    ('Vue.js', 'frameworks'),
    ('Spring Boot', 'frameworks'),
    ('Laravel', 'frameworks'),
    
    # Programming
    ('TypeScript', 'programming'),
    ('Go', 'programming'),
    ('Rust', 'programming'),
    ('Swift', 'programming'),
    ('Kotlin', 'programming'),
    ('PHP', 'programming'),
    ('Ruby', 'programming'),

    # Others
    ('Software Testing', 'others'),
    ('Deployment', 'others'),
    ('UI/UX Design', 'others'),
    ('Cloud Computing', 'others'),
    ('Backend Development', 'others'),
    ('Frontend Development', 'others'),
    ('DevOps', 'others'),
    ('Agile/Scrum', 'others'),
    ('CI/CD', 'others'),
    ('System Design', 'others'),
]

added_count = 0
for name, category in skills_to_add:
    obj, created = Skill.objects.get_or_create(name=name, defaults={'category': category})
    if created:
        added_count += 1

print(f"Added {added_count} new skills.")
