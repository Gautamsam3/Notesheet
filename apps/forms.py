from django import forms
from .models import notesheet
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import profile
from django.db.models import Q
from django.utils.html import format_html
from django.forms.widgets import CheckboxSelectMultiple
from django.contrib.auth import get_user_model
from django import forms
from django.contrib.auth import get_user_model
from django.forms.widgets import CheckboxSelectMultiple
from .models import notesheet, profile

class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email",
                "class": "form-control"
            }
        ))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"
            }
        ))

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "First Name",
                "class": "form-control"
            }
        ))
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Last Name",
                "class": "form-control"
            }
        ))
    username = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control"
            }
        ))
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email",
                "class": "form-control"
            }
        ))
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"
            }
        ))
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password check",
                "class": "form-control"
            }
        ))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')

class CheckboxSelectMultipleUsers(CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = []

        has_id = attrs and 'id' in attrs
        output = []

        for i, (option_value, option_label) in enumerate(self.choices):
            final_attrs = self.build_attrs(attrs, {'type': 'checkbox', 'name': name})

            if has_id:
                final_attrs['id'] = attrs['id'] + '_%s' % i

            cb = forms.CheckboxInput(final_attrs, check_test=self.check_test)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(force_text(option_label))
            output.append(format_html(
                '<label for="{0}">{1} {2}</label>',
                final_attrs['id'], rendered_cb, option_label
            ))

        return mark_safe('\n'.join(output))

class NotesheetForm(forms.ModelForm):
    channels = forms.ModelMultipleChoiceField(
        queryset=get_user_model().objects.all(),
        widget=forms.CheckboxSelectMultiple,  # Use the standard CheckboxSelectMultiple widget
    )

    class Meta:
        model = notesheet
        fields = ['name', 'faculty', 'department', 'event_name', 'event_date', 'event_time', 'intro', 'objective', 'brief_desc', 'reg_fee', 'brochure', 'channels']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(NotesheetForm, self).__init__(*args, **kwargs)
        if user:
            try:
                user_profile = profile.objects.get(user=user)
                self.fields['name'].initial = user_profile.user.username
                self.fields['faculty'].initial = user_profile.faculty
                self.fields['department'].initial = user_profile.department
            except profile.DoesNotExist:
                pass
        self.fields['channels'].queryset = get_user_model().objects.exclude(Q(email=user.email) | Q(email__endswith='@muj.manipal.edu'))
        self.fields['event_date'].widget.attrs.update({'class': 'datepicker'})
        self.fields['event_time'].widget.attrs.update({'class': 'timepicker'})
