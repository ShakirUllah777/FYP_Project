from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_initial'),
        ('posts', '0001_initial'),
    ]

    operations = [
        # ── Profile new fields ──────────────────────────────────────────────
        migrations.AddField(
            model_name='profile',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='is_supervisor',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='batch',
            field=models.CharField(max_length=4, blank=True, null=True),
        ),

        # ── Review ─────────────────────────────────────────────────────────
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])),
                ('comment', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('reviewer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews_given', to='auth.user')),
                ('reviewed_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews_received', to='auth.user')),
                ('post', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='posts.post')),
            ],
            options={'ordering': ['-created_at']},
        ),

        # ── Report ─────────────────────────────────────────────────────────
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(max_length=20, choices=[
                    ('spam', 'Spam or irrelevant content'),
                    ('fake', 'Fake profile or impersonation'),
                    ('harassment', 'Harassment or abusive behaviour'),
                    ('scam', 'Scam or fraudulent activity'),
                    ('other', 'Other'),
                ])),
                ('details', models.TextField(blank=True)),
                ('status', models.CharField(max_length=20, default='pending', choices=[
                    ('pending', 'Pending Review'),
                    ('reviewed', 'Reviewed'),
                    ('dismissed', 'Dismissed'),
                    ('actioned', 'Action Taken'),
                ])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('reporter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports_filed', to='auth.user')),
                ('reported_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports_received', to='auth.user')),
                ('post', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='posts.post')),
            ],
            options={'ordering': ['-created_at']},
        ),

        # ── EmailOTP ───────────────────────────────────────────────────────
        migrations.CreateModel(
            name='EmailOTP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('otp', models.CharField(max_length=6)),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='email_otp', to='auth.user')),
            ],
        ),

        # ── SupervisorEndorsement ──────────────────────────────────────────
        migrations.CreateModel(
            name='SupervisorEndorsement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('supervisor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='endorsements_given', to='auth.user')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='endorsements_received', to='auth.user')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='endorsements', to='posts.post')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='supervisorendorsement',
            unique_together={('supervisor', 'post')},
        ),
    ]
