# Generated by Django 5.1.6 on 2025-03-16 10:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0002_alter_projectidentifier_options_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="projectroleassignment",
            options={
                "ordering": ["user_id"],
                "verbose_name": "Project role assignment",
                "verbose_name_plural": "Project role assignments",
            },
        ),
    ]
