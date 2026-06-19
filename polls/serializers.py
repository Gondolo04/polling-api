from rest_framework import serializers
from .models import Poll, Choice, Vote

class ChoiceSerializer(serializers.ModelSerializer):
    vote_count = serializers.SerializerMethodField()

    class Meta:
        model = Choice
        fields = ["id", "text", "vote_count"]

    def get_vote_count(self, obj):
        return obj.votes.count()


class PollSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)
    created_by = serializers.ReadOnlyField(source="created_by.username")

    class Meta:
        model = Poll
        fields = ["id", "title", "description", "created_by", "created_at", "is_open", "choices"]


class PollCreateSerializer(serializers.ModelSerializer):
    choices = serializers.ListField(child=serializers.CharField(max_length=200), write_only=True)

    class Meta:
        model = Poll
        fields = ["title", "description", "choices"]

    def validate_choices(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("A poll needs at least 2 choices.")
        return value

    def create(self, validated_data):
        choices_data = validated_data.pop("choices")
        poll = Poll.objects.create(created_by=self.context["request"].user, **validated_data)
        Choice.objects.bulk_create([Choice(poll=poll, text=c) for c in choices_data])
        return poll


class VoteSerializer(serializers.Serializer):
    choice_id = serializers.IntegerField()

    def validate_choice_id(self, value):
        poll = self.context["poll"]
        if not poll.is_open:
            raise serializers.ValidationError("This poll is closed.")
        if not poll.choices.filter(id=value).exists():
            raise serializers.ValidationError("Invalid choice for this poll.")
        return value