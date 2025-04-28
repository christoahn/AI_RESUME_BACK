from openai import OpenAI
import anthropic
import google.generativeai as genai
import json
import threading

class resume_chunk:
    def __init__(self, CHATGPT_API: str, CLAUDE_API: str, GEMINI_API: str, DEEPSEEK_API: str, section: str) -> None:
        self._CHATGPT_API = CHATGPT_API
        self._CLAUDE_API = CLAUDE_API
        self._GEMINI_API = GEMINI_API
        self._DEEPSEEK_API = DEEPSEEK_API
        self._section = section
        self._sectionOutputOrder = {"projects" : {
            "title": "Project Name", 
            "position" : "user's position", 
            "duration" : "duration of project", 
            "description" : "Project Description based on keyword"
            },
            "jobs" : {
                "title" : "job title",
                "position" : "job position",
                "duration" : "duration for job",
                "description" : "job role descritpion based on keyword"
            }
        }

    def set_chatgptAPI(self, api_key):
        assert isinstance(api_key, str)
        self._CHATGPT_API = api_key

    def set_claudeAPI(self, api_key):
        assert isinstance(api_key, str)
        self._CLAUDE_API = api_key
    
    def set_geminiAPI(self, api_key):
        assert isinstance(api_key, str)
        self._GEMINI_API = api_key

    def set_deepseekAPI(self, api_key):
        assert isinstance(api_key, str)
        self._DEEPSEEK_API = api_key

    def set_assignedSection(self, section):
        """
        One of the sections
        project
        job
        research
        """
        assert isinstance(section, str)

        self._section = section
        self.set_systemRole()

    def set_systemRole(self):
        self._systemRole = "You are one parts of AI resume generator." \
            f"Your assigned section is {self._section}. " \
            f"You will be provided with {self._section} title, user's position, and keywords for the {self._section}. " \
            "Your role is generating one chunk of resume based on keyword and STAR methodology (Situation, Task, Action, Result). " \
            "Also you will edit it by user's preference and command. " \
            "The output should \"JSON\" format like this: " \
            f"{self._sectionOutputOrder[self._section]}." \
            "Again, your job is to make DETAILED sentences without any ambiguity with provided Keyword. Include detailed numbers if possible. This is your final Goal." \
            "Use \n for different topic discription."
    
    def generate_resume(self, self_input):
        """
        Return in JSON
        """
        self._user_input = self_input
        self.three_models()
        self.blending()
        self.json_parsing()
        return self.json_result

    def three_models(self):
        assert isinstance(self._user_input, dict)
        results = [None, None, None]
        self._user_input = f"{self._user_input}"

        def chat_gpt():
            client = OpenAI(api_key= self._CHATGPT_API)
            completion = client.chat.completions.create(
                model="gpt-4o", 
                store=True, 
                messages = [
                    {"role": "developer", "content": self._systemRole},
                    {"role": "user", "content": self._user_input}
                ]
            )
            results[0] = completion.choices[0].message.content
            # print(completion.choices[0].message.content)

        #Claude
        def claude():
            client = anthropic.Anthropic(
                api_key=self._CLAUDE_API,
            )
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                temperature=0.0,
                system = self._systemRole,
                messages = [{'role': 'user', 'content': self._user_input}]
            )
            results[1] = message.content[0].text
            # print(message.content[0].text)

        #Gemini
        def gemini():
            genai.configure(api_key=self._GEMINI_API)

            model2 = genai.GenerativeModel(model_name='gemini-2.5-pro-exp-03-25',
                                        system_instruction=self._systemRole)
            response2 = model2.generate_content(
                contents=self._user_input
            )
            results[2] = response2.text
            # print(response2.text)

        threads = [
            threading.Thread(target=chat_gpt),
            threading.Thread(target=claude),
            threading.Thread(target=gemini),
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        self.three_modelsResult = results
    
    def blending(self):
        client = OpenAI(api_key=self._DEEPSEEK_API, base_url="https://api.deepseek.com")
        self._blending_result = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": "You are an output blender. Your job is to blend three inputs into one output and make a best possible outcome." \
                        f"The output should be JSON format that looks like this: {self._sectionOutputOrder[self._section]}." \
                            "Any specific numbers in input should be replaced with underbar. Make it as 3 ~ 4 bullet pointed Descriptions with list format."},
                        {"role": "user", "content": f"1st Input: {self.three_modelsResult[0]}, 2nd Input: {self.three_modelsResult[1]}, 3rd Input: {self.three_modelsResult[2]}"}
                    ],
                    stream=False
                )
        
    def json_parsing(self):
        try:
            # 여러 형식의 JSON 파싱 시도
            if self._blending_result.startswith('['):
                self.json_result = json.loads(self._blending_result)
                if isinstance(self.json_result, list) and len(self.json_result) > 0:
                    return self.json_result[0]  # 리스트의 첫 번째 항목 반환
                else:
                    raise ValueError("Empty array result")
            elif self._blending_result.startswith('{'):
                self.json_result = json.loads(self._blending_result)
                return self.json_result  # 단일 객체 반환
            else:
                # 중간에 JSON 객체가 있는지 확인
                self._blending_result = self._blending_result.replace("```json", "").replace("```", "")
                # JSON 부분만 추출 시도
                json_start = self._blending_result.find('{')
                json_end = self._blending_result.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_content = self._blending_result[json_start:json_end]
                    self.json_result = json.loads(json_content)
                    return self.json_result
                else:
                    raise ValueError("No valid JSON found in content")
        except (json.JSONDecodeError, ValueError) as json_err:
            print(f"JSON parsing error: {str(json_err)}")
            print(f"Content to parse: {self._blending_result}")
        