from calendar import monthrange
import calendar
import datetime
from datetime import date
from django.contrib.auth.hashers import make_password
from django.forms import ValidationError
from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets, generics, status
from payroll_app import send_email
from payroll_app.management.commands.monthly_task import send_payroll_email
from payroll_app.models import LeaveManagement, PayrollManagement, Position, User, Employer, UserAnnualSalaryRevision, current_year, year_choices
from payroll_app.send_email import send_leave_email
from payroll_app.seralizers import EmployerLoginSerializer, LeaveManagementSerializer, PayrollCalculationSerializer, PayrollManagementSerializer, PositionSerializer, UpdateLeaveStatusSerializer, UserAnnualSalaryRevisionSerializer,UserLoginSerializer, UserSerializer, EmployerSerializer, UserSignupSerializer, EmployerSignupSerializer,LeaveApplicationSerializer, UsersalarySerializer, payrollSerializer
from django.contrib.auth.hashers import make_password,check_password
from drf_yasg.utils import swagger_auto_schema
from django.utils import timezone
from payroll_project import settings
from payroll_project.settings import EMAIL_HOST_USER



# Add imports for UserSignupSerializer and EmployerSignupSerializer

# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class EmployerViewSet(viewsets.ModelViewSet):
    queryset = Employer.objects.all()
    serializer_class = EmployerSerializer

class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer

class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer

class PayrollManagementViewSet(viewsets.ModelViewSet):
    queryset = PayrollManagement.objects.all()
    serializer_class = PayrollManagementSerializer

class LeaveManagementViewSet(viewsets.ModelViewSet):
    queryset = LeaveManagement.objects.all()
    serializer_class = LeaveManagementSerializer

class UserAnnualSalaryRevisionViewSet(viewsets.ModelViewSet):
    queryset = UserAnnualSalaryRevision.objects.all()
    serializer_class = UserAnnualSalaryRevisionSerializer




