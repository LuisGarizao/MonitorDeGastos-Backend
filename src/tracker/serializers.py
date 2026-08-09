from tracker.models import User, Expense
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    
    password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name","password", "email", "date_joined", "is_active", "is_staff", "is_superuser"]
        read_only_fields = ["id", "date_joined"]
    
    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance

class UserListSerializer(serializers.ModelSerializer):
        
    class Meta:
        model = User
        fields = ["id", "username", "email", "date_joined", "is_active"]
        read_only_fields = fields

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ["id", "type", "amount", "date", "plan"]
        read_only_fields = ["id", "amount", "date", "plan"]
