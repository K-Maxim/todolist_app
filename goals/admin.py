from django.contrib import admin

from goals.models import GoalCategory


@admin.register(GoalCategory)
class GoalCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "user", "created", "updated")
    list_display_links = ("title", )
    search_fields = ("title", )
    list_filter = ("is_deleted", )
    readonly_fields = ("created", "updated", )



