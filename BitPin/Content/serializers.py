from rest_framework.serializers import ModelSerializer, IntegerField, PrimaryKeyRelatedField
from Content.models import Score, Content, User


class ContentSerializer(ModelSerializer):
    class Meta:
        model = Content
        fields = ['id', 'title', 'count', 'score_average']


class ScoreSerializer(ModelSerializer):
    content_id = PrimaryKeyRelatedField(queryset=Content.objects.all())
    user_id = PrimaryKeyRelatedField(queryset=User.objects.all())
    score_value = IntegerField(min_value=0, max_value=5)

    class Meta:
        model = Score
        fields = ['content_id', 'user_id', 'score_value']
