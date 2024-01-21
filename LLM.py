import re
from openai import OpenAI
from dotenv import load_dotenv
from telepot import Bot
from DBPipeline import DBInstance
import os
from llama_cpp import Llama
from huggingface_hub import hf_hub_download
from SettingLoder import BOT_PERSONA,USER_PERSEPECTIVE_RULE
from rich import print
from rich.console import Console

# Create a Console instance with the desired style
console = Console()

load_dotenv()
Database = DBInstance()

llm_hf_repo_id = "TheBloke/Mistral-7B-Instruct-v0.2-GGUF"
llm_hf_model_file = "mistral-7b-instruct-v0.2.Q4_K_M.gguf"

model_path = hf_hub_download(
    repo_id=llm_hf_repo_id, filename=llm_hf_model_file,
    cache_dir="models/cache",
    local_dir="models",
    resume_download=True,)


def getSystemPrompt():
    with open("DB/ServiceInfo.txt", "r") as file:
        return BOT_PERSONA + "\nAbout our Service :\n" +file.read()


def getCommunicationRules():
    return USER_PERSEPECTIVE_RULE


class LLMMODEL:
    def __init__(self):
        self.Model = OpenAI(base_url="http://localhost:8000/v1",
                            api_key="gybf6btr9j993")

        self.Bot = Bot(os.environ["client_tele_bot_token"])

    def getResponseFromLLM(self, userid, ChatHistory,followup=False):
        ChatHistory = [{"role": "system", "content": getSystemPrompt(
        )}]+[{'role': x['role'], 'content': x['content']} for x in ChatHistory]
        if not followup:
            ChatHistory[-1]['content'] += f"({getCommunicationRules()})"

        Reply = ""
        line = ""
        console.print(f"\n\n[+] Query    : [black on white] {ChatHistory[-1]['content']} [/black on white]")

        try:
            Response = self.Model.chat.completions.create(
                model="local-model",
                stream=True,
                messages=ChatHistory,
                temperature=0.7,
                timeout=50000
            )
            print("[+] Response : ",end="")
            for partial in Response:
                Response = partial.choices[0].delta.content or ""
                console.print(f"[blue]{Response}[/blue]",end="")
                line += Response
                line = line.replace("Rs.", "Rs ").replace('Understood,', "").replace("Sweety:","")  
                
                if ". " in line and len(re.split(r'(?<!\d)\. ', line))>1:
                    comp = re.split(r'(?<!Rs)\. ', re.sub(
                        r'\([^)]*\)', '', line))[0]
                    if comp.strip():
                        self.Bot.sendMessage(userid, comp+".")
                        line = ". ".join(line.split(". ")[1:]).strip()
                
                if "\n" in line:
                    comp = line.split("\n")[0]
                    if comp.strip():
                        self.replyToUserWithUserid(userid, comp)
                        line = "\n".join(line.split("\n")[1:]).strip()

                Reply += re.sub(r'\([^)]*\)', '', Response)
            if line.strip():
                self.replyToUserWithUserid(userid, line)
        except Exception as e:
            print(f"\n[+] Error : {e}")
        print("\n---------------------------------[ Done ]---------------------------------")
        return Reply

    def replyToUserWithUserid(self, userid, msg):
        try:
            if msg:
                self.Bot.sendMessage(userid, re.sub(r'\([^)]*\)', '', msg))
        except Exception as e:
            print(f"[+] Sending Msg Error : {e}")

    def getFollowUpFromLLM(self, userid, ChatHistory, internalPrompt):
        ChatHistory = ChatHistory+[{"role": "user", "content": internalPrompt}]
        return self.getResponseFromLLM(userid, ChatHistory,followup=True)
