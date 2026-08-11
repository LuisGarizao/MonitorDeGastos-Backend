from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from datetime import timedelta
from uuid import uuid7
from tracker.models import User, Expense, ExpenseType
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from tracker.serializers import UserSerializer, UserListSerializer, ExpenseSerializer

def get_object(pk, model):
    """Retrieve a model instance by primary key.
    
    Args:
        pk: Primary key of the model.
        
    Returns:
        object: The requested model instance.
        
    Raises:
        Http404: If user with the given pk doesn't exist.
    """
    try:
        return model.objects.get(pk=pk)
    except model.DoesNotExist:
        raise Http404

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
    
    def get(self, request, pk: uuid7 | None = None):
        """Retrieve details of a specific user.
        
        Args:
            request: Request object.
            pk: Primary key of the user.
            
        Returns:
            Response: Serialized data of the requested user with status 200.
        """
        _pk = request.user.id if pk is None else pk
        user = get_object(pk=_pk, model=User)
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request, pk: uuid7 | None = None):
        """Partially update a specific user.
        
        Args:
            request: Request object containing updated user fields.
            pk: Primary key of the user.
            
        Returns:
            Response: Serialized data of updated user with status 200 if successful,
                or error details with status 400 if invalid.
        """
        pk = request.user.id if pk is None else pk
        user = get_object(pk, User)
        serializer = UserSerializer(user,data=request.data,partial=True,context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk: uuid7 | None = None):
        """Delete a specific user.
        
        Args:
            request: Request object.
            pk: Primary key of the user to delete.
            
        Returns:
            Response: Empty response with status 204.
        """
        pk = request.user.id if pk is None else pk
        user = get_object(pk, User)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ExpenseList(APIView):
    """API view for creating and listing all expenses of the user in session."""
    
    permission_classes = [IsAuthenticated]  
    
    def get(self, request):
        """Return a list of all expenses."""
        user_id = request.user.id
        expenses = Expense.objects.filter(user=user_id).order_by("-date")
        serializer = ExpenseSerializer(expenses, context={'request': request}, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """Create a new expense."""
        expense_data = request.data.copy()
        serializer = ExpenseSerializer(data=expense_data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ExpenseDetail(APIView):
    """API view for retrieving, updating or deleting a specific expense."""
    
    permission_classes = [IsAuthenticated]  
    
    def get(self, request, pk: int):
        """Retrieve details of a specific expense."""
        expense = get_object(pk, model=Expense)
        if expense.user.id != request.user.id:
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = ExpenseSerializer(expense, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    
    def patch(self, request, pk: int):
        """Edit a expense."""
        expense = get_object(pk, model=Expense)
        if expense.user.id != request.user.id:
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = ExpenseSerializer(expense, data=request.data, partial=True,context={'request': request})
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk:int):
        """Delete a specific expense"""
        expense = get_object(pk, model=Expense)
        if expense.user.id != request.user.id:
            return Response(status=status.HTTP_403_FORBIDDEN)
        expense.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ExpenseStats(APIView):
    
    def get(self, request):
        user_id = request.user.id
        filters = {"user": user_id}
        
        start_date = request.data.get("start_date")
        if start_date is not None:
            filters["date__gte"] = start_date
        
        expenses_report = {}
        expenses = Expense.objects.filter(**filters)
        
        total = sum([exp.amount for exp in list(expenses)])
        expenses_report["total_spent"] = total
        
        spent_by_type = {expense_type.value: 0 for expense_type in ExpenseType}
        for expense in expenses:
            spent_by_type[expense.type] += expense.amount

        expenses_report["spent_by_type"] = {
            expense_type: {
                "amount": amount,
                "percentage": round((amount / total) * 100, 2) if total else 0
            }
            for expense_type, amount in spent_by_type.items()
        }

        return Response(expenses_report)
