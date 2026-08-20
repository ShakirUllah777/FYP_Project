from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0001_initial'),
    ]

    operations = [
        # ── Post new fields ────────────────────────────────────────────────
        migrations.AddField(
            model_name='post',
            name='status',
            field=models.CharField(
                max_length=20, default='open',
                choices=[
                    ('open', 'Open'),
                    ('in_progress', 'In Progress'),
                    ('completed', 'Completed'),
                    ('closed', 'Closed'),
                ]
            ),
        ),
        migrations.AddField(
            model_name='post',
            name='views_count',
            field=models.PositiveIntegerField(default=0),
        ),

        # ── Milestone ──────────────────────────────────────────────────────
        migrations.CreateModel(
            name='Milestone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('due_date', models.DateField()),
                ('status', models.CharField(max_length=20, default='pending', choices=[
                    ('pending', 'Pending'),
                    ('in_progress', 'In Progress'),
                    ('completed', 'Completed'),
                ])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='milestones', to='posts.post')),
            ],
            options={'ordering': ['due_date']},
        ),

        # ── ProjectFile ────────────────────────────────────────────────────
        migrations.CreateModel(
            name='ProjectFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='project_files/')),
                ('description', models.CharField(max_length=200, blank=True)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_files', to='posts.post')),
                ('uploader', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
        ),
    ]
