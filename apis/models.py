from django.db import models
from django.contrib.auth.models import User


class AcademicYear(models.Model):
    year = models.CharField(primary_key=True, max_length=256)

class Purpose(models.Model):
    purpose = models.CharField(primary_key=True, max_length=256)

class CashOutPurpose(models.Model):
    purpose = models.CharField(primary_key=True, max_length=256)

class Class(models.Model):
    name = models.CharField(max_length=100)
    fee = models.CharField(max_length=256)

class Student(models.Model):
    full_name = models.TextField(max_length=1000, unique=True)
    student_class = models.ForeignKey(Class, on_delete=models.CASCADE)
    parent_name = models.TextField(max_length=1000)
    parent_phone = models.CharField(max_length=256)
    current_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    owing = models.BooleanField(default=True)


class Subject(models.Model):
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    subject_class = models.ForeignKey(Class, on_delete=models.CASCADE)
    coef = models.CharField(max_length=10)

class Teacher(models.Model):
    full_name = models.TextField(max_length=1000)
    subjects = models.ManyToManyField(Subject)

class CashIn(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    purpose = models.ForeignKey(Purpose, on_delete=models.CASCADE)
    date = models.CharField(max_length=256)
    amount = models.CharField(max_length=256)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)

class CashOut(models.Model):
    name_of_receiver = models.TextField(max_length=1000)
    amount = models.CharField(max_length=256)
    purpose = models.ForeignKey(CashOutPurpose, on_delete=models.CASCADE)
    date = models.CharField(max_length=256)

class Mark(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    year = models.CharField(max_length=256)
    sequence = models.CharField(max_length=256)
    term = models.CharField(max_length=256)
    mark = models.CharField(max_length=256)

class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    year = models.CharField(max_length=256)
    sequence = models.CharField(max_length=256)
    term = models.CharField(max_length=256)
    average = models.CharField(max_length=256)

class CustomUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length = 256)
    picture = models.TextField()