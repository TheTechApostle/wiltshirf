from django  import forms
from .models import *
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ['title', 'description', 'price','property_type', 'location', 'propertyFeature', 'property_status', 'allSubscription']
        widgets = {
            'title':forms.TextInput(attrs={'class':'form-control', 'placeholder':'Enter Proper Title'}),
            'description':forms.Textarea(attrs={'class':'form-control','placeholder':'Enter Property Description'}),
            'price':forms.NumberInput(attrs={'class':'form-control', 'placeholder':'Enter Price of Property'}),
            'property_type':forms.Select(attrs={'class':'form-control'}),
            'propertyFeature':forms.Select(attrs={'class':'form-control'}),
            'property_status':forms.Select(attrs={'class':'form-control'}),
            'allSubscription':forms.Select(attrs={
                'class': 'form-control d-none',  # Hidden by default, replaced by toggle
                'id': 'subscriptionToggle'
            }),
            'location':forms.Select(attrs={'class':'form-control'}),
        }


class PropertyImageForm(forms.ModelForm):
    class Meta:
        model = PropertyImage
        fields = ['image', 'label']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'label': forms.Select(attrs={'class': 'form-select'}),
        }

class PropertyTypeForm(forms.ModelForm):
    class Meta:
        model = PropertyType
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control'})
        }


class PropertyLocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['city','state','address']
        widgets = {
            'city': forms.TextInput(attrs={'class':'form-control'}),
            'address': forms.TextInput(attrs={'class':'form-control'}),
        }

class AgentForm(forms.ModelForm):
    class Meta:
        model = Agent
        fields = ['name', 'phone', 'email', 'profile_picture']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Agent Name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class ClientTestimonyForm(forms.ModelForm):
    class Meta:
        model = ClientTestimony
        fields = ['name', 'profession', 'statement', 'profile_picture']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Client Name'}),
            'profession': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Client Profession'}),
            'statement': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Statement'}),
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))




class SubscriptionPropertyPlanForm(forms.ModelForm):
    class Meta:
        model = SubscriptionPropertyPlan
        fields = ['duration_months', 'initial_deposit_percent']
        widgets = {
            'duration_months': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'initial_deposit_percent': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 99}),
        }


class ClientRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, label="First Name", widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=True, label="Last Name", widget=forms.TextInput(attrs={'class': 'form-control'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))
    referral_code = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Referral Code (Optional)"
    )
    phone = forms.CharField(max_length=15, widget=forms.NumberInput(attrs={'class':'form-control'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control','rows':3}))

    class Meta:
        model = User
        fields = ['first_name','last_name','username', 'email', 'password']


    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")
        if password != confirm:
            raise forms.ValidationError("Passwords do not match.")
        


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Type your message...'}),
        }


# Simple profile update form
class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']



class UserWithReferralForm(UserCreationForm):
    BANK_CHOICES = [
        ('Access Bank', 'Access Bank'),
        ('GTBank', 'GTBank'),
        ('Zenith Bank', 'Zenith Bank'),
        ('UBA', 'UBA'),
        ('First Bank', 'First Bank'),
        ('FCMB', 'FCMB'),
        ('Kuda Bank', 'Kuda Bank'),
        # Add more...
    ]
    first_name = forms.CharField(max_length=30, required=True, label="First Name")
    last_name = forms.CharField(max_length=30, required=True, label="Last Name")
    email = forms.EmailField(required=True)
    CONFIRM_CHOICES = (
        ('yes', 'Yes'),
        ('no', 'No'),
    )

    confirm = forms.ChoiceField(
        label="Do you want to become a referrer?",
        choices=CONFIRM_CHOICES,
        widget=forms.RadioSelect,
        required=True
    )
    bank_name = forms.ChoiceField(
        choices=[('', 'Select your bank')] + BANK_CHOICES,
        label="Bank Name",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    account_number = forms.CharField(max_length=20)
    account_name = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ['first_name','last_name','username', 'email', 'password1', 'password2']