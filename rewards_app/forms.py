"""
Forms for Student Reward System
Contains forms for all user inputs (login, coin rewards, attendance, etc.)
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _
from .models import (
    CustomUser, StudentProfile, Transaction, Attendance, Product, Order,
    AttendanceStatus
)
from datetime import date


class CustomUserCreationForm(UserCreationForm):
    """Form for creating new users with role selection"""
    email = forms.EmailField(
        required=True,
        label=_('Email Address'),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter email')
        })
    )
    first_name = forms.CharField(
        max_length=150,
        required=True,
        label=_('First Name'),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('First name')
        })
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        label=_('Last Name'),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Last name')
        })
    )
    role = forms.ChoiceField(
        choices=CustomUser.ROLE_CHOICES,
        label=_('Role'),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})


class CustomAuthenticationForm(AuthenticationForm):
    """Custom login form with styling"""
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Username')
        })
    )
    password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Password')
        })
    )


class RewardStudentForm(forms.ModelForm):
    """Form for teachers to reward students with coins"""
    student = forms.ModelChoiceField(
        queryset=StudentProfile.objects.select_related('user'),
        label=_('Select Student'),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    coins = forms.IntegerField(
        min_value=1,
        label=_('Number of Coins'),
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter number of coins')
        })
    )
    reason = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': _('Why are you rewarding this student?')
        }),
        label=_('Reason for Reward')
    )

    class Meta:
        model = Transaction
        fields = ['coins', 'reason']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set transaction type to reward
        self.fields['coins'].label = _('Number of Coins')


class MarkAttendanceForm(forms.ModelForm):
    """Form for marking student attendance"""
    student = forms.ModelChoiceField(
        queryset=StudentProfile.objects.select_related('user'),
        label=_('Select Student'),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    status = forms.ChoiceField(
        choices=AttendanceStatus.choices,
        label=_('Attendance Status'),
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    date = forms.DateField(
        label=_('Date'),
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        initial=date.today()
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': _('Add any notes (optional)')
        }),
        label=_('Notes')
    )

    class Meta:
        model = Attendance
        fields = ['status', 'date', 'notes']


class AddProductForm(forms.ModelForm):
    """Form for teachers to add products to the store"""
    name = forms.CharField(
        max_length=255,
        label=_('Product Name'),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter product name')
        })
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': _('Product description (optional)')
        }),
        label=_('Description')
    )
    price = forms.IntegerField(
        min_value=1,
        label=_('Price (in coins)'),
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter price in coins')
        })
    )
    image = forms.ImageField(
        required=False,
        label=_('Product Image'),
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    quantity_available = forms.IntegerField(
        initial=-1,
        label=_('Quantity Available (-1 for unlimited)'),
        widget=forms.NumberInput(attrs={
            'class': 'form-control'
        })
    )
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        label=_('Active'),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'image', 'quantity_available', 'is_active']


class PurchaseProductForm(forms.ModelForm):
    """Form for students to purchase products"""
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(is_active=True),
        label=_('Select Product'),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        label=_('Quantity'),
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Order
        fields = ['quantity']

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity and quantity < 1:
            raise forms.ValidationError(_('Quantity must be at least 1'))
        return quantity
