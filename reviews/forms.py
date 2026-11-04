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
            'title': forms.TextInput(attrs={'placeholder': 'A short headline'}),
            'content': forms.Textarea(attrs={'placeholder': 'Share your experience', 'rows': 5}),
            'advantages': forms.Textarea(attrs={'placeholder': 'What did you like?', 'rows': 3}),
            'disadvantages': forms.Textarea(attrs={'placeholder': 'What could be better?', 'rows': 3}),
        }

    def clean_title(self):
        v = (self.cleaned_data.get('title') or '').strip()
        if len(v) < 5:
            raise forms.ValidationError('The headline must contain at least 5 characters.')
        return v

    def clean_content(self):
        v = (self.cleaned_data.get('content') or '').strip()
        if len(v) < 20:
            raise forms.ValidationError('The review must contain at least 20 characters.')
        return v

    def clean_advantages(self):
        return (self.cleaned_data.get('advantages') or '').strip()

    def clean_disadvantages(self):
        return (self.cleaned_data.get('disadvantages') or '').strip()
