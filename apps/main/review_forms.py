from django import forms
from django.core.exceptions import ValidationError
from PIL import Image
from io import BytesIO
import re


class ReviewForm(forms.Form):
    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        widget=forms.HiddenInput(attrs={'id': 'rating-input'})
    )
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'review-input',
            'placeholder': 'Summarize your experience',
            'maxlength': '200'
        })
    )
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'review-textarea',
            'placeholder': 'Share your thoughts about this product...',
            'rows': '6',
            'maxlength': '2000'
        })
    )
    images = forms.FileField(
        required=False,
        widget=forms.TextInput(attrs={
            'type': 'file',
            'multiple': True,
            'accept': 'image/jpeg,image/png,image/webp',
            'class': 'review-file-input',
            'id': 'review-images'
        })
    )
    
    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        
        if len(title) < 5:
            raise ValidationError('Title must be at least 5 characters long.')
        
        if re.search(r'(.)\1{4,}', title):
            raise ValidationError('Title contains invalid character repetition.')
        
        return title
    
    def clean_content(self):
        content = self.cleaned_data.get('content', '').strip()
        
        if len(content) < 20:
            raise ValidationError('Review must be at least 20 characters long.')
        
        if len(content.split()) < 5:
            raise ValidationError('Review must contain at least 5 words.')
        
        spam_patterns = [
            r'(https?://|www\.)',
            r'[\w\.-]+@[\w\.-]+\.\w+',
            r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4})',
        ]
        
        for pattern in spam_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                raise ValidationError('Review cannot contain URLs, emails, or phone numbers.')
        
        return content
    
    def clean_images(self):
        images = self.files.getlist('images')
        
        if len(images) > 5:
            raise ValidationError('Maximum 5 images allowed.')
        
        max_size = 5 * 1024 * 1024
        allowed_types = ['image/jpeg', 'image/png', 'image/webp']
        
        for image in images:
            if image.content_type not in allowed_types:
                raise ValidationError('Only JPEG, PNG, and WebP images are allowed.')
            
            if image.size > max_size:
                raise ValidationError('Each image must be less than 5MB.')
            
            try:
                img = Image.open(image)
                img.verify()
                
                if img.size[0] < 200 or img.size[1] < 200:
                    raise ValidationError('Images must be at least 200x200 pixels.')
                
                if img.size[0] > 4000 or img.size[1] > 4000:
                    raise ValidationError('Images must not exceed 4000x4000 pixels.')
                
            except Exception:
                raise ValidationError('Invalid or corrupted image file.')
        
        return images


class ReviewEditForm(ReviewForm):
    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)
        
        if self.instance:
            self.fields['rating'].initial = self.instance.rating
            self.fields['title'].initial = self.instance.title
            self.fields['content'].initial = self.instance.content