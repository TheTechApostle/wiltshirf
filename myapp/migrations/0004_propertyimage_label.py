# Generated by Django 5.1.6 on 2025-06-29 18:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_remove_property_image_propertyimage'),
    ]

    operations = [
        migrations.AddField(
            model_name='propertyimage',
            name='label',
            field=models.CharField(choices=[('front', 'Front View'), ('back', 'Back View'), ('side', 'Side View'), ('palour', 'Palour View'), ('kitchen', 'Kitchen View'), ('bedroom', 'Bedroom View')], default=1, max_length=50),
            preserve_default=False,
        ),
    ]
