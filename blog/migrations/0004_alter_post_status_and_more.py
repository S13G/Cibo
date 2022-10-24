# Generated by Django 4.1.2 on 2022-10-24 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_post_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='status',
            field=models.CharField(choices=[('DRAFT', 'DRAFT'), ('PUBLISHED', 'PUBLISHED')], default='draft', max_length=10),
        ),
        migrations.AddIndex(
            model_name='comment',
            index=models.Index(fields=['created'], name='blog_commen_created_0e6ed4_idx'),
        ),
    ]
