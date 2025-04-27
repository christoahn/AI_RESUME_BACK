from django.http import JsonResponse
from django.views import View
from AI_model import models
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

        if action == 'add_chunk':
            return self.add_chunk(request)

        elif action == 'submit_resume':
            return self.submit_resume(request)

        else:
            return JsonResponse({"error": "Unknown action"}, status=400)

    def add_chunk(self, request):
        """
        get and store information from each chunk
        """
        user_input = request.POST.get('input')
        section = request.POST.get('section')

        chunk = models.resume_chunk(CHATGPT_API, CLAUDE_API, GEMINI_API, DEEPSEEK_API, section)
        result = chunk.generate_resume(user_input)

        return JsonResponse({"message": "Chunk added successfully.", "chunk": result})
    
    def 

    def submit_resume(self, request):
        final_resume = {
            "projects": self.chunks
        }
        # 여기서 DB 저장하거나, 파일 저장하거나, 그대로 return하거나
        return JsonResponse(final_resume)
