from django.contrib import admin
from Content.models import Content, User, Score


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    pass

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass

@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    pass
