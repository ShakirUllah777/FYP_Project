from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Community(models.Model):
    """User-created community hubs. Users can create, discover, and join communities."""
    creator      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_communities', null=True, blank=True)
    name         = models.CharField(max_length=100, unique=True)
    slug         = models.SlugField(max_length=110, unique=True, blank=True)
    description  = models.TextField()
    logo         = models.ImageField(upload_to='community_logos/', blank=True, null=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'community_community'
        ordering = ['-created_at']
        verbose_name_plural = 'Communities'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Community.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def member_count(self):
        return self.memberships.count()


class CommunityMembership(models.Model):
    """Tracks users who joined a community."""
    community  = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='memberships')
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_memberships')
    joined_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'community_membership'
        unique_together = ('community', 'user')
        ordering = ['-joined_at']

    def __str__(self):
        return f'{self.user.username} in {self.community.name}'


class CommunityPost(models.Model):
    """Posts created inside a specific community by its members."""
    community  = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='posts')
    author     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_posts')
    title      = models.CharField(max_length=255)
    content    = models.TextField()
    image      = models.ImageField(upload_to='community_posts/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'community_post'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} by {self.author.username} in {self.community.name}'

    def likes_count(self):
        return self.likes.count()

    def is_liked_by(self, user):
        if not user or not user.is_authenticated:
            return False
        return self.likes.filter(user=user).exists()


class CommunityPostLike(models.Model):
    """Likes for posts inside a community."""
    post       = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name='likes')
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_post_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'community_post_like'
        unique_together = ('post', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} liked "{self.post.title}"'

