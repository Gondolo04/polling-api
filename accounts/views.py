from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import User
from .serializers import RegisterSerializer, UserListSerializer
from .permissions import IsAdminRole


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class BanUserView(APIView):
    permission_classes = [IsAdminRole]

    def patch(self, request, pk):
        target = get_object_or_404(User, pk=pk)

        if target.role == "admin":
            return Response({"detail": "Cannot ban another admin."}, status=400)

        target.is_active = False
        target.save()
        return Response({"detail": f"{target.username} has been banned."})


class UnbanUserView(APIView):
    permission_classes = [IsAdminRole]

    def patch(self, request, pk):
        target = get_object_or_404(User, pk=pk)
        target.is_active = True
        target.save()
        return Response({"detail": f"{target.username} has been unbanned."})
    
class UserListView(generics.ListAPIView):
    serializer_class = UserListSerializer
    permission_classes = [IsAdminRole]
    queryset = User.objects.all().order_by("id")