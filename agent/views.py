from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.timezone import now
from .models import RideRequest
from .serializers import RideRequestSerializer
from geopy.distance import geodesic 
from users.models import User
from rest_framework.views import APIView
from utils.firebase_config import send_push_notification

def find_nearest_rider(pickup_lat, pickup_lon):
    """Find the closest rider (hardcoded for now)"""
    riders = [
        {"id": 1, "name": "John Doe", "phone": "1234567890", "latitude": 6.525, "longitude": 3.380},
        {"id": 2, "name": "Jane Smith", "phone": "0987654321", "latitude": 6.530, "longitude": 3.390},
    ]

    # Calculate distances
    riders.sort(key=lambda rider: geodesic((pickup_lat, pickup_lon), (rider["latitude"], rider["longitude"])).km)

    return riders[0] if riders else None

class CreateRideRequestView(APIView):
    """Passenger creates a ride request"""
    def perform_create(self, serializer):
        ride = serializer.save(passenger=self.request.user)

        # Simulate finding the nearest rider
        pickup_lat, pickup_lon = 6.5244, 3.3792  # Hardcoded for now
        nearest_rider = find_nearest_rider(pickup_lat, pickup_lon)

        if nearest_rider:
            ride.rider = User.objects.get(id=nearest_rider["id"])
            ride.status = "confirmed"
            ride.save()

            # Send notification to rider
            rider_token = ride.rider.profile.fcm_token  # Assuming FCM tokens are stored in `profile`
            send_push_notification(rider_token, "New Ride Request", "A passenger is requesting a ride!")

        else:
            ride.status = "cancelled"
            ride.save()

        return Response({"message": "Ride request processed", "ride_id": ride.id}, status=status.HTTP_201_CREATED)


class RideListView(APIView):
    """Retrieve all rides for a passenger"""
    permission_classes = [IsAuthenticated]
    serializer_class = RideRequestSerializer

    def get_queryset(self):
        return RideRequest.objects.filter(passenger=self.request.user).order_by('-created_at')

class NegotiatePriceView(APIView):
    """Allows a rider to propose a new price"""
    permission_classes = [IsAuthenticated]
    serializer_class = RideRequestSerializer

    def patch(self, request, *args, **kwargs):
        ride = RideRequest.objects.get(id=kwargs["ride_id"])

        if ride.rider != request.user:
            return Response({"error": "You are not assigned to this ride"}, status=status.HTTP_403_FORBIDDEN)

        new_price = request.data.get("new_price")
        ride.price = new_price
        ride.status = "negotiation"
        ride.save()

        # TODO: Notify passenger about the new price
        return Response({"message": "New price proposed", "new_price": new_price}, status=status.HTTP_200_OK)


class ScheduleRideView(APIView):
    """Passenger schedules a ride"""
    permission_classes = [IsAuthenticated]
    serializer_class = RideRequestSerializer

    def post(self, serializer):
        ride = serializer.save(passenger=self.request.user, status="pending")
        return Response({"message": "Ride scheduled successfully", "ride_id": ride.id}, status=status.HTTP_201_CREATED)

class AcceptRideView(generics.UpdateAPIView):
    """Rider accepts a ride"""
    permission_classes = [IsAuthenticated]

    def patch(self, request, ride_id):
        ride = RideRequest.objects.filter(id=ride_id, status="pending").first()
        if not ride:
            return Response({"error": "Ride not found"}, status=status.HTTP_404_NOT_FOUND)

        ride.rider = request.user
        ride.status = "confirmed"
        ride.save()

        # Send notification to the passenger
        send_push_notification(ride.passenger, "Ride Accepted", f"Your ride to {ride.dropoff_location} has been accepted!")

        return Response({"message": "Ride accepted successfully"}, status=status.HTTP_200_OK)

class NegotiateRideView(generics.UpdateAPIView):
    """Rider negotiates the ride price"""
    permission_classes = [IsAuthenticated]

    def patch(self, request, ride_id):
        ride = RideRequest.objects.filter(id=ride_id, status="pending").first()
        if not ride:
            return Response({"error": "Ride not found"}, status=status.HTTP_404_NOT_FOUND)

        new_price = request.data.get("new_price")
        if not new_price or float(new_price) <= 0:
            return Response({"error": "Invalid price"}, status=status.HTTP_400_BAD_REQUEST)

        ride.price = float(new_price)
        ride.status = "negotiation"
        ride.save()

        # Notify passenger about price negotiation
        send_push_notification(ride.passenger, "Price Negotiation", f"Rider proposed a new price: ${ride.price}")

        return Response({"message": "Price negotiation sent to passenger"}, status=status.HTTP_200_OK)
