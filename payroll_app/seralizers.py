from multiprocessing import Value
from django.forms import IntegerField
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import LeaveManagement, PayrollManagement, User, Employer,Position, UserAnnualSalaryRevision
from django.contrib.auth import authenticate

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class EmployerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employer
        fields = '__all__'


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model=Position
        fields='__all__'

class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'password', 'position']

    def create(self, validated_data):
        password = validated_data.pop('password')
        hashed_password = make_password(password)  # Hash the password
        user = User.objects.create(password=hashed_password, **validated_data)
        return user



class EmployerSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Employer
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        hashed_password=make_password(password)
        employer = Employer.objects.create(password=hashed_password, **validated_data)
        return employer





class EmailPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            raise serializers.ValidationError('Email and password are required.')

        user = authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError('Invalid email or password.')

        data['user'] = user  # Attach the authenticated user to the validated data
        return data

class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()

class UsersalarySerializer(serializers.Serializer):
    annual_salary = serializers.IntegerField()
    
    class Meta:
        model = User
        fields = ['annual_salary'] 

class EmployerLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128, write_only=True)

class UpdateLeaveStatusSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=LeaveManagement.STATUS_CHOICES)

    class Meta:
        model = LeaveManagement
        fields = ['status']

class LeaveApplicationSerializer(serializers.ModelSerializer):
    date = serializers.DateField()

    class Meta:
        model = LeaveManagement
        fields = ['user','date']

class LeaveManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveManagement
        fields = '__all__'

class payrollSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField()
    
    class Meta:
        model=PayrollManagement
        fields=['user','year','month']

class PayrollManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollManagement
        fields = '__all__'


class PayrollCalculationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollManagement
        fields = '__all__'

def create(self, validated_data):
        user_instance = validated_data['user']
        payroll_instance = PayrollManagement.objects.create(user=user_instance, **validated_data)
        return payroll_instance


class UserAnnualSalaryRevisionSerializer(serializers.ModelSerializer):
    new_salary = serializers.IntegerField()

    class Meta:
        model = UserAnnualSalaryRevision
        fields = ['new_salary', 'effective_date']