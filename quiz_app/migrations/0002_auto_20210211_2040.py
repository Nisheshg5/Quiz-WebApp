# Generated by Django 3.1.6 on 2021-02-11 15:10

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('quiz_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Question_bank',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.TextField()),
                ('choice_1', models.TextField()),
                ('choice_2', models.TextField()),
                ('choice_3', models.TextField(blank=True, null=True)),
                ('choice_4', models.TextField(blank=True, null=True)),
                ('choice_5', models.TextField(blank=True, null=True)),
                ('correct', models.TextField()),
                ('isShuffle', models.BooleanField(default=True)),
                ('tag', models.CharField(choices=[('C', 'C'), ('C++', 'C++'), ('java', 'Java'), ('python', 'Python'), ('os', 'OS'), ('csa', 'CSA'), ('ds', 'DS')], max_length=10)),
                ('level', models.CharField(choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')], default='beginner', max_length=15)),
            ],
            options={
                'db_table': 'question_bank',
            },
        ),
        migrations.AlterModelOptions(
            name='quiz',
            options={'ordering': ['created'], 'verbose_name_plural': 'Quizzes'},
        ),
        migrations.AddField(
            model_name='quiz',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
