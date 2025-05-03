from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .service import resume_chunk
from .model import Resume, Project, Job, Research, Education 
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import json, traceback
import os

load_dotenv()
CHATGPT_API = os.getenv('CHATGPT_API')
CLAUDE_API = os.getenv('CLAUDE_API')
GEMINI_API = os.getenv('GEMINI_API')
DEEPSEEK_API = os.getenv('DEEPSEEK_API')

@method_decorator(csrf_exempt, name='dispatch') #토큰 확인 절차 생략
class userInfoInputPage(View):
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
        def generate_chunk(section, chunks):
            # for entry in filter(lambda x: x.get('name') is not None, section['data'].values()):
            #     model_fields = {field: entry.get(field) for field in section['fields']}

            #     if section['use_chunk']:
            #         chunk = chunks[section['key']]
            #         desc = chunk.generate_resume(entry)
            #         assert isinstance(desc, dict)
            #         model_fields['description'] = desc['description']

            #     section['model'].objects.create(resume=resume, **model_fields)
            def process_entry(entry):
                model_fields = {field: entry.get(field) for field in section['fields']}

                if section['use_chunk']:
                    chunk = chunks[section['key']]
                    desc = chunk.generate_resume(entry)
                    assert isinstance(desc, dict)
                    model_fields['description'] = desc['description']

                section['model'].objects.create(resume=resume, **model_fields)

            entries = list(filter(lambda x: x.get('name') is not None, section['data'].values()))

            with ThreadPoolExecutor() as executor:
                futures = [executor.submit(process_entry, entry) for entry in entries]
                for _ in as_completed(futures):
                    pass 
        try:
            name       = request_body.get('name')
            phone      = request_body.get('phone')
            email      = request_body.get('email')
            address    = request_body.get('address')
            projects   = request_body.get('projects', {})
            jobs       = request_body.get('jobs', {})
            researches = request_body.get('researches', {})
            educations = request_body.get('educations', {})

            print(projects)
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

            section_map = {
                'jobs': {
                    'key': 'jobs',
                    'data': jobs,
                    'model': Job,
                    'fields': ['name', 'position', 'duration'],
                    'use_chunk': True
                },
                'projects': {
                    'key': 'projects',
                    'data': projects,
                    'model': Project,
                    'fields': ['name', 'position', 'duration'],
                    'use_chunk': True
                },
                'researches': {
                    'key': 'researches',
                    'data': researches,
                    'model': Research,
                    'fields': ['name', 'duration'],
                    'use_chunk': True
                },
                'educations': {
                    'data': educations,
                    'model': Education,
                    'fields': ['name', 'degree', 'major', 'duration', 'gpa', 'coursework'],
                    'use_chunk': False
                }
            }

            threads = [
            threading.Thread(target=generate_chunk(section_map['jobs'], chunks)),
            threading.Thread(target=generate_chunk(section_map['projects'], chunks)),
            threading.Thread(target=generate_chunk(section_map['researches'], chunks)),
            threading.Thread(target=generate_chunk(section_map['educations'], chunks))
            ]

            for thread in threads:
                thread.start()

            for thread in threads:
                thread.join()
 
            return JsonResponse({'status':'success', 'resume_id': resume.id})
        except Exception as e:
            tb = traceback.format_exc()
            print(tb)  # 터미널 로그에 뜸
            return JsonResponse({'error': str(e)}, status=500)
        

    

class ResumePreviewEditPage(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get(self, request):
        resume_id = request.GET.get('resume_id')
        if resume_id == None:
            return JsonResponse({'error': 'resume_id query parameter is required.'}, status = 400)
        
        try:
            resume = int(resume_id)
        except ValueError:
            return JsonResponse({'error' : 'resume_id must be integer'}, status = 400)
        
        try:
            resume = Resume.objects.get(id = resume_id)
        except Resume.DoesNotExist:
            return JsonResponse({'error' : 'No resume found'}, status = 404)

        resume_data = {
            "name": resume.name,
            "phone": resume.phone,
            "email": resume.email,
            "address": resume.address,
            "projects": {item["id"]: item for item in resume.projects.all().values()},
            "jobs": {item["id"]: item for item in resume.jobs.all().values()},
            "researches": {item["id"]: item for item in resume.researches.all().values()},
            "educations": {item["id"]: item for item in resume.educations.all().values()}
        }
        # print(resume_data)
        return JsonResponse({'status': 'success', 'data': resume_data})
    
class ResumePreviewChat(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def POST(self, request):
        return
    