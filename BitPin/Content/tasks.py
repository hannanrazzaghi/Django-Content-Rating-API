from django.utils.timezone import now, timedelta
from django.db.models import Avg, Count
from Content.models import Score
from celery import shared_task
import numpy as np


@shared_task
def detect_fraud():
    one_hour_ago = now() - timedelta(hours=1)

    recent_stats = Score.objects.filter(created_at__gte=one_hour_ago).aggregate(
        recent_avg=Avg('score_value'),
        recent_count=Count('id')
    )
    recent_avg = recent_stats['recent_avg'] or 0
    recent_count = recent_stats['recent_count']

    overall_stats = Score.objects.aggregate(
        overall_avg=Avg('score_value'),
        overall_count=Count('id')
    )
    overall_avg = overall_stats['overall_avg'] or 0
    overall_count = overall_stats['overall_count']
    overall_std = np.std(Score.objects.all().values_list('score_value', flat=True))

    avg_threshold = 2 * overall_std
    count_threshold = 10000

    if (
            abs(recent_avg - overall_avg) > avg_threshold and
            recent_count > count_threshold
    ):
        print("Fraud detected!")

        fraud_scores = Score.objects.filter(created_at__gte=one_hour_ago).exclude(
            score_value__lte=overall_avg + avg_threshold)

        if fraud_scores.exists():
            fraud_avg = fraud_scores.aggregate(Avg('score_value'))['score_value__avg']
            new_avg = (overall_avg * overall_count - fraud_avg * fraud_scores.count()) / (
                    overall_count - fraud_scores.count())
            print(f"Adjusted overall average: {new_avg}")

    else:
        print("No fraud detected.")
