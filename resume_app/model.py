from django.db import models

class Resume(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    address = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Project(models.Model):
    resume = models.ForeignKey(Resume, related_name='projects', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    position = models.CharField(max_length=50)
    duration = models.CharField(max_length=100)  # ex: "2023.01 ~ 2023.06"
    description = models.TextField()

    def __str__(self):
        return self.title
    
class Job(models.Model):
    resume = models.ForeignKey(Resume, related_name='jobs', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    position = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.company_name
    
class Research(models.Model):
    resume = models.ForeignKey(Resume, related_name='researches', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    duration = models.CharField(max_length=100)  # ex: "2023.01 ~ 2023.06"
    description = models.TextField()

    def __str__(self):
        return self.title

class Education(models.Model):
    resume = models.ForeignKey(Resume, related_name='educations', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    degree = models.CharField(max_length=100)
    duration = models.CharField(max_length=15, null=True)
    major = models.CharField(max_length=50, null = True)
    gpa = models.CharField(max_length=5, null=True)
    coursework = models.CharField(max_length=300, null=True)

    def __str__(self):
        return self.school_name