# Generated by Django 4.2.2 on 2023-07-02 17:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0004_alter_subtopic_unique_together_alter_subtopic_name_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subtopic',
            options={'verbose_name': 'subtopic', 'verbose_name_plural': 'subtopics'},
        ),
    ]
