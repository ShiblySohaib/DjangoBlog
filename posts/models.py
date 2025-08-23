from django.db import models
from django.conf import settings

class TimeStampModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# Category choices for blog posts
CATEGORY_CHOICES = [
    ("tech", "Tech"),
    ("lifestyle", "Lifestyle"),
    ("education", "Education"),
    ("news", "News"),
    ("other", "Other"),
]

class Post(TimeStampModel):
    title = models.CharField(max_length=200)
    body = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts")
    favorited_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='favorite_posts',
        blank=True
    )

    def __str__(self):
        return self.title

class Review(TimeStampModel):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.TextField()
    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])

    class Meta:
        unique_together = ('post', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.user} on {self.post} ({self.rating} stars)"
