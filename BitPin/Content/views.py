from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.db import transaction
from django.core.cache import cache
from Content.models import Score, Content
from Content.serializers import ScoreSerializer, ContentSerializer
from rest_framework.pagination import PageNumberPagination
from django.db.models import F
from Content.models import Content
from Content.serializers import ContentSerializer
import logging


logger = logging.getLogger(__name__)


class ContentPagination(PageNumberPagination):
    page_size = 10  # for example! it depends on the contents.


class ContentView(APIView):
    @staticmethod
    def get(request):
        paginator = ContentPagination()
        page_number = request.query_params.get('page', 1)
        cache_key = f'contents_page_{page_number}'
        cached_contents = cache.get(cache_key)
        if not cached_contents:
            try:
                contents = Content.objects.all().order_by('id')
                paginated_contents = paginator.paginate_queryset(contents, request)
                serializer = ContentSerializer(paginated_contents, many=True)
                cached_contents = serializer.data
                cache.set(cache_key, cached_contents, timeout=60 * 5)

            except Exception as e:
                logger.error(f"Error fetching or serializing content: {e}")
                return Response({"error": "Internal Server Error"}, status=500)

        return paginator.get_paginated_response(cached_contents)


class ScoreView(APIView):
    @staticmethod
    @transaction.atomic
    def post(request):
        serializer = ScoreSerializer(data=request.data)
        if not serializer.is_valid():
            raise ValidationError(serializer.errors)

        data = serializer.validated_data
        content = data['content_id']
        user = data['user_id']
        score_value = data['score_value']

        # Check if the user has already scored the content
        score_cache_key = f"score_{user}_{content}"
        cached_score = cache.get(score_cache_key)

        if cached_score:
            return Response({'message': "Score fetched from cache."}, status=status.HTTP_200_OK)

        score = Score.objects.select_for_update().filter(user=user, content=content).first()
        if score:
            if score.score_value == score_value:
                return Response({'message': "Score doesn't change."}, status=status.HTTP_200_OK)

            old_avg_value = content.score_average
            content.score_average = content.fix_score_avg(score_value, old_avg_value)
            content.save()

            score.score_value = score_value
            score.save()

            # Cache the updated score
            cache.set(score_cache_key, score_value, timeout=60 * 60)

            return Response({'message': 'Score updated successfully.'}, status=status.HTTP_200_OK)
        else:
            Score.objects.create(user=user, content=content, score_value=score_value)
            content.score_average = content.calculate_score_avg(score_value)
            content.count = F('count') + 1
            content.save()

            # Cache the new score
            cache.set(score_cache_key, score_value, timeout=60 * 60)

            return Response({'message': 'Score added successfully.'}, status=status.HTTP_201_CREATED)