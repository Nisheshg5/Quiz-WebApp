# Generated by Django 3.1.6 on 2021-02-20 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz_app', '0015_auto_20210220_2101'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='quiztakers',
            constraint=models.UniqueConstraint(fields=('quiz', 'user'), name='Unique Quiz Taker'),
        ),
    ]
