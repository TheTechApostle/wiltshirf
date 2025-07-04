from django  import forms
from .models import *


class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ['title', 'description', 'price','property_type', 'location', 'propertyFeature']
        widgets = {
            'title':forms.TextInput(attrs={'class':'form-control', 'placeholder':'Enter Proper Title'}),
            'description':forms.Textarea(attrs={'class':'form-control','placeholder':'Enter Property Description'}),
            'price':forms.NumberInput(attrs={'class':'form-control', 'placeholder':'Enter Price of Property'}),
            'property_type':forms.Select(attrs={'class':'form-control'}),
            'propertyFeature':forms.Select(attrs={'class':'form-control'}),
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