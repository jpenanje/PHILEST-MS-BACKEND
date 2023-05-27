from django.contrib.auth.models import User, Group
from rest_framework import serializers
from apis.models import *


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'password']

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']

class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = '__all__'

class StudentSerializer(serializers.ModelSerializer):
    student_class = serializers.PrimaryKeyRelatedField(queryset=Class.objects.all())
    class Meta:
        model = Student
        fields = '__all__'

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = '__all__'

class CashInSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashIn
        fields = '__all__'

class CashOutSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashOut
        fields = '__all__'

class MarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mark
        fields = '__all__'

class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = '__all__'

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'

class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = '__all__'

class PurposeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purpose
        fields = '__all__'