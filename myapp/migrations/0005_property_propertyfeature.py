# Generated by Django 5.1.6 on 2025-07-02 12:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_propertyimage_label'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='propertyFeature',
            field=models.CharField(choices=[('For Sell', 'For Sell'), ('For Rent', 'For Rent'), ('Sub-Let', 'Sub-Let')], default=1, max_length=50, verbose_name='feture Choice'),
            preserve_default=False,
        ),
    ]
