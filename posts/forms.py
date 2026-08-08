from django import forms
from .models import Post
from accounts.models import Skill


class PostForm(forms.ModelForm):
    skills_required = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control select2',
            'data-placeholder': 'Search or type required skills...'
        })
    )

    class Meta:
        model  = Post
        fields = ['title', 'post_type', 'description', 'skills_required', 'deadline']
        widgets = {
            'title':       forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Project Title'}),
            'post_type':   forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Describe your project requirements...'}),
            'deadline':    forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['skills_required'].queryset = Skill.objects.all().order_by('name')

        if self.data and 'skills_required' in self.data:
            skill_vals = self.data.getlist('skills_required')
            resolved_ids = []
            for val in skill_vals:
                if val:
                    val_str = str(val).strip()
                    if val_str.isdigit():
                        resolved_ids.append(val_str)
                    else:
                        # Auto-create missing custom skill typed by user
                        skill_obj, _ = Skill.objects.get_or_create(
                            name=val_str,
                            defaults={'category': 'others'}
                        )
                        resolved_ids.append(str(skill_obj.id))

            # Refresh queryset so newly created skills pass validation
            self.fields['skills_required'].queryset = Skill.objects.all().order_by('name')
            mutable_data = self.data.copy()
            mutable_data.setlist('skills_required', resolved_ids)
            self.data = mutable_data

