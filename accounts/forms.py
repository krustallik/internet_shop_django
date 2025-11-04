from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import date


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(label='Електронна пошта', required=True,
                             widget=forms.EmailInput(
                                 attrs={'placeholder': 'name@example.com', 'class': 'w-full rounded border p-2'}))
    first_name = forms.CharField(label='Ім’я', required=False,
                                 widget=forms.TextInput(
                                     attrs={'placeholder': 'Ім’я', 'class': 'w-full rounded border p-2'}))
    last_name = forms.CharField(label='Прізвище', required=False,
                                widget=forms.TextInput(
                                    attrs={'placeholder': 'Прізвище', 'class': 'w-full rounded border p-2'}))

    bio = forms.CharField(label='Біографія', required=False,
                          widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Коротко про себе',
                                                       'class': 'w-full rounded border p-2'}))
    birth_date = forms.DateField(label='Дата народження', required=False,
                                 widget=forms.DateInput(attrs={'type': 'date', 'class': 'w-full rounded border p-2'}))
    location = forms.CharField(label='Місто', required=False,
                               widget=forms.TextInput(
                                   attrs={'placeholder': 'Ваше місто', 'class': 'w-full rounded border p-2'}))
    website = forms.URLField(label='Веб-сайт', required=False,
                             widget=forms.URLInput(
                                 attrs={'placeholder': 'https://', 'class': 'w-full rounded border p-2'}))
    avatar = forms.ImageField(label='Аватар', required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
        'username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'bio', 'birth_date', 'location',
        'website', 'avatar')
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Логін', 'class': 'w-full rounded border p-2'}),
            'password1': forms.PasswordInput(attrs={'class': 'w-full rounded border p-2'}),
            'password2': forms.PasswordInput(attrs={'class': 'w-full rounded border p-2'}),
        }
        labels = {'username': 'Логін', 'password1': 'Пароль', 'password2': 'Підтвердження пароля'}
        help_texts = {
            'username': 'Латинські літери, цифри та @/./+/-/_',
            'password1': 'Використовуйте надійний пароль.',
            'password2': 'Повторіть пароль.',
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('Такий email вже використовується.')
        return email

    def clean_birth_date(self):
        bd = self.cleaned_data.get('birth_date')
        if bd:
            today = date.today()
            age = today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
            if age < 13:
                raise ValidationError('Вік має бути не менше 13 років.')
        return bd

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            if avatar.size > 5 * 1024 * 1024:
                raise ValidationError('Максимальний розмір файлу — 5MB.')
            main, _, sub = (avatar.content_type or 'application/octet-stream').partition('/')
            if main != 'image' or sub.lower() not in ('jpeg', 'jpg', 'png', 'gif'):
                raise ValidationError('Дозволені формати: JPG, PNG, GIF.')
        return avatar

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        if commit:
            user.save()
            p = user.profile  # створений сигналом
            p.bio = self.cleaned_data.get('bio', '')
            p.birth_date = self.cleaned_data.get('birth_date')
            p.location = self.cleaned_data.get('location', '')
            p.website = self.cleaned_data.get('website', '')
            if self.cleaned_data.get('avatar'):
                p.avatar = self.cleaned_data['avatar']
            p.save()
        return user
