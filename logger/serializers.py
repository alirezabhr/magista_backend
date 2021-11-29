from rest_framework import serializers

from logger.models import Issue


class IssueSerializer(serializers.ModelSerializer):
    time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Issue
        fields = '__all__'



