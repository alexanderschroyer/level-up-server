"""View module for handling requests about games"""
from django.core.exceptions import ValidationError
from rest_framework import status
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from levelupapi.models import Event, EventGamer, Gamer, Game
from django.contrib.auth.models import User

class EventView(ViewSet):
    """Level up events"""

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized game instance"""
        gamer = Gamer.objects.get(user=request.auth.user)

        try:
            event = Event.objects.create(
                game= Game.objects.get(pk=request.data["gameId"]),
                description=request.data["description"],
                date=request.data["date"],
                time=request.data["time"],
                organizer=Gamer.objects.get(user=request.auth.user)
            )
            serializer = EventSerializer(event, context={'request': request})
            return Response(serializer.data)

        except ValidationError as ex:
            return Response({"reason": ex.message}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single game

        Returns:
            Response -- JSON serialized game instance
        """
        try:
            event = Event.objects.get(pk=pk)
            serializer = EventSerializer(event, context={'request': request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def update(self, request, pk=None):
        """Handle PUT requests for a game

        Returns:
            Response -- Empty body with 204 status code
        """
        gamer = Gamer.objects.get(user=request.auth.user)

        event = Event.objects.get(pk=pk)
        event.game = Game.objects.get(pk=request.data["gameId"])
        event.description = request.data["description"]
        event.date=request.data["date"]
        event.time=request.data["time"]
        event.organizer=Gamer.objects.get(user=request.auth.user)

        event.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single game

        Returns:
            Response -- 200, 404, or 500 status code
        """
        try:
            event = Event.objects.get(pk=pk)
            event.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except Event.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request):
        """Handle GET requests to games resource

        Returns:
            Response -- JSON serialized list of games
        """
        events = Event.objects.all()

        serializer = EventSerializer(
            events, many=True, context={'request': request})
        return Response(serializer.data)

class EventUserSerializer(serializers.ModelSerializer):
    """JSON serializer for games

    Arguments:
        serializer type
    """
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username')

class GamerSerializer(serializers.ModelSerializer):
    """JSON serializer for games

    Arguments:
        serializer type
    """
    user = EventUserSerializer(many=False)
    class Meta:
        model = Gamer
        fields = ('id', 'user', 'bio')

class EventGameSerializer(serializers.ModelSerializer):
    """JSON serializer for games

    Arguments:
        serializer type
    """
    class Meta:
        model = Game
        fields = ('id', 'title', 'maker', 'number_of_players', 'skill_level')

class EventSerializer(serializers.ModelSerializer):
    """JSON serializer for games

    Arguments:
        serializer type
    """
    organizer = GamerSerializer()
    game = EventGameSerializer()

    class Meta:
        model = Event
        fields = ('id', 'game', 'description', 'date', 'time', 'organizer')
        
