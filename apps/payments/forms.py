from django import forms
from django.core.validators import RegexValidator
import re


class CheckoutForm(forms.Form):
    # Contact Information
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'checkout-input',
            'placeholder': 'your@email.com',
            'autocomplete': 'email'
        }),
        error_messages={
            'required': 'Email address is required',
            'invalid': 'Please enter a valid email address'
        }
    )

    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'checkout-input',
            'placeholder': 'John',
            'autocomplete': 'given-name'
        }),
        error_messages={
            'required': 'First name is required',
            'max_length': 'First name cannot exceed 50 characters'
        }
    )

    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'checkout-input',
            'placeholder': 'Doe',
            'autocomplete': 'family-name'
        }),
        error_messages={
            'required': 'Last name is required',
            'max_length': 'Last name cannot exceed 50 characters'
        }
    )

    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )

    phone = forms.CharField(
        validators=[phone_regex],
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'checkout-input',
            'placeholder': '+1234567890',
            'autocomplete': 'tel'
        }),
        error_messages={
            'required': 'Phone number is required'
        }
    )

    # Shipping Address
    address_line1 = forms.CharField(
        max_length=250,
        widget=forms.TextInput(attrs={
            'class': 'checkout-input',
            'placeholder': '123 Main Street',
            'autocomplete': 'address-line1'
        }),
        error_messages={
            'required': 'Street address is required',
            'max_length': 'Address cannot exceed 250 characters'
        }
    )

    address_line2 = forms.CharField(
        max_length=250,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'checkout-input',
            'placeholder': 'Apartment, suite, etc. (optional)',
            'autocomplete': 'address-line2'
        })
    )

    city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'checkout-input',
            'placeholder': 'New York',
            'autocomplete': 'address-level2'
        }),
        error_messages={
            'required': 'City is required',
            'max_length': 'City name cannot exceed 100 characters'
        }
    )

    postal_code = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'checkout-input',
            'placeholder': '10001',
            'autocomplete': 'postal-code'
        }),
        error_messages={
            'required': 'Postal code is required',
            'max_length': 'Postal code cannot exceed 20 characters'
        }
    )

    country = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'checkout-input',
            'placeholder': 'United States',
            'autocomplete': 'country-name'
        }),
        error_messages={
            'required': 'Country is required',
            'max_length': 'Country name cannot exceed 100 characters'
        }
    )

    # Optional notes
    customer_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'checkout-textarea',
            'placeholder': 'Order notes (optional)',
            'rows': 3,
            'maxlength': 500
        })
    )

    def clean_email(self):
        """Additional email validation"""
        email = self.cleaned_data.get('email', '').lower().strip()

        # Check for valid email format
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            raise forms.ValidationError('Please enter a valid email address')

        return email

    def clean_phone(self):
        """Clean and validate phone number"""
        phone = self.cleaned_data.get('phone', '').strip()
        # Remove all non-digit characters except +
        phone = re.sub(r'[^\d+]', '', phone)
        return phone

    def clean_postal_code(self):
        """Clean postal code"""
        postal_code = self.cleaned_data.get('postal_code', '').strip().upper()
        return postal_code