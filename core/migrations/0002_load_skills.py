from django.db import migrations

def load_skills(apps, schema_editor):
    Skill = apps.get_model('core', 'Skill')

    skills = [
        # Programming Languages
        ('Python',          'programming'),
        ('JavaScript',      'programming'),
        ('Java',            'programming'),
        ('C++',             'programming'),
        ('C#',              'programming'),
        ('PHP',             'programming'),
        ('Swift',           'programming'),
        ('Kotlin',          'programming'),
        ('R',               'programming'),
        ('Go',              'programming'),

        # Frameworks
        ('Django',          'frameworks'),
        ('React',           'frameworks'),
        ('Flutter',         'frameworks'),
        ('Node.js',         'frameworks'),
        ('Laravel',         'frameworks'),
        ('Angular',         'frameworks'),
        ('Vue.js',          'frameworks'),
        ('FastAPI',         'frameworks'),
        ('Spring Boot',     'frameworks'),
        ('Bootstrap',       'frameworks'),

        # AI / Data
        ('Machine Learning',    'ai_data'),
        ('Deep Learning',       'ai_data'),
        ('Data Analysis',       'ai_data'),
        ('NLP',                 'ai_data'),
        ('Computer Vision',     'ai_data'),
        ('TensorFlow',          'ai_data'),
        ('PyTorch',             'ai_data'),
        ('Pandas',              'ai_data'),
        ('Power BI',            'ai_data'),

        # Databases
        ('PostgreSQL',      'databases'),
        ('MySQL',           'databases'),
        ('MongoDB',         'databases'),
        ('Firebase',        'databases'),
        ('SQLite',          'databases'),
        ('Redis',           'databases'),
        ('Oracle',          'databases'),

        # Others
        ('Problem Solving', 'others'),
        ('DevOps',          'others'),
        ('Docker',          'others'),
        ('Git',             'others'),
        ('UI/UX',           'others'),
        ('Figma',           'others'),
        ('Project Management', 'others'),
        ('Content Writing', 'others'),
        ('Cyber Security',  'others'),
        ('Networking',      'others'),
    ]

    for name, category in skills:
        Skill.objects.get_or_create(name=name, defaults={'category': category})


def remove_skills(apps, schema_editor):
    Skill = apps.get_model('core', 'Skill')
    Skill.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),  
    ]

    operations = [
        migrations.RunPython(load_skills, remove_skills),
    ]