# Generated by Django 5.1 on 2024-09-02 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fact_app', '0002_article_total'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='sex',
            field=models.CharField(choices=[('M', 'Male'), ('F', 'Female')], max_length=1),
        ),
    ]
