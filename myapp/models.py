from django.db import models

# Create your models here.
class SliderImages(models.Model):
    sliderText = models.TextField("Slider Text", max_length=200)
    sliderImage = models.FileField(upload_to="slider_images/")


    def __str__(self):
        return self.sliderText[:50]

# Property type model
class PropertyType(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


# Location model
class Location(models.Model):
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=100)
    address = models.TextField()

    def __str__(self):
        return f"{self.address}, {self.city}, {self.state}"


# Property model
class Property(models.Model):
    featureChoice = [
        ('For Sell', 'For Sell'),
        ('For Rent', 'For Rent'),
        ('Sub-Let', 'Sub-Let')
    ]
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    property_type = models.ForeignKey(PropertyType, on_delete=models.SET_NULL, null=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    propertyFeature = models.CharField("feature Choice", choices=featureChoice, max_length=50)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.property_type.name}"
    
class PropertyImage(models.Model):
    VIEW_CHOICES = [
        ('front', 'Front View'),
        ('back', 'Back View'),
        ('side', 'Side View'),
        ('palour', 'Palour View'),
        ('kitchen', 'Kitchen View'),
        ('bedroom', 'Bedroom View'),
        # add more as needed
    ]
    
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='property_images/')
    label = models.CharField(max_length=50, choices=VIEW_CHOICES)

    def __str__(self):
        return f"{self.label.title()} - {self.property.title}"


# What the client wants (Client Request)
class ClientRequest(models.Model):
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    preferred_property_type = models.ForeignKey(PropertyType, on_delete=models.SET_NULL, null=True)
    preferred_location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    budget_min = models.DecimalField(max_digits=12, decimal_places=2)
    budget_max = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(help_text="What kind of property do you want?", null=True, blank=True)
    submitted_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.preferred_property_type.name}"

# models.py



class Agent(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(upload_to='agent_profiles/', null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class ClientTestimony(models.Model):
    name = models.CharField(max_length=100)
    profession = models.CharField(max_length=100)
    statement = models.CharField(max_length=200)
    profile_picture = models.ImageField(upload_to='client_profiles/', null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


