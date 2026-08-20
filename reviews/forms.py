from django import forms
from .models import Review, Report


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'How was working with this student? (optional)'
            }),
        }


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['reason', 'details']
        widgets = {
            'reason': forms.Select(attrs={'class': 'form-select'}),
            'details': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'Give a few details to help our moderators review this quickly...'
            }),
        }
