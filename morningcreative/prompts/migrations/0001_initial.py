# Generated by Django 4.2.10 on 2024-02-29 20:13

from django.db import migrations, models
import markdownx.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Prompt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('published', models.DateField()),
                ('title', models.CharField(max_length=140)),
                ('body', markdownx.models.MarkdownxField(blank=True, null=True)),
            ],
            options={
                'ordering': ('-published',),
                'get_latest_by': 'published',
            },
        ),
    ]
