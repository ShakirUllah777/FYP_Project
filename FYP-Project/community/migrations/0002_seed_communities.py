from django.db import migrations


COMMUNITY_SEED = [
    {
        'name': 'Web Development',
        'description': 'Frontend, backend & full-stack builders shipping web apps.',
        'icon': 'bi-globe2',
        'color': '#1B6FFF',
        'order': 1,
        'skills': ['HTML5 / CSS3', 'JavaScript', 'TypeScript', 'React.js', 'Vue.js', 'Angular',
                   'Next.js', 'Django', 'Flask', 'Node.js', 'Express.js', 'Frontend Development',
                   'Backend Development', 'Full Stack Development', 'Bootstrap', 'Tailwind CSS'],
    },
    {
        'name': 'Cybersecurity',
        'description': 'Ethical hacking, network security & pen-testing enthusiasts.',
        'icon': 'bi-shield-lock-fill',
        'color': '#E63946',
        'order': 2,
        'skills': ['Cybersecurity', 'Ethical Hacking & Pen Testing', 'Network Security',
                   'Cryptography', 'OWASP Security Standards', 'Software Testing / QA'],
    },
    {
        'name': 'Python Developers',
        'description': 'Everything Python - scripting, web backends & automation.',
        'icon': 'bi-filetype-py',
        'color': '#F5A623',
        'order': 3,
        'skills': ['Python', 'Django', 'Flask', 'FastAPI', 'Pandas & NumPy'],
    },
    {
        'name': 'AI & Machine Learning',
        'description': 'Model builders working on ML, deep learning & LLMs.',
        'icon': 'bi-cpu-fill',
        'color': '#7C5CFF',
        'order': 4,
        'skills': ['Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch',
                   'Artificial Intelligence', 'Generative AI / LLMs',
                   'Natural Language Processing (NLP)', 'Computer Vision', 'Prompt Engineering'],
    },
    {
        'name': 'Mobile App Developers',
        'description': 'Android, iOS & cross-platform mobile app builders.',
        'icon': 'bi-phone-fill',
        'color': '#12B76A',
        'order': 5,
        'skills': ['Flutter', 'React Native', 'Android Development (Kotlin/Java)',
                   'iOS Development (Swift/SwiftUI)', 'Cross-Platform Mobile Dev', 'Kotlin',
                   'Swift', 'Dart'],
    },
    {
        'name': 'Data Science & Analytics',
        'description': 'Turning raw data into insight, dashboards & decisions.',
        'icon': 'bi-bar-chart-fill',
        'color': '#0EA5E9',
        'order': 6,
        'skills': ['Data Science', 'Data Analytics', 'Data Visualization',
                   'Tableau & Power BI', 'R', 'Big Data & Spark'],
    },
    {
        'name': 'DevOps & Cloud',
        'description': 'CI/CD, containers & cloud infrastructure practitioners.',
        'icon': 'bi-cloud-fill',
        'color': '#334155',
        'order': 7,
        'skills': ['Docker', 'Kubernetes', 'Amazon Web Services (AWS)', 'Microsoft Azure',
                   'Google Cloud Platform (GCP)', 'CI/CD Pipelines', 'Terraform',
                   'Linux Administration'],
    },
    {
        'name': 'UI/UX & Design',
        'description': 'Product design, wireframing & delightful interfaces.',
        'icon': 'bi-palette-fill',
        'color': '#FF5B7A',
        'order': 8,
        'skills': ['UI/UX Design', 'Figma', 'Adobe XD', 'Wireframing & Prototyping',
                   'Responsive Web Design'],
    },
    {
        'name': 'Game Development',
        'description': 'Building games and interactive experiences with Unity/Unreal.',
        'icon': 'bi-controller',
        'color': '#6D28D9',
        'order': 9,
        'skills': ['Game Development (Unity/Unreal Engine)', 'C#', 'C++'],
    },
]


def seed_communities(apps, schema_editor):
    Community = apps.get_model('community', 'Community')
    Skill = apps.get_model('accounts', 'Skill')

    for entry in COMMUNITY_SEED:
        community, _ = Community.objects.get_or_create(
            name=entry['name'],
            defaults={
                'description': entry['description'],
                'icon': entry['icon'],
                'color': entry['color'],
                'order': entry['order'],
                'slug': entry['name'].lower().replace(' & ', '-').replace(' ', '-').replace('/', '-'),
            },
        )
        skill_objs = Skill.objects.filter(name__in=entry['skills'])
        community.related_skills.set(skill_objs)


def unseed_communities(apps, schema_editor):
    Community = apps.get_model('community', 'Community')
    Community.objects.filter(name__in=[e['name'] for e in COMMUNITY_SEED]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0001_initial'),
        ('accounts', '0003_profile_resume_profile_resume_updated_at'),
    ]

    operations = [
        migrations.RunPython(seed_communities, unseed_communities),
    ]
