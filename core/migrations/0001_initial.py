# Generated by Django 5.1.3 on 2024-11-21 10:23

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CryptoCurrency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('symbol', models.CharField(max_length=20)),
                ('price', models.DecimalField(decimal_places=18, max_digits=30)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Cryptocurrencies',
            },
        ),
    ]
