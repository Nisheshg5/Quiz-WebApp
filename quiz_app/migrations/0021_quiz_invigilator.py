# Generated by Django 3.1.6 on 2021-03-08 10:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quiz_app', '0020_auto_20210224_0132'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='invigilator',
            field=models.ForeignKey(default=23, limit_choices_to={'is_staff': True}, on_delete=django.db.models.deletion.CASCADE, to='quiz_app.account'),
            preserve_default=False,
        ),
    ]
