from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(
        choices=Review.RATING_CHOICES,
        widget=forms.RadioSelect
    )

    class Meta:
        model = Review
        fields = ['rating', 'title', 'content', 'advantages', 'disadvantages']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Короткий заголовок'}),
            'content': forms.Textarea(attrs={'placeholder': 'Детальний відгук', 'rows': 5}),
            'advantages': forms.Textarea(attrs={'placeholder': 'Переваги', 'rows': 3}),
            'disadvantages': forms.Textarea(attrs={'placeholder': 'Недоліки', 'rows': 3}),
        }

    def clean_title(self):
        v = (self.cleaned_data.get('title') or '').strip()
        if len(v) < 5:
            raise forms.ValidationError('Заголовок має містити щонайменше 5 символів.')
        return v

    def clean_content(self):
        v = (self.cleaned_data.get('content') or '').strip()
        if len(v) < 20:
            raise forms.ValidationError('Текст відгуку має містити щонайменше 20 символів.')
        return v

    def clean_advantages(self):
        return (self.cleaned_data.get('advantages') or '').strip()

    def clean_disadvantages(self):
        return (self.cleaned_data.get('disadvantages') or '').strip()
