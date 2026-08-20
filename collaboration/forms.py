from django import forms
from .models import TaskItem, Milestone, ProjectFile, MeetingLink, Endorsement


class TaskItemForm(forms.ModelForm):
    class Meta:
        model = TaskItem
        fields = ['title', 'description', 'assigned_to', 'priority', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Task title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Details (optional)'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, team=None, **kwargs):
        super().__init__(*args, **kwargs)
        if team is not None:
            self.fields['assigned_to'].queryset = team.members.all()
        self.fields['assigned_to'].required = False


class MilestoneForm(forms.ModelForm):
    class Meta:
        model = Milestone
        fields = ['title', 'description', 'due_date', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Proposal Submission'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Short note (optional)'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class ProjectFileForm(forms.ModelForm):
    class Meta:
        model = ProjectFile
        fields = ['file', 'description']
        widgets = {
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'What is this file? (optional)'}),
        }


class MeetingLinkForm(forms.ModelForm):
    class Meta:
        model = MeetingLink
        fields = ['title', 'link', 'scheduled_for']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Weekly Sync'}),
            'link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://meet.google.com/xyz-abcd'}),
            'scheduled_for': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }


class EndorsementForm(forms.ModelForm):
    class Meta:
        model = Endorsement
        fields = ['status', 'remarks']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Feedback for the student team...'}),
        }
