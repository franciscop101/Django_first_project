from django.contrib import admin
from .models import Post

# Register your models here.

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at', 'published')
    list_filter = ('created_at', 'updated_at', 'published')
    search_fields = ('title', 'content')
    date_hierarchy = 'created_at'

admin.site.register(Post, PostAdmin)
