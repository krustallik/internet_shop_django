from django import forms

from .models import Discount, PromoCode


COMMON_INPUT = (
    "w-full px-4 py-2 border rounded-lg "
    "focus:outline-none focus:ring-2 focus:ring-indigo-500"
)


class DiscountForm(forms.ModelForm):
    discount_type = forms.ChoiceField(
        choices=Discount.DISCOUNT_TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "flex gap-4"}),
        label='Discount type',
    )

    class Meta:
        model = Discount
        fields = [
            'discount_type',
            'value',
            'start_date',
            'end_date',
            'min_quantity',
            'description',
            'is_active',
        ]
        widgets = {
            'value': forms.NumberInput(attrs={
                'class': COMMON_INPUT,
                'placeholder': '20 for 20% or 100 for a fixed amount',
            }),
            'start_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': COMMON_INPUT,
            }),
            'end_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': COMMON_INPUT,
            }),
            'min_quantity': forms.NumberInput(attrs={
                'class': COMMON_INPUT,
                'min': 1,
            }),
            'description': forms.Textarea(attrs={
                'class': COMMON_INPUT,
                'rows': 3,
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-indigo-600 border-gray-300 rounded',
            }),
        }

    def clean_value(self):
        value = self.cleaned_data.get('value')
        t = self.cleaned_data.get('discount_type')
        if value is None:
            return value
        if t == Discount.DISCOUNT_TYPE_PERCENTAGE and not (0 < value <= 100):
            raise forms.ValidationError('Enter a percentage greater than 0 and no more than 100.')
        if t == Discount.DISCOUNT_TYPE_FIXED and value <= 0:
            raise forms.ValidationError('Enter a fixed discount greater than 0.')
        return value

    def clean_min_quantity(self):
        q = self.cleaned_data.get('min_quantity') or 1
        if q < 1:
            raise forms.ValidationError('The minimum quantity is 1.')
        return q

    def clean(self):
        data = super().clean()
        s, e = data.get('start_date'), data.get('end_date')
        if s and e and e <= s:
            self.add_error('end_date', 'The end date must be after the start date.')
        return data


class PromoCodeForm(forms.ModelForm):
    class Meta:
        model = PromoCode
        fields = [
            'code',
            'discount_type',
            'value',
            'start_date',
            'end_date',
            'usage_limit',
            'min_order_amount',
            'description',
            'is_active',
        ]
        widgets = {
            'code': forms.TextInput(attrs={
                'class': COMMON_INPUT,
                'placeholder': 'SUMMER2025',
            }),
            'discount_type': forms.Select(attrs={'class': COMMON_INPUT}),
            'value': forms.NumberInput(attrs={'class': COMMON_INPUT}),
            'start_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local', 'class': COMMON_INPUT,
            }),
            'end_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local', 'class': COMMON_INPUT,
            }),
            'usage_limit': forms.NumberInput(attrs={'class': COMMON_INPUT}),
            'min_order_amount': forms.NumberInput(attrs={'class': COMMON_INPUT}),
            'description': forms.Textarea(attrs={'class': COMMON_INPUT, 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-indigo-600 border-gray-300 rounded',
            }),
        }

    def clean_code(self):
        code = self.cleaned_data.get('code', '')
        normalized = code.replace(' ', '').upper()
        if len(normalized) < 4:
            raise forms.ValidationError('Use at least 4 characters without spaces.')
        return normalized

    def clean_value(self):
        value = self.cleaned_data.get('value') or 0
        t = self.cleaned_data.get('discount_type')
        if t == PromoCode.TYPE_PERCENTAGE and not (0 < value <= 100):
            raise forms.ValidationError('Enter a percentage greater than 0 and no more than 100.')
        if t == PromoCode.TYPE_FIXED and value <= 0:
            raise forms.ValidationError('Enter a fixed discount greater than 0.')
        return value

    def clean_usage_limit(self):
        limit = self.cleaned_data.get('usage_limit')
        if limit is not None and limit <= 0:
            raise forms.ValidationError('Enter a number greater than 0 or leave this field blank.')
        return limit

    def clean(self):
        data = super().clean()
        s, e = data.get('start_date'), data.get('end_date')
        if s and e and e <= s:
            self.add_error('end_date', 'The end date must be after the start date.')
        return data


class ApplyPromoCodeForm(forms.Form):
    promo_code = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': COMMON_INPUT,
            'placeholder': 'Enter a promo code',
        }),
        label='Promo code',
    )

    def clean_promo_code(self):
        from .models import PromoCode
        code = self.cleaned_data.get('promo_code', '')
        code = code.replace(' ', '').upper()
        try:
            promo = PromoCode.objects.get(code=code)
        except PromoCode.DoesNotExist:
            raise forms.ValidationError('Promo code not found.')
        if not promo.is_valid():
            raise forms.ValidationError('This promo code is inactive or has expired.')
        return code
