from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import *
from django.http import JsonResponse
from django.db.models import Count, Prefetch
from .forms import *
from django.forms import modelformset_factory
from django.contrib import messages
from collections import OrderedDict


# Create your views here.
def myHome(request):
    getSlider = SliderImages.objects.all()
    getAgent = Agent.objects.all()
    getPropertyType= PropertyType.objects.distinct()
    ClientTestimonies = ClientTestimony.objects.all().distinct()
    getPropertyCount = PropertyType.objects.annotate(property_count=Count('property'))
    getPropertyLocation = Location.objects.all().distinct()

    # Get distinct propertyFeature values
    property_features = Property.objects.values_list('propertyFeature', flat=True).distinct()

    grouped_properties = OrderedDict()
    for feature in property_features:
        grouped_properties[feature] = Property.objects.filter(
            propertyFeature=feature
        ).prefetch_related(
            Prefetch('images', queryset=PropertyImage.objects.all())
        )

    context = {
        'getSliders': getSlider,
        'ClientTestimonies':ClientTestimonies,
        'getPropertyLocation':getPropertyLocation,
        'getPropertyType': getPropertyCount,
        'getPropertyType_':getPropertyType,
        'grouped_properties': grouped_properties,
        'property_features': property_features,
        'getAgent': getAgent
    }

    return render(request, 'index.html', context)


def about(request):
    return render(request, 'about.html')


def createSlider(request):
    if request.method == "POST":
        text = request.POST.get('sliderText')
        slider = request.FILES.get('sliderImage')
        if text and slider:
            SliderImages.objects.create(sliderText=text, sliderImage=slider)
            return JsonResponse({'status': 'success', 'message': 'Slider Image Uploaded Successfully'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Missing data'})
    return render(request, 'createSlider.html')

def property_list_view(request):
    if request.method == "POST":
        ClientRequest.objects.create(
            full_name=request.POST['full_name'],
            email=request.POST['email'],
            phone=request.POST['phone'],
            preferred_property_type_id=request.POST['preferred_property_type'],
            preferred_location_id=request.POST.get('preferred_location'),
            budget_min=request.POST['budget_min'],
            budget_max=request.POST['budget_max'],
            description=request.POST.get('description', '')
        )

    properties = Property.objects.all().order_by('-date_added')
    property_types = PropertyType.objects.all()
    locations = Location.objects.all()

    return render(request, "property_list.html", {
        "properties": properties,
        "property_types": property_types,
        "locations": locations
    })

def Dashboard(request):
    return render(request, 'Dashboard/index.html')



def FormProperty(request):
    ImageFormSet = modelformset_factory(PropertyImage, form=PropertyImageForm, extra=4, can_delete=False)

    if request.method == 'POST':
        form = PropertyForm(request.POST)
        formset = ImageFormSet(request.POST, request.FILES, queryset=PropertyImage.objects.none())

        if form.is_valid() and formset.is_valid():
            prop = form.save()
            for image_form in formset:
                if image_form.cleaned_data.get('image') and image_form.cleaned_data.get('label'):
                    PropertyImage.objects.create(
                        property=prop,
                        image=image_form.cleaned_data['image'],
                        label=image_form.cleaned_data['label']
                    )
            messages.success(request, "Property created successfully!")
            return redirect('FormProperty')  # Redirect back to the same form or another page
    else:
        form = PropertyForm()
        formset = ImageFormSet(queryset=PropertyImage.objects.none())

    return render(request, 'Dashboard/property.html', {
        'form': form,
        'image_forms': formset
    })

def propertyType(request):
    if request.method == 'POST':
        FormProperty = PropertyTypeForm(request.POST)

        if FormProperty.is_valid():
            FormProperty.save()
            messages.success(request, 'Property Type Inserted Successfully')
            return redirect('propertyType')
    else:
        FormProperty = PropertyTypeForm()
        getPropertyType =  PropertyType.objects.all()
    return render(request, 'Dashboard/propertyType.html', {'FormProperty': FormProperty, 'property-type':getPropertyType})


def property_list(request):
    properties = property.objects.prefetch_related('images').all()
    return render(request, 'Dashboard/property_list.html', {'propertyView':properties})


# form Property Type

def FormPropertyType(request):
    formPropertyType = PropertyTypeForm(request.POST)
    if formPropertyType.is_valid():
        type_name = formPropertyType.cleaned_data['name'].strip().lower()

        # Check if it already exists (case-insensitive)
        checkProperty = PropertyType.objects.filter(name__iexact=type_name).exists()
        if checkProperty:
            messages.warning(request, f"Property Type '{type_name}' already exists.")
        else:
            formPropertyType.save()
            messages.success(request, 'Property Type Inserted Successfully')
            return redirect('/Dashboard/propertyType')
    return render(request, 'Dashboard/propertyType.html', {'property_type_form':formPropertyType})

# form Property Type

def FormPropertyLocation(request):
    formPropertyLocation = PropertyLocationForm(request.POST)
    if formPropertyLocation.is_valid():
        formPropertyLocation.save()
        messages.success(request, 'Property Location Inserted Successfully')
        return redirect('/Dashboard/propertyLocation')
    else:

        formPropertyLocation = PropertyLocationForm()
        
    return render(request, 'Dashboard/propertyLocation.html', {'property_location_form':formPropertyLocation})



def agent_list(request):
    agents = Agent.objects.all()
    return render(request, 'agents/agent_list.html', {'agents': agents})

def add_agent(request):
    if request.method == 'POST':
        form = AgentForm(request.POST, request.FILES)
        if form.is_valid():
            type_name = form.cleaned_data['name'].strip().lower()
            AgentProperty = Agent.objects.filter(name__iexact=type_name).exists()
            if AgentProperty:
                messages.warning(request, f"Agent Info '{type_name}' already exists.")
            else:
                form.save()
                messages.success(request, 'Agent added successfully.')
                
                return redirect('/Dashboard/add_agent')
    else:
        form = AgentForm()    
                
    return render(request, 'Dashboard/agent_form.html', {'form': form})


def clientTestimony(request):
    if request.method == 'POST':
        form = ClientTestimonyForm(request.POST, request.FILES)
        if form.is_valid():
            type_name = form.cleaned_data['name'].strip().lower()
            ClientTest = ClientTestimony.objects.filter(name__iexact=type_name).exists()
            if ClientTest:
                messages.warning(request, f"Client Testimony Info '{type_name}' already exists.")
            else:
                form.save()
                messages.success(request, 'Client Testimony added successfully.')
                
                return redirect('/Dashboard/client_testimony')
    else:
        form = ClientTestimonyForm()    
                
    return render(request, 'Dashboard/client_testimony.html', {'form': form})


