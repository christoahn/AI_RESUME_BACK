from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .service import resume_chunk
from .model import Resume, Project, Job, Research, Education 
from dotenv import load_dotenv
import json, traceback
import os

load_dotenv()
CHATGPT_API = os.getenv('CHATGPT_API')
CLAUDE_API = os.getenv('CLAUDE_API')
GEMINI_API = os.getenv('GEMINI_API')
DEEPSEEK_API = os.getenv('DEEPSEEK_API')

@method_decorator(csrf_exempt, name='dispatch') #토큰 확인 절차 생략
class second_page(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def post(self, request):
        # print(json.loads(request.body))
        # action = request.POST.get('action')
        # print(action)

        # if action == 'generate_resume':
        try:
            if not isinstance(request.body, dict):
                request_body = json.loads(request.body)
            else:
                request_body = request.body
            # print(request_body)
            return self.generate_resume(request_body)
        except:
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
        assert isinstance(request_body, dict)
        """
        Request body example
        {'name':'Christopher',
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
                            'keywords': ....}},
        'projects':{
                'project1':{
                            'project_name': ...
                            'duration': ...
                            'role': ...
                            'keywords': ...},
                'project2':{
                            'project_name': ...
                            'duration': ...
                            'role': ...
                            'keywords': ...}}
        }
        """
        try:
            name       = request_body.get('name')
            phone      = request_body.get('phone')
            email      = request_body.get('email')
            address    = request_body.get('address')
            projects   = request_body.get('projects', {})
            jobs       = request_body.get('jobs', {})
            researches = request_body.get('researches', {})
            educations = request_body.get('educations', {})

            # print(projects)
            resume = Resume.objects.create(
                name = name,
                phone = phone,
                email = email,
                address = address
            )

            # print("resume")

            project_chunk = resume_chunk(CHATGPT_API, CLAUDE_API, GEMINI_API, DEEPSEEK_API, 'projects')
            jobs_chunk = resume_chunk(CHATGPT_API, CLAUDE_API, GEMINI_API, DEEPSEEK_API, 'jobs')
            research_chunk = resume_chunk(CHATGPT_API, CLAUDE_API, GEMINI_API, DEEPSEEK_API, 'researches')
            chunks = {
                'projects': project_chunk,
                'jobs': jobs_chunk,
                'researches': research_chunk
            }

            for job in jobs.values():
                if job['company_name'] == None:
                    continue
                chunk = chunks['jobs']
                desc = chunk.generate_resume(job)
                assert isinstance(desc, dict)

                Job.objects.create(
                    resume=resume,
                    company_name=job['company_name'],
                    position=job['position'],
                    work_duration=job['duration'],
                    description=desc['description']
                )

            # print(chunks)
            for project in projects.values():
                if project['project_name'] == None:
                    continue
                # print(project['project_name'])
                chunk = chunks['projects']
                desc = chunk.generate_resume(project)
                assert isinstance(desc, dict)

                Project.objects.create(
                    resume=resume,
                    title=project['project_name'],
                    project_duration=project['duration'],
                    description=desc['description']
                )

            for research in researches.values():
                if research['title'] == None:
                    continue
                # print(research["title"])
                chunk = chunks['researches']
                desc = chunk.generate_resume(research)
                assert isinstance(desc, dict)

                Research.objects.create(
                    resume=resume,
                    title=research['title'],
                    research_duration=research['research_duration'],
                    description=desc['description']
                )

            for edu in educations.values():
                if edu['school'] == None:
                    continue
                Education.objects.create(
                    resume=resume,
                    school_name=edu['school'],
                    degree=edu['degree'],
                    major = edu['major'],
                    duration=edu['duration'],
                    gpa = edu['gpa']
                )
            print(resume)

            return JsonResponse({'status':'success', 'resume_id': resume.id})
        except Exception as e:
            tb = traceback.format_exc()
            print(tb)  # 터미널 로그에 뜸
            return JsonResponse({'error': str(e)}, status=500)
    

class third_page(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def GET(self, request, resume_id = 1):
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
    