from django.db import migrations

def set_root_for_existing_comments(apps, schema_editor):
    Comment = apps.get_model('blog_app', 'Comment')
    for comment in Comment.objects.filter(root__isnull=True):
        comment.root = comment
        comment.save()

class Migration(migrations.Migration):

    dependencies = [
        ('blog_app', '0004_comment_root'),
    ]

    operations = [
        migrations.RunPython(set_root_for_existing_comments),
    ]
