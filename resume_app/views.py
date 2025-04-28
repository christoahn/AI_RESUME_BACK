from django.http import JsonResponse
from django.views import View
from .service import resume_chunk
from .model import Resume, Project, Job, Research, Education 
from dotenv import load_dotenv
import os

load_dotenv()
CHATGPT_API = os.getenv('CHATGPT_API')
CLAUDE_API = os.getenv('CLAUDE_API')
GEMINI_API = os.getenv('GEMINI_API')
DEEPSEEK_API = os.getenv('DEEPSEEK_API')

class second_page(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def post(self, request):
        action = request.POST.get('action')

        if action == 'generate_resume':
            return self.generate_resume(request.body)
        else:
            return JsonResponse({"error": "Unknown action"}, status=400)

    # def add_chunk(self, request):
    #     """
    #     get and store information from each chunk
    #     """
    #     user_input = request.POST.get('input')
    #     section = request.POST.get('section')

    #     chunk_infos = request.session.get('chunk_infos', [])
    #     chunk_infos.append({})
    #     request.session['chunk_infos'] = chunk_infos
    #     request.session.modified = True


    #     return JsonResponse({"message": "Chunk added successfully.", "chunk": result})
    
    def generate_resume(self, request_body):
        """
        Request body example
        {'name':'Char',
        'phone':'1234567890',
        'email':'asdfasdf@gmail.com',
        'jobs':{
                'job1':{
                            'company_name':'peakup',
                            'duration': '2025.01 ~ 2025.02',
                            'position':'Junier SW engineer',
                            'keywords':'AI resume generator, Django, python, finetuning'}
                'job2':{
                            'company_name': ....
                            'duration': ....
                            'position': ....
                            'keywords': ....}}},
        'projects':{
                'project1':{
                            'project_name': ...
                            'duration': ...
                            'role': ...
                            'keywords': ...}}
        """
        #찬균형과 변수명 맞추기
        name = request_body['name']
        phone = request_body['phone']
        email = request_body['email']
        address = request_body['address']
        jobs = request_body['jobs']
        projects = request_body['projects']
        researches = request_body['researchs']
        educations = request_body['education']

        resume = Resume.objects.create(
            name = name,
            phone = phone,
            email = email,
            address = address
        )

        chunks = {
            'projects': resume_chunk(CHATGPT_API, CLAUDE_API, GEMINI_API, DEEPSEEK_API, 'projects'),
            'jobs': resume_chunk(CHATGPT_API, CLAUDE_API, GEMINI_API, DEEPSEEK_API, 'jobs'),
            'researchs': resume_chunk(CHATGPT_API, CLAUDE_API, GEMINI_API, DEEPSEEK_API, 'researchs')
        }


        for project in projects.get('projects', []):
            chunk = chunks['projects']
            desc = chunk.generate_resume(project['keywords'])
            assert isinstance(desc, dict)

            Project.objects.create(
                resume=resume,
                title=project['title'],
                project_duration=project['duration'],
                description=desc['description']
            )

        for job in jobs.get('jobs', []):
            chunk = chunks['jobs']
            desc = chunk.generate_resume(job['keywords'])
            assert isinstance(desc, dict)

            Job.objects.create(
                resume=resume,
                company_name=job['company_name'],
                position=job['position'],
                work_duration=job['work_duration'],
                description=desc['description']
            )

        for research in researches.get('researches', []):
            chunk = chunks['researches']
            desc = chunk.generate_resume(research['keywords'])
            assert isinstance(desc, dict)

            Research.objects.create(
                resume=resume,
                title=research['title'],
                project_duration=research['duration'],
                description=desc['description']
            )

        for edu in educations.get('educations', []):
            Education.objects.create(
                resume=resume,
                school_name=edu['school_name'],
                degree=edu['degree'],
                graduation_year=edu['graduation_year']
            )

        return JsonResponse({'message': 'Resume successfully saved!', 'resume_id': resume.id})
    

class third_page(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get(self, request, resume_id = 1):
        resume = Resume.objects.get(id = resume_id)

        data = {
            "name": resume.name,
            "phone": resume.phone,
            "email": resume.email,
            "address": resume.address,
            "projects": list(resume.projects.values()),
            "jobs": list(resume.jobs.values()),
            "researchs": list(resume.researchs.values()),
            "educations": list(resume.educations.values())
        }
        
        return JsonResponse(data)
    