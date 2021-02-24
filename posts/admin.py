from django.contrib import admin

from .models import Comment, Follow, Group, Post


class PostAdmin(admin.ModelAdmin):
    list_display = ("pk", "text", "pub_date", "author")
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"
    search_fields = ("text", "author")


class GroupAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "slug", "description")
    list_filter = ("title", "slug")
    empty_value_display = "-пусто-"
    search_fields = ("title", "slug", "description")
    prepopulated_fields = {"slug": ("title",)}


class CommentAdmin(admin.ModelAdmin):
    list_display = ("pk", "text", "post", "author", "created")
    list_filter = ("post", "author")
    empty_value_display = "-пусто-"
    search_fields = ("text",)


class FollowAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "author")
    list_filter = ("user", "author")
    empty_value_display = "-пусто-"
    search_fields = ("user", "author")


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
