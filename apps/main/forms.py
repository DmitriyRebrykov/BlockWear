from django import forms


class ProductFilterForm(forms.Form):
    categories = forms.MultipleChoiceField(
        choices=[],
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        })
    )

    sizes = forms.MultipleChoiceField(
        choices=[],
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        })
    )

    price_max = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-range price-range',
            'min': 50,
            'max': 500,
            'value': 500,
            'id': 'priceRange'
        })
    )

    def __init__(self, *args, **kwargs):
        categories = kwargs.pop('categories', [])
        sizes = kwargs.pop('sizes', [])
        super().__init__(*args, **kwargs)
        self.fields['categories'].choices = [(category.id, category.name) for category in categories]
        self.fields['sizes'].choices = [(size.id, size.name) for size in sizes]
