from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model  = Post
        fields = ['title', 'post_type', 'description', 'skills_required', 'deadline']
        widgets = {
            'title':           forms.TextInput(attrs={'class': 'form-control'}),
            'post_type':       forms.Select(attrs={'class': 'form-select'}),
            'description':     forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'skills_required': forms.SelectMultiple(attrs={'class': 'form-control select2', 'data-placeholder': 'Search and select skills...'}),
            'deadline':        forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
