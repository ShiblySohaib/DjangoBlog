from django.contrib import admin
from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
	list_display = ("title", "author", "category", "created_at", "updated_at")
	list_filter = ("category", "author", "created_at")
	search_fields = ("title", "body")
