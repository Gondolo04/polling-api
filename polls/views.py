from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Poll, Vote
from .serializers import PollSerializer, PollCreateSerializer, VoteSerializer
from .permissions import IsOwnerOrPrivilegedOrReadOnly


class PollViewSet(viewsets.ModelViewSet):
    queryset = Poll.objects.all().order_by("-created_at")
    permission_classes = [IsOwnerOrPrivilegedOrReadOnly]

    def get_serializer_class(self):
        if self.action == "create":
            return PollCreateSerializer
        return PollSerializer

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def vote(self, request, pk=None):
        poll = self.get_object()
        serializer = VoteSerializer(data=request.data, context={"poll": poll})
        serializer.is_valid(raise_exception=True)
        choice_id = serializer.validated_data["choice_id"]

        if Vote.objects.filter(poll=poll, user=request.user).exists():
            return Response({"detail": "You already voted on this poll."}, status=status.HTTP_400_BAD_REQUEST)

        Vote.objects.create(poll=poll, choice_id=choice_id, user=request.user)
        return Response({"detail": "Vote recorded."}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], permission_classes=[permissions.AllowAny])
    def results(self, request, pk=None):
        poll = self.get_object()
        data = [{"choice": c.text, "votes": c.votes.count()} for c in poll.choices.all()]
        return Response({"poll": poll.title, "results": data})

    @action(detail=True, methods=["patch"], permission_classes=[IsOwnerOrPrivilegedOrReadOnly])
    def close(self, request, pk=None):
        poll = self.get_object()
        poll.is_open = False
        poll.save()
        return Response({"detail": "Poll closed."})