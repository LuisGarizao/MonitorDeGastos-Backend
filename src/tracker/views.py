from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from tracker.models import User, Expense
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from tracker.serializers import UserSerializer, UserListSerializer, ExpenseSerializer

class UsersView(APIView):
    """API view for listing all users."""
    
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        """Return a list of all users.
        
        Returns:
            Response: Serialized data of all users with status 200.
        """
        users = User.objects.all()
        serializer = UserListSerializer(users, many=True, context={'request': request})
        return Response(serializer.data)

class Register(APIView):
    """API view for creating users."""
    
    def post(self, request):
        """Create a new user.
        
        Args:
            request: Request object containing user data.
            
        Returns:
            Response: Serialized data of created user with status 201 if successful,
                or error details with status 400 if invalid.
        """
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class UserDetail(APIView):
    """API view for retrieving, updating or deleting a specific user."""
    
    permission_classes = [IsAuthenticated]  
    
    def get_object(self, pk):
        """Retrieve a user instance by primary key.
        
        Args:
            pk: Primary key of the user.
            
        Returns:
            User: The requested user instance.
            
        Raises:
            Http404: If user with the given pk doesn't exist.
        """
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404
    
    def get(self, request, pk):
        """Retrieve details of a specific user.
        
        Args:
            request: Request object.
            pk: Primary key of the user.
            
        Returns:
            Response: Serialized data of the requested user with status 200.
        """
        user = self.get_object(pk)
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data)
    
    def put(self, request, pk):
        """Update all fields of a specific user.
        
        Args:
            request: Request object containing updated user data.
            pk: Primary key of the user.
            
        Returns:
            Response: Serialized data of updated user with status 200 if successful,
                or error details with status 400 if invalid.
        """
        user = self.get_object(pk)
        serializer = UserSerializer(user, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        """Partially update a specific user.
        
        Args:
            request: Request object containing updated user fields.
            pk: Primary key of the user.
            
        Returns:
            Response: Serialized data of updated user with status 200 if successful,
                or error details with status 400 if invalid.
        """
        user = self.get_object(pk)
        serializer = UserSerializer(user,data=request.data,partial=True,context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        """Delete a specific user.
        
        Args:
            request: Request object.
            pk: Primary key of the user to delete.
            
        Returns:
            Response: Empty response with status 204.
        """
        user = self.get_object(pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ExpenseList(APIView):
    """API view for creating and listing all expenses."""
    
    def get(self, request):
        """Return a list of all expenses."""
        pass
    
    def post(self, request):
        """Create a new expense."""
        pass
    

class ExpenseDetail(APIView):
    """API view for retrieving, updating or deleting a specific expense."""
    
    def get(self, request):
        """Retrieve details of a specific expense."""
        pass
    
    def post(self, request):
        """Create a new expense."""
        pass