@swagger_auto_schema(methods=['post'],request_body=UserSignupSerializer)
@api_view(['POST'])
def user_signup(request):
    if request.method == 'POST':
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            # Hash the password before saving
            validated_data['password'] = make_password(validated_data.get('password'))
            user = User.objects.create(**validated_data)
            # Return serialized user data
            response_serializer = UserSignupSerializer(user)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({'payload': 'Only POST requests are allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@swagger_auto_schema(methods=['post'],request_body=EmployerSignupSerializer)
@api_view(['POST'])
def employer_signup(request):
    if request.method == 'POST':
        serializer = EmployerSignupSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            # Hash the password before saving
            validated_data['password'] = make_password(validated_data.get('password'))
            employer = Employer.objects.create(**validated_data)
            # Return serialized employer data
            response_serializer = EmployerSignupSerializer(employer)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
def user_list(request):
    if request.method == 'GET':
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

@api_view(['DELETE'])
def user_detail(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@swagger_auto_schema(methods=['post'],request_body=UserLoginSerializer)
@api_view(['POST'])
def user_login(request):
    email=request.data.get('email')
    password=request.data.get('password')
    try:
        user=User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'payload': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
    if check_password(password,user.password):
        if not user.verified:
            return Response({'payload': 'User is not verified'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'payload': 'login successfull'}, status=status.HTTP_200_OK)
    return Response({'payload': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
@swagger_auto_schema(methods=['post'],request_body=EmployerLoginSerializer)
@api_view(['POST'])
def employer_login(request):
    email=request.data.get('email')
    password=request.data.get('password')
    try:
        employer=Employer.objects.get(email=email)
    except Employer.DoesNotExist:
        return Response({'payload': 'Employer does not exist'}, status=status.HTTP_404_NOT_FOUND)
    if check_password(password,employer.password):
        if not employer.verified:
            return Response({'payload': 'Employer is not verified'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'payload': 'login successfull'}, status=status.HTTP_200_OK)
    return Response({'payload': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
@api_view(['POST'])
def position_create(request):
    if request.method == 'POST':
        serializer = PositionSerializer(data=request.data)
        if serializer.is_valid():
            position = serializer.save()
            return Response({'payload': 'Position created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def position_update(request, pk):
    if request.method == 'POST':
        position = Position.objects.filter(id=pk).first()
        if position:
            serializer = PositionSerializer(position, data=request.data)
            if serializer.is_valid():
                position = serializer.save()
                return Response({'payload': 'Position updated successfully'}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Position not found'}, status=status.HTTP_404_NOT_FOUND)

@swagger_auto_schema(methods=['get'])
@api_view(['GET'])
def unverified_users(request):
    if request.method == 'GET':
        unverified_users = User.objects.filter(verified=False)
        serializer = UserSerializer(unverified_users, many=True)
        return Response(serializer.data)
    
@swagger_auto_schema(methods=['get'])
@api_view(['GET'])
def verified_users(request):
    if request.method == 'GET':
        verified_users = User.objects.filter(verified=True)
        serializer = UserSerializer(verified_users, many=True)
        return Response(serializer.data)

@api_view(['PUT'])
def update_user_verification(request, user_id):
    if request.method == 'PUT':
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({'payload': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if user.verified:
            return Response({'payload': 'User is already verified'}, status=status.HTTP_200_OK)

        position_id = user.position_id
        position = Position.objects.filter(id=position_id).first()

        if position:
            user.verified = True
            user.save()
            updated_user = UserSerializer(user)
            return Response(updated_user.data, status=status.HTTP_200_OK)
        else:
            return Response({'payload': 'Position not found in Position model'}, status=status.HTTP_404_NOT_FOUND)
        
@swagger_auto_schema(methods=['put'], request_body=UserAnnualSalaryRevisionSerializer)
@api_view(['PUT'])
def user_annual_salary_revision(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response("User not found", status=status.HTTP_404_NOT_FOUND)

    if not user.verified:
        return Response("User is not verified", status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'PUT':
        serializer = UserAnnualSalaryRevisionSerializer(data=request.data)
        if serializer.is_valid():
            user.annual_salary = serializer._validated_data['new_salary']
            user.save()
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        



@swagger_auto_schema(methods=['post'], request_body=LeaveApplicationSerializer)
@api_view(['POST'])
def leave_apply(request):
    if request.method == 'POST':
        user = request.data.get('user')
        try:
            leaves_data = User.objects.get(pk=user)
        except User.DoesNotExist:
            return Response({'detail': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

        if not leaves_data.verified:
            return Response({'detail': 'User is not verified yet'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = LeaveManagementSerializer(data=request.data)
        if serializer.is_valid():
            entered_date = serializer.validated_data['date']
            if entered_date < datetime.date.today():
                return Response({'detail': 'Leave cannot be applied for past dates'}, status=status.HTTP_400_BAD_REQUEST)

            if leaves_data.leaves <= 0:
                return Response({'detail': 'User has no leaves left'}, status=status.HTTP_400_BAD_REQUEST)

            leave_exists = LeaveManagement.objects.filter(user=user, date=entered_date).exists()
            if leave_exists:
                return Response({'detail': 'Record already exists for this user with the same date and status'}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()  # Save the new leave application
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
@swagger_auto_schema(method='patch', request_body=UpdateLeaveStatusSerializer)
@api_view(['PATCH'])
def update_leave_status(request, user_id):
    try:
        leave_status = request.data.get('status')
        leaves_data = LeaveManagement.objects.get(pk=user_id)
    except LeaveManagement.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PATCH':
        if leave_status not in ['approved', 'rejected', 'pending']:
            return Response({'It is not a valid choice'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = LeaveManagementSerializer(leaves_data, data=request.data, partial=True)
        if serializer.is_valid():
            user = leaves_data.user
            status_value = serializer.validated_data.get('status')

            if status_value == 'approved':
                if user.leaves > 0:
                    user.leaves -= 1
                    user.save()
                    subject = "Leave Request Approved"
                    message = "Your leave request has been approved."
                    send_leave_email(user.email, subject, message)
                else:
                    return Response({"detail": "User does not have enough leaves"}, status=status.HTTP_400_BAD_REQUEST)

            elif status_value == 'rejected':
                subject = "Leave Request Rejected"
                message = "Your leave request has been rejected."
                send_leave_email(user.email, subject, message)

            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

def get_leave_management(request):
    if request.method == 'GET':
        leave_management = LeaveManagement.objects.all()
        serializer = LeaveManagementSerializer(leave_management, many=True)
        return Response(serializer.data)
    

@api_view(['GET'])
def get_pending_leaves(request):
    if request.method == 'GET':
        pending_leaves = LeaveManagement.objects.filter(status='pending')
        serializer = LeaveManagementSerializer(pending_leaves, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

@api_view(['GET'])
def get_approved_leaves(request):
    if request.method == 'GET':
        approved_leaves = LeaveManagement.objects.filter(status='approved')
        serializer = LeaveManagementSerializer(approved_leaves, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_rejected_leaves(request):
    if request.method == 'GET':
        rejected_leaves = LeaveManagement.objects.filter(status='rejected')
        serializer = LeaveManagementSerializer(rejected_leaves, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(methods=['post'], request_body=LeaveApplicationSerializer)
@api_view(['POST'])
def loss_pay(request):
    if request.method == 'POST':
        serializer = LeaveApplicationSerializer(data=request.data)
        if serializer.is_valid():
            user_id = request.data.get('user')
            date_applied = serializer.validated_data.get('date', timezone.now().date())
            user_verified = User.objects.filter(id=user_id, verified=True).first()
            user = User.objects.filter(id=user_id).first()

            if not user:
                return Response({'payload': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            
            if not user_verified:
                return Response({'payload': 'User not verified'}, status=status.HTTP_400_BAD_REQUEST)

            if user.leaves > 0:
                return Response({'payload': 'regular leaves are available for this user'}, status=status.HTTP_400_BAD_REQUEST)

            if date_applied < timezone.now().date():
                return Response({'payload': 'Cannot apply leave for past day'}, status=status.HTTP_400_BAD_REQUEST)

            existing_leave = LeaveManagement.objects.filter(user=user, date=datetime.date).first()
            if existing_leave:
                return Response({'payload': 'Leave already applied for the same date'}, status=status.HTTP_400_BAD_REQUEST)

            # Update LeaveManagement table
            leave_obj = LeaveManagement.objects.create(user=user_verified, date=datetime.date)
            leave_obj.date = datetime.date
            leave_obj.save()

            return Response({'payload': 'Leave applied successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(method='put', request_body=UsersalarySerializer)
@api_view(['PUT'])
def user_salary(request, id):
    user = get_object_or_404(User, id=id)

    if request.method == 'PUT':
        if not user.verified:
            return Response({"payload": "User not verified"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UsersalarySerializer(data=request.data)
        if serializer.is_valid():
            annual_salary = serializer.validated_data['annual_salary']
            user.annual_salary = annual_salary
            user.save()
            return Response({"payload": "User Salary Updated"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            
            
def current_year():
    return datetime.date.today().year   
def current_month():
    return datetime.date.today().month        
def get_days_in_month(year, month):
    return calendar.monthrange(year, month)[1]

@swagger_auto_schema(method='post', request_body=payrollSerializer)
@api_view(['POST'])
def payroll_calculation(request):
    if request.method == 'POST':
        serializer = payrollSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['user']
            year = serializer.validated_data['year']
            month = serializer.validated_data['month']
            user = User.objects.filter(id=user_id).first()  # Retrieve the user object

            if not user:
                return Response({"payload": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)

            current_year = datetime.now().year
            current_month = datetime.now().month

            if year > current_year or (year == current_year and month > current_month):
                return Response({"payload": "Cannot calculate for future year or month"}, status=status.HTTP_400_BAD_REQUEST)

            elif not user.verified:  # Assuming 'verified' is the correct attribute name
                return Response({"payload": "User not verified"}, status=status.HTTP_400_BAD_REQUEST)

            elif PayrollManagement.objects.filter(user=user, year=year, month=month).exists():
                return Response({"payload": "Payroll data for this month and year already exists for this user"}, status=status.HTTP_400_BAD_REQUEST)

            else:
                annual_salary = user.annual_salary
                gross_salary = round(annual_salary / 12, 2)
                provident_fund = round(gross_salary * 0.04, 2)

                if gross_salary <= 7500:
                    professional_tax = 0
                elif 7500 < gross_salary <= 10000:
                    professional_tax = 175
                else:
                    professional_tax = 200

                num_days = get_days_in_month(year, month)
                loss_of_pay = 0

                if user.leaves < 0:
                    loss_of_pay = round((gross_salary - provident_fund - professional_tax) / num_days * abs(user.leaves), 2)

                net_salary = round(gross_salary - provident_fund - professional_tax - loss_of_pay, 2)

                payroll = PayrollManagement.objects.create(
                    user=user,
                    year=year,
                    month=month,
                    gross_salary=gross_salary,
                    provident_fund=provident_fund,
                    professional_tax=professional_tax,
                    loss_of_pay=loss_of_pay,
                    net_salary=net_salary
                )

                # Include 'user_salary' when calling 'send_payroll_email'
                send_payroll_email(month, year, user, gross_salary, provident_fund, professional_tax, loss_of_pay, net_salary)
                return Response(PayrollCalculationSerializer(payroll).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def payroll_details(request,user_id):
    if request.method == 'GET':
        user_payroll = PayrollManagement.objects.filter(user=user_id)
        serializer = PayrollCalculationSerializer(user_payroll, many=True)
        return Response(serializer.data)