# Generated by Django 5.1.3 on 2024-11-26 06:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cryptocurrency',
            name='daily_high',
            field=models.DecimalField(decimal_places=18, default=0, max_digits=30),
        ),
        migrations.AddField(
            model_name='cryptocurrency',
            name='daily_low',
            field=models.DecimalField(decimal_places=18, default=0, max_digits=30),
        ),
    ]
