from uuid import uuid7
from config.exceptions import *
from datetime import timedelta, date

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from tracker.pagination import StandardPagination
from tracker.models import User, Expense, ExpenseType
from tracker.serializers import UserSerializer, UserListSerializer, ExpenseSerializer

############################################# 

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
        raise ExpenseNotFound()

def is_valid_date(_date: str, equal: bool = False) -> bool:
    if equal:
        if date.fromisoformat(_date) >= date.today():
            return False
    else:
        if date.fromisoformat(_date) > date.today():
            return False
    return True

def is_valid_date_range(start_date: str, end_date: str) -> bool:
    if date.fromisoformat(start_date) > date.fromisoformat(end_date):
        return False
    return True
    
############################################# 

class UsersView(APIView):
    """API view for listing all users."""
    
    permission_classes = [IsAdminUser]
    
    def get(self, request: Request):
        """Return a list of all users.
        
        Returns:
            Response: Serialized data of all users with status 200.
        """
        if request.query_params:
            params = request.query_params
            
            filters = {}
            
            active = params.get("active")
            if active:
                if not active.isdigit() or (active.isdigit() and not (active == '1' or active == '0')):
                    raise InvalidParamValue("The value of the 'active' parameter is invalid. set 1 for 'True', 0 for 'False'")
                filters["is_active"] = True if active == '1' else False
            
            staff = params.get("staff")
            if staff:
                if not staff.isdigit() or (staff.isdigit() and not (staff == '1' or staff == '0')):
                    raise InvalidParamValue("The value of the 'staff' parameter is invalid. set 1 for 'True', 0 for 'False'")
                filters["is_staff"] = True if staff == '1' else False
        
            joined_before = params.get("joined_before")
            joined_after = params.get("joined_after")
            joined_on = params.get("joined_on")
            
            if (joined_after and joined_before) and not is_valid_date_range(joined_after, joined_before):
                raise InvalidDateRange()
            if (joined_after and joined_before) and joined_on:
                raise ConflictingParams("Cannot have 'joined_on' and 'joined_before/after' in the same request")
                
            if joined_after:
                if not is_valid_date(joined_after, equal=True):
                    raise InvalidParamValue("The 'joined_after' date cannot be greater or equal than the current date")
                filters["date_joined__gt"] = joined_after
                
            if joined_before:
                filters["date_joined__lt"] = joined_before
            
            if joined_on:
                filters["date_joined"] = joined_on
        
            users = User.objects.filter(**filters)
        else:
            users = User.objects.all()
        
        paginator = StandardPagination()
        page = paginator.paginate_queryset(users, request)
        
        serializer = UserListSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

