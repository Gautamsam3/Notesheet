# Generated by Django 3.2.2 on 2023-10-24 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0006_notesheet_reg_fee'),
    ]

    operations = [
        migrations.AddField(
            model_name='notesheet',
            name='brochure',
            field=models.ImageField(default='NA', upload_to='brochures/'),
        ),
    ]
