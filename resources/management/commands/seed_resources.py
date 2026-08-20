from django.core.management.base import BaseCommand
from resources.models import Resource

DEFAULT_RESOURCES = [
    {
        'title': 'FYP Proposal Template',
        'category': 'proposal',
        'description': 'Standard structure for an FYP proposal document: problem statement, objectives, scope, tools, and timeline.',
        'external_link': 'https://docs.google.com/document/',
    },
    {
        'title': 'Software Requirements Specification (SRS) Template',
        'category': 'srs',
        'description': 'IEEE-style SRS template covering functional/non-functional requirements, use cases, and system diagrams.',
        'external_link': 'https://docs.google.com/document/',
    },
    {
        'title': 'Final Year Project Report Template',
        'category': 'report',
        'description': 'Full report structure: abstract, literature review, methodology, implementation, results, and conclusion.',
        'external_link': 'https://docs.google.com/document/',
    },
    {
        'title': 'FYP Defense Evaluation Checklist',
        'category': 'checklist',
        'description': 'What panels typically check during a final defense - demo readiness, documentation, individual contribution clarity.',
        'external_link': 'https://docs.google.com/document/',
    },
    {
        'title': 'Choosing a Good FYP Topic - Guideline',
        'category': 'guideline',
        'description': 'How to scope an FYP idea that is original, feasible in one/two semesters, and defensible.',
        'external_link': 'https://docs.google.com/document/',
    },
    {
        'title': 'Mid-Evaluation Presentation Guideline',
        'category': 'guideline',
        'description': 'What to include in your mid-term progress presentation to supervisors and panels.',
        'external_link': 'https://docs.google.com/document/',
    },
]


class Command(BaseCommand):
    help = 'Seeds the resource library with default FYP document templates.'

    def handle(self, *args, **options):
        created_count = 0
        for item in DEFAULT_RESOURCES:
            _, created = Resource.objects.get_or_create(
                title=item['title'],
                defaults={
                    'category': item['category'],
                    'description': item['description'],
                    'external_link': item.get('external_link', ''),
                }
            )
            if created:
                created_count += 1
        self.stdout.write(self.style.SUCCESS(
            f'Seeded resources: {created_count} created, {len(DEFAULT_RESOURCES) - created_count} already existed.'
        ))