class Register(APIView):
    """API view for creating users."""
    
    def post(self, request: Request):
        """Create a new user.
        
        Args:
            request: Request object containing user data.
            
        Returns:
            Response: Serialized data of created user with status 201 if successful,
                or error details with status 400 if invalid.
        """
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class UserDetail(APIView):
    """API view for retrieving, updating or deleting a specific user."""
    
    def get(self, request: Request, pk: uuid7 | None = None):
        """Retrieve details of a specific user.
        
        Args:
            request: Request object.
            pk: Primary key of the user.
            
        Returns:
            Response: Serialized data of the requested user with status 200.
        """
        id = request.user.id if pk is None else pk
        user: User = get_object(id, User)
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class MyUserDetail(UserDetail):
    
    permission_classes = [IsAuthenticated]  
    
    def patch(self, request: Request):
        """Partially update a specific user."""
        req_body = request.data
        user: User = get_object(request.user.id, User)
        
        if not (user.is_staff or user.is_superuser):
            staff, superuser = req_body.pop("is_staff", None), req_body.pop("is_superuser", None)
            if staff or superuser:
                raise UnauthorizedAction("The user cannot give itself admin status.")

        serializer = UserSerializer(user, data=req_body, partial=True, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request: Request):
        """Delete(disable) a specific user."""
        user: User = get_object(request.user.id, User)
        serializer = UserSerializer(user, data={"is_active": False}, partial=True, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class AdminUserDetail(UserDetail):
    
    permission_classes = [IsAdminUser]
    
    def patch(self, request: Request, pk: uuid7):
        """Partially update a specific user."""
        user: User = get_object(pk, User)
        serializer = UserSerializer(user, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request: Request, pk: uuid7):
        """Delete(disable) a specific user."""
        user: User = get_object(pk, User)
        serializer = UserSerializer(user, data={"is_active": False}, partial=True, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ExpenseList(APIView):
    """API view for creating and listing all expenses of the user in session."""
    
    permission_classes = [IsAuthenticated]  
    
    def get(self, request: Request):
        """Return a list of all expenses."""
        user_id = request.user.id
        filters = {"user": user_id}
        
        if request.query_params:
            params = request.query_params
            
            start_date = params.get("from")
            end_date = params.get("to")
            days = params.get("days")
            
            if start_date and end_date:
                if not is_valid_date_range(start_date, end_date):
                    raise InvalidDateRange()
            
            if (start_date is not None) and (days is not None):
                raise ConflictingParams(detail="Cannot have number of days and start date on the same request.")
            
            if start_date:
                if not is_valid_date(start_date, equal=True):
                    raise InvalidDateRange(detail="The start date cannot be greater or equal than the current date")
                filters["date__gte"] = start_date
            
            if end_date:
                filters["date__lte"] = end_date
                
            if days:
                if not days.isdigit():
                    raise InvalidParamValue("The value provided for the parameter 'days' is not a number.")
                days = int(days)
                if days <= 0:
                    raise InvalidParamValue("The value provided of 'days' must be grater than 0.")
                start_date = date.today() - timedelta(days=days)
                filters["date__gte"] = start_date
            
        expenses = Expense.objects.filter(**filters).order_by("-date")
        paginator = StandardPagination()
        page = paginator.paginate_queryset(expenses, request)
        
        serializer = ExpenseSerializer(page, context={'request': request}, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    def post(self, request: Request):
        """Create a new expense."""
        expense_data = request.data.copy()
        serializer = ExpenseSerializer(data=expense_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

class ExpenseDetail(APIView):
    """API view for retrieving, updating or deleting a specific expense."""
    
    permission_classes = [IsAuthenticated]  
    
    def get(self, request: Request, pk: int):
        """Retrieve details of a specific expense."""
        expense = get_object(pk, model=Expense)
        if expense.user.id != request.user.id:
            raise UnauthorizedAccess()
        serializer = ExpenseSerializer(expense, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request: Request, pk: int):
        """Edit a expense."""
        expense = get_object(pk, model=Expense)
        if expense.user.id != request.user.id:
            raise UnauthorizedAccess()
        serializer = ExpenseSerializer(expense, data=request.data, partial=True,context={'request': request})
        
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request: Request, pk:int):
        """Delete a specific expense"""
        expense = get_object(pk, model=Expense)
        if expense.user.id != request.user.id:
            raise UnauthorizedAccess()
        expense.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ExpenseStats(APIView):
    
    permission_classes = [IsAuthenticated]  
    
    def get(self, request: Request):
        user_id = request.user.id
        filters = {"user": user_id}
        
        start_date = request.query_params.get("from")
        if start_date is not None:
            if date.fromisoformat(start_date) > date.today():
                raise InvalidDateRange()
            filters["date__gte"] = start_date
        
        end_date = request.query_params.get("to")
        if end_date is not None:
            if date.fromisoformat(end_date) > date.today():
                end_date = date.today().isoformat()
            filters["date__lte"] = end_date
        
        expenses_report = {}
        expenses = Expense.objects.filter(**filters)
        
        total = sum([exp.amount for exp in list(expenses)])
        expenses_report["total_spent"] = total
        
        spent_by_type = {
            expense_type.value: {
                "amount": 0,
                "num_of_expenses": 0
            } for expense_type in ExpenseType
        }
        
        for expense in expenses:
            spent_by_type[expense.type]["amount"] += expense.amount
            spent_by_type[expense.type]["num_of_expenses"] += 1
            
        expenses_report["spent_by_type"] = {
            expense_type: {
                "num_of_expenses": details["num_of_expenses"],
                "amount": details["amount"],
                "percentage": round((details["amount"] / total) * 100, 2) if total else 0
            }
            for expense_type, details in spent_by_type.items()
        }

        return Response(expenses_report, status=status.HTTP_200_OK)
