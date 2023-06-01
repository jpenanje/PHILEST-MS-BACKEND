from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from apis.serializers import *
from apis.models import *
from apis.pagination import CustomPagination
from django.db.models import Sum, F,IntegerField, CharField
from django.db.models.functions import Coalesce
from datetime import datetime, timedelta
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.decorators import api_view
from django.db.models import Q
from django.db.models import Sum
from django.db.models.functions import Cast
from django.db.models import Subquery,OuterRef
from rest_framework.settings import api_settings


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class ClassViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing classes.
    """
    queryset = Class.objects.all()
    serializer_class = ClassSerializer

    @action(detail=False, methods=['get'])
    def count(self, request):
        count = self.get_queryset().count()
        return Response({'count': count})
    
    

class StudentViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing students.
    """
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    pagination_class = CustomPagination

    @action(detail=False, methods=['get'])
    def count(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        count = queryset.count()
        return Response({'count': count})
    
    @action(detail=False, methods=['get'])
    def lists(self, request):
        classes = Class.objects.all()
        classSerializer = ClassSerializer(classes, many=True)
        academicYears = AcademicYear.objects.all()
        academicYearsSerializer = AcademicYearSerializer(academicYears, many = True)
        return Response([classSerializer.data,academicYearsSerializer.data])
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if(page is not None):
            serializer = self.get_serializer(page, many=True)

        else:
            serializer = self.get_serializer(queryset, many=True)
        
        student_data = serializer.data
        
        # Retrieve all unique class IDs from the list of students
        class_ids = list(set(student['student_class'] for student in student_data))
        student_ids = [student['id'] for student in student_data]
        
        # Fetch the class objects for the associated class IDs
        class_objects = Class.objects.filter(id__in=class_ids)
        class_serializer = ClassSerializer(class_objects, many=True)
        class_data_by_id = {str(class_obj.id): class_serializer.data[idx] for idx, class_obj in enumerate(class_objects)}

        cash_in_objects = CashIn.objects.filter(student__id__in=student_ids)
        cash_in_serializer = CashInSerializer(cash_in_objects, many=True)
        cash_in_data_by_student = {}

        for cash_in in cash_in_serializer.data:
            student_id = str(cash_in['student'])
            if student_id not in cash_in_data_by_student:
                cash_in_data_by_student[student_id] = []
            student = Student.objects.get(id = student_id)
            print( str(cash_in["academic_year"]) +" == " + str(student.current_year.year))
            if cash_in["academic_year"] == student.current_year.year:
                cash_in_data_by_student[student_id].append(cash_in)
        
        for student in student_data:
            student_class_id = str(student['student_class'])
            student_id = str(student['id'])
            current_academic_year = str(student['current_year'])
            if student_class_id in class_data_by_id:
                student['class'] = class_data_by_id[student_class_id]
            if student_id in cash_in_data_by_student:
                student['cash_ins'] = cash_in_data_by_student[student_id]
                for cash_in_data in cash_in_data_by_student[student_id]:
                    if cash_in_data["academic_year"] != current_academic_year:
                        student['cash_ins'].remove(cash_in_data)
            
        
        
        return Response(student_data)
    
    def filter_queryset(self, queryset):
        # return super().filter_queryset(queryset)
        queryset = super().filter_queryset(queryset)
        filter_id = self.request.query_params.get('id')
        if filter_id:
            id_str = str(filter_id)
            queryset = queryset.filter(id__icontains=id_str)

        filter_pupil_name = self.request.query_params.get('pupil_name')
        if filter_pupil_name:
            queryset = queryset.filter(full_name__icontains=filter_pupil_name)

        filter_class_name = self.request.query_params.get('class_name')
        if filter_class_name:
            queryset = queryset.filter(student_class__name__icontains=filter_class_name)

        filter_parent_name = self.request.query_params.get('parent_name')
        if filter_parent_name:
            queryset = queryset.filter(parent_name__icontains=filter_parent_name)

        filter_parent_phone = self.request.query_params.get('parent_phone')
        if filter_parent_phone:
            queryset = queryset.filter(parent_phone__icontains=filter_parent_phone)

        filter_registered = self.request.query_params.get('registered')
        if filter_registered:
            if(filter_registered == "yes" or filter_registered == "Yes"):
                queryset = queryset.filter(cashin__purpose__purpose="registration",current_year__year__exact = F("cashin__academic_year__year")).distinct()

            else:
                queryset = queryset.exclude(cashin__purpose__purpose="registration",current_year__year__exact = F("cashin__academic_year__year")).distinct()

        
        filter_year = self.request.query_params.get('year')

        if filter_year:
            queryset = queryset.filter(current_year__year__icontains=filter_year)


        filter_owing = self.request.query_params.get('owing')

        if(filter_owing):
            
            if filter_owing == 'yes' or filter_owing == 'Yes':

                # filter registered first
                # queryset = queryset.filter(cashin__purpose__purpose="registration",current_year__year__exact = F("cashin__academic_year__year")).distinct()

                # filter completed school fees
                queryset = queryset.filter(owing = True)

            else:
                # filter registered first
                # queryset = queryset.exclude(cashin__purpose__purpose="registration",current_year__year__exact = F("cashin__academic_year__year")).distinct()

                # filter completed school fees
                queryset = queryset.filter(owing = False)

                # queryset = queryset.annotate(
                #     cashin_total=Coalesce(Sum('cashin__amount', filter=models.Q(cashin__purpose__purpose='installment')), 0, output_field=IntegerField())
                # )
                # queryset = queryset.filter(student_class__fee=F('cashin_total'))
            
        return queryset.order_by('id')
    
    def perform_update(self, serializer):
        print("update student")
        
        student = serializer.validated_data
        student_instance = serializer.instance
        current_year_cash_ins = CashIn.objects.filter(student = student_instance.id,academic_year = student["current_year"], purpose = "installement")
        try:
            CashIn.objects.get(student = student_instance.id,academic_year = student["current_year"], purpose="registration")
            total_cash_ins = 0
            for cashIn in current_year_cash_ins:
                total_cash_ins += int(cashIn.amount)
            student_is_owing = total_cash_ins < int(student["student_class"].fee)
            student["owing"] = student_is_owing
        except:
            student["owing"] = True

        serializer.save()
    
class SubjectViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing students.
    """
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

    @action(detail=False, methods=['get'])
    def count(self, request):
        count = self.get_queryset().count()
        return Response({'count': count})
    
class TeacherViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing students.
    """
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer

    @action(detail=False, methods=['get'])
    def count(self, request):
        count = self.get_queryset().count()
        return Response({'count': count})
    
class CashInViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing cash ins.
    """
    queryset = CashIn.objects.all()
    serializer_class = CashInSerializer
    pagination_class = CustomPagination

    @action(detail=False, methods=['get'])
    def count(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        count = queryset.count()
        return Response({'count': count})
    
    @action(detail=False, methods=['get'])
    def lists(self, request):
        students = Student.objects.all()
        studentSerializer = StudentSerializer(students, many=True)

        academicYears = AcademicYear.objects.all()
        academicYearsSerializer = AcademicYearSerializer(academicYears, many = True)

        purposes = Purpose.objects.all()
        purposeSerializer = PurposeSerializer(purposes, many = True)

        return Response([studentSerializer.data, academicYearsSerializer.data, purposeSerializer.data])


    def perform_create(self, serializer):
        print("add cash in")
        serializer.save()

        cashIn = serializer.validated_data
        student = cashIn["student"]
        current_year_cash_ins = CashIn.objects.filter(student = student,academic_year = student.current_year, purpose = "installement")
        
        try:
            print(CashIn.objects.all().count)
            CashIn.objects.get(student = student.id,academic_year = student.current_year, purpose="registration")
            total_cash_ins = 0
            for cashIn in current_year_cash_ins:
                total_cash_ins += int(cashIn.amount)
            student_is_owing = total_cash_ins < int(student.student_class.fee)
            student.owing = student_is_owing
        except:
            student.owing = True

        student.save()

    def perform_update(self, serializer):
        print("update cash in")
        serializer.save()
        
        cashIn = serializer.validated_data
        student = cashIn["student"]
        current_year_cash_ins = CashIn.objects.filter(student = student,academic_year = student.current_year, purpose = "installement")

        try:
            CashIn.objects.get(student = student.id,academic_year = student.current_year, purpose="registration")
            total_cash_ins = 0
            for cashIn in current_year_cash_ins:
                total_cash_ins += int(cashIn.amount)
            student_is_owing = total_cash_ins < int(student.student_class.fee)
            student.owing = student_is_owing
        except:
            student.owing = True

        student.save()
        

    def perform_destroy(self, instance):
        print("delete cash in")
        student = instance.student
        instance.delete()

        current_year_cash_ins = CashIn.objects.filter(student = student,academic_year = student.current_year, purpose = "installement")
        
        try:
            CashIn.objects.get(student = instance.id,academic_year = student.current_year, purpose="registration")
            total_cash_ins = 0
            for cashIn in current_year_cash_ins:
                total_cash_ins += int(cashIn.amount)
            student_is_owing = total_cash_ins < int(student.student_class.fee)
            student.owing = student_is_owing

        except:
            student.owing = True
        student.save()

    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if(page is not None):
            serializer = self.get_serializer(page, many=True)

        else:
            serializer = self.get_serializer(queryset, many=True)
        
        cash_in_data = serializer.data
        
        # Retrieve all unique class IDs from the list of students
        student_ids = list(set(cash_in['student'] for cash_in in cash_in_data))
        cash_in_ids = [cash_in['id'] for cash_in in cash_in_data]
        
        # Fetch the class objects for the associated class IDs
        student_objects = Student.objects.filter(id__in=student_ids)
        student_serializer = StudentSerializer(student_objects, many=True)
        student_data_by_id = {str(student_obj.id): student_serializer.data[idx] for idx, student_obj in enumerate(student_objects)}
        
        for cash_in in cash_in_data:
            cash_in_student_id = str(cash_in['student'])
            if cash_in_student_id in student_data_by_id:
                cash_in['student_data'] = student_data_by_id[cash_in_student_id]
        
        return Response(cash_in_data)
    
    def filter_queryset(self, queryset):
        # return super().filter_queryset(queryset)
        queryset = super().filter_queryset(queryset)
        filter_id = self.request.query_params.get('id')
        if filter_id:
            id_str = str(filter_id)
            queryset = queryset.filter(id__icontains=id_str)

        filter_student_name = self.request.query_params.get('student')
        if filter_student_name:
            queryset = queryset.filter(student__full_name__icontains=filter_student_name)

        filter_purpose = self.request.query_params.get('purpose')
        if filter_purpose:
            queryset = queryset.filter(purpose__purpose__icontains=filter_purpose)

        filter_amount = self.request.query_params.get('amount')
        if filter_amount:
            queryset = queryset.filter(amount__icontains=filter_amount)

        filter_parent_phone = self.request.query_params.get('parent_phone')
        if filter_parent_phone:
            queryset = queryset.filter(parent_phone__icontains=filter_parent_phone)

        filter_registered = self.request.query_params.get('registered')
        if filter_registered:
            if(filter_registered == "yes" or filter_registered == "Yes"):
                queryset = queryset.filter(cashin__purpose__purpose="registration")

            else:
                queryset = queryset.exclude(cashin__purpose__purpose="registration")

        filter_owing = self.request.query_params.get('owing')

        if(filter_owing):
            if filter_owing == 'yes' or filter_owing == 'Yes':
                queryset = queryset.annotate(
                    cashin_total=Coalesce(Sum('cashin__amount', filter=models.Q(cashin__purpose__purpose='installment')), 0, output_field=IntegerField())
                )
                
                queryset = queryset.exclude(student_class__fee=F('cashin_total'))
            else:
                queryset = queryset.annotate(
                    cashin_total=Coalesce(Sum('cashin__amount', filter=models.Q(cashin__purpose__purpose='installment')), 0, output_field=IntegerField())
                )
                queryset = queryset.filter(student_class__fee=F('cashin_total'))

        filter_year = self.request.query_params.get('year')

        if filter_year:
            queryset = queryset.filter(academic_year__year__icontains=filter_year)


        filter_start_date = self.request.query_params.get('start_date')

        if filter_start_date:
            filter_start_date_dt = datetime.strptime(filter_start_date, '%Y-%m-%dT%H:%M:%S')
            queryset = queryset.filter(date__gt=filter_start_date_dt)

        
        filter_end_date = self.request.query_params.get('end_date')

        if filter_end_date:
            filter_end_date_dt = datetime.strptime(filter_end_date, '%Y-%m-%dT%H:%M:%S')
            filter_end_date_dt += timedelta(days=1)
            queryset = queryset.filter(date__lte=filter_end_date_dt)
            

        return queryset.order_by('id')
    
class CashOutViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing cash outs.
    """
    queryset = CashOut.objects.all()
    serializer_class = CashOutSerializer
    pagination_class = CustomPagination

    @action(detail=False, methods=['get'])
    def count(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        count = queryset.count()
        return Response({'count': count})
    
    @action(detail=False, methods=['get'])
    def lists(self, request):

        purposes = CashOutPurpose.objects.all()
        purposeSerializer = PurposeSerializer(purposes, many = True)

        return Response([purposeSerializer.data])
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if(page is not None):
            serializer = self.get_serializer(page, many=True)

        else:
            serializer = self.get_serializer(queryset, many=True)
        
        cash_out_data = serializer.data
        
        return Response(cash_out_data)
    
    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        filter_id = self.request.query_params.get('id')
        if filter_id:
            id_str = str(filter_id)
            queryset = queryset.filter(id__icontains=id_str)

        filter_receiver_name = self.request.query_params.get('name_of_receiver')
        if filter_receiver_name:
            queryset = queryset.filter(name_of_receiver__icontains=filter_receiver_name)

        filter_purpose = self.request.query_params.get('purpose')
        if filter_purpose:
            queryset = queryset.filter(purpose__purpose__icontains=filter_purpose)

        filter_amount = self.request.query_params.get('amount')
        if filter_amount:
            queryset = queryset.filter(amount__icontains=filter_amount)

        filter_start_date = self.request.query_params.get('start_date')

        if filter_start_date:
            filter_start_date_dt = datetime.strptime(filter_start_date, '%Y-%m-%dT%H:%M:%S')
            queryset = queryset.filter(date__gt=filter_start_date_dt)

        
        filter_end_date = self.request.query_params.get('end_date')

        if filter_end_date:
            filter_end_date_dt = datetime.strptime(filter_end_date, '%Y-%m-%dT%H:%M:%S')
            filter_end_date_dt += timedelta(days=1)
            queryset = queryset.filter(date__lte=filter_end_date_dt)
            

        return queryset.order_by('id')
    
class MarkViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing students.
    """
    queryset = Mark.objects.all()
    serializer_class = MarkSerializer

    @action(detail=False, methods=['get'])
    def count(self, request):
        count = self.get_queryset().count()
        return Response({'count': count})
    
class ResultViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing students.
    """
    queryset = Result.objects.all()
    serializer_class = ResultSerializer

    @action(detail=False, methods=['get'])
    def count(self, request):
        count = self.get_queryset().count()
        return Response({'count': count})
    
class CustomUserViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing students.
    """
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    @action(detail=False, methods=['get'])
    def count(self, request):
        count = self.get_queryset().count()
        return Response({'count': count})
    

class CustomAuthTokenView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        try:
            custom_user = CustomUser.objects.get(user=user.id)
        except:
            return Response({"error_message":"no custom user with that information"}, status=400)
        return Response({
            'token': token.key,
            'username': custom_user.user.username,
            'full_name':custom_user.user.first_name,
            'phone_number':custom_user.phone_number,
            'pic': custom_user.picture,
        })
    


class CustomUserUpdateView(APIView):
    def put(self, request, format=None):

        try:
            user = request.user
        except CustomUser.DoesNotExist:
            return Response(status=452)
        
        requestBody = request.data

        # Make sure there is only one user with that username
        try:
            if(user.username != requestBody["username"]):
                users_with_request_username = User.objects.filter(username = requestBody["username"])
                if users_with_request_username.count() > 0:
                    return Response(status=status.HTTP_409_CONFLICT)
        except:
            return Response(status=status.HTTP_409_CONFLICT)

        try:
            if "old_password" in requestBody: 
                if user.check_password(requestBody["old_password"]):
                    user.username = requestBody["username"]
                    user.first_name = requestBody["full_name"]
                    user.set_password(requestBody["password"])
                    user.save()
                    custom_user = CustomUser.objects.get(user=user)
                    custom_user.phone_number = requestBody["phone_number"]
                    custom_user.picture = requestBody["picture"]
                    custom_user.save()
                else:
                    return Response(status=status.HTTP_412_PRECONDITION_FAILED)
            else:
                user.username = requestBody["username"]
                user.first_name = requestBody["full_name"]
                user.save()
                custom_user = CustomUser.objects.get(user=user)
                custom_user.phone_number = requestBody["phone_number"]
                custom_user.picture = requestBody["picture"]
                custom_user.save()
        except:
            return Response(status=status.HTTP_417_EXPECTATION_FAILED)
        
        return Response(status=200)

# -----------------------------For the dashboard ----------------------------

# returns the list of academic years for the dashboard
@api_view()
def academic_years(request):
    academicYears = AcademicYear.objects.all()
    academicYearsSerializer = AcademicYearSerializer(academicYears, many = True)
    return Response(academicYearsSerializer.data)


# returns the matrics of the dashboard
@api_view()
def metrics(request):
    current_year = request.query_params.get('current_year')
    if(current_year):
        try:
            year_obj = AcademicYear.objects.get(year = current_year)

            number_of_students = Student.objects.filter(current_year = year_obj).count()
            number_of_classes = Class.objects.all().count()

            start_year, end_year = current_year.split('/')
            start_date = datetime.strptime(start_year, '%Y').date()
            end_date = datetime.strptime(end_year, '%Y').date()

            number_of_cash_ins = CashIn.objects.filter(date__range=[start_date, end_date]).count()
            number_of_cash_outs = CashOut.objects.filter(date__range=[start_date, end_date]).count()

            return Response({"num_students":number_of_students,
                             "num_classes":number_of_classes,
                             "num_cashin":number_of_cash_ins,
                             "num_cashout":number_of_cash_outs,
                             })
        except:
            return Response(status = status.HTTP_422_UNPROCESSABLE_ENTITY)
        
    else:
        return Response(status = status.HTTP_406_NOT_ACCEPTABLE)


# returns information about the graph of the dashboard
@api_view()
def graph(request):
    current_year = request.query_params.get('current_year')
    if(current_year):
        try:

            AcademicYear.objects.get(year = current_year)

            start_year, end_year = current_year.split('/')
            start_date = datetime.strptime(start_year, '%Y').date()
            end_date = datetime.strptime(end_year, '%Y').date()

            cash_ins = CashIn.objects.filter(date__range=[start_date, end_date])
            cash_outs = CashOut.objects.filter(date__range=[start_date, end_date])

            months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep","Oct", "Nov", "Dec"]
            months_indices = ["01", "02", "03", "04", "05", "06", "07", "08", "09","10", "11", "12"]

            response_body = []

            i = 0
            for month in months:
                response_body.append(get_month_graph_item(cash_ins, cash_outs, months, months_indices, month))
                i+=1

            net_income = 0
            for item in response_body:
                net_income += get_valid_value(item["cashin"]) - get_valid_value(item["cashout"])

            response_body.append({"net_income":net_income})

            return Response(
                response_body
            )
        except:
            return Response(status = status.HTTP_422_UNPROCESSABLE_ENTITY)
        
    else:
        return Response(status = status.HTTP_406_NOT_ACCEPTABLE)
    

def get_month_graph_item(cash_ins,cash_outs,months, months_indices, month):

    index = months.index(month)
    month_in_date_str = months_indices[index]

    month_cash_ins = cash_ins.filter(date__regex=r'^\d{4}'+'-'+month_in_date_str+'\\b')
    month_cash_outs = cash_outs.filter(date__regex=r'^\d{4}'+'-'+month_in_date_str+'\\b')

    total_cash_ins = month_cash_ins.aggregate(sum_amount=Sum('amount')).get('sum_amount', 0)

    total_cash_outs = month_cash_outs.aggregate(sum_amount=Sum('amount')).get('sum_amount', 0)

    return {
        "month":month,
        "cashin":total_cash_ins,
        "cashout":total_cash_outs,
    }

def get_valid_value(value):
    if value:
        return value
    return 0