# Generated by Django 3.2.2 on 2023-11-01 05:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0010_review_review_order'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='review',
            name='review_order',
        ),
    ]