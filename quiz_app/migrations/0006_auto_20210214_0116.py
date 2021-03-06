# Generated by Django 3.1.6 on 2021-02-13 19:46

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('quiz_app', '0005_auto_20210213_1816'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='question',
            options={'ordering': ['marks', 'created_at'], 'verbose_name_plural': 'questions'},
        ),
        migrations.AlterModelOptions(
            name='question_bank',
            options={'ordering': ['created_at', 'tag', 'level'], 'verbose_name_plural': 'question_bank'},
        ),
        migrations.AlterModelOptions(
            name='quiz',
            options={'ordering': ['created_at'], 'verbose_name_plural': 'Quizzes'},
        ),
        migrations.RenameField(
            model_name='question',
            old_name='question',
            new_name='title',
        ),
        migrations.RenameField(
            model_name='question_bank',
            old_name='question',
            new_name='title',
        ),
        migrations.RenameField(
            model_name='quiz',
            old_name='created',
            new_name='created_at',
        ),
        migrations.AddField(
            model_name='question',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='question_bank',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
