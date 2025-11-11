from django import forms


class CartAddProductForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        max_value=99,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'p-3 border-2 border-gray-400 rounded-lg w-20 text-center font-bold',
            'placeholder': '1',
        }),
        label='Кількість',
    )
    override = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.HiddenInput()
    )
