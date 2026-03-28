from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile


class RegisterForm(UserCreationForm):
    first_name   = forms.CharField(max_length=50, required=True)
    last_name    = forms.CharField(max_length=50, required=True)
    email        = forms.EmailField(required=True)
    department   = forms.ChoiceField(choices=Profile.DEPARTMENT_CHOICES)
    program      = forms.ChoiceField(choices=Profile.PROGRAM_CHOICES)
    semester     = forms.ChoiceField(choices=Profile.SEMESTER_CHOICES)
    photo        = forms.ImageField(required=False)
    bio          = forms.CharField(max_length=200, required=False,
                       widget=forms.Textarea(attrs={'rows': 3}))
    github       = forms.URLField(required=False)
    linkedin     = forms.URLField(required=False)
    looking_for  = forms.ChoiceField(choices=Profile.LOOKING_FOR)
    availability = forms.ChoiceField(choices=Profile.AVAILABILITY)

    class Meta:
        model  = User
        fields = ['first_name', 'last_name', 'username', 'email',
                  'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def save(self, commit=True):
        user            = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name  = self.cleaned_data['last_name']
        user.email      = self.cleaned_data['email']
        if commit:
            user.save()
            Profile.objects.create(
                user         = user,
                department   = self.cleaned_data['department'],
                program      = self.cleaned_data['program'],
                semester     = self.cleaned_data['semester'],
                photo        = self.cleaned_data.get('photo'),
                bio          = self.cleaned_data.get('bio', ''),
                github       = self.cleaned_data.get('github', ''),
                linkedin     = self.cleaned_data.get('linkedin', ''),
                looking_for  = self.cleaned_data['looking_for'],
                availability = self.cleaned_data['availability'],
            )
        return user


# Make all fields use Bootstrap styling
for field_name, field in RegisterForm.base_fields.items():
    if hasattr(field.widget, 'attrs'):
        if field.widget.__class__.__name__ == 'Textarea':
            field.widget.attrs.update({'class': 'form-control'})
        elif field.widget.__class__.__name__ == 'Select':
            field.widget.attrs.update({'class': 'form-select'})
        elif field.widget.__class__.__name__ == 'ClearableFileInput':
            field.widget.attrs.update({'class': 'form-control'})
        else:
            field.widget.attrs.update({'class': 'form-control'})


from .models import Profile, Post

class PostForm(forms.ModelForm):
    class Meta:
        model  = Post
        fields = ['title', 'post_type', 'description', 'skills_required', 'deadline']
        widgets = {
            'description':     forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'deadline':        forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'skills_required': forms.CheckboxSelectMultiple(),
            'title':           forms.TextInput(attrs={'class': 'form-control'}),
            'post_type':       forms.Select(attrs={'class': 'form-select'}),
        }