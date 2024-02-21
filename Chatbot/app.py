from transformers import AutoTokenizer
from sentence_transformers import SentenceTransformer
from unstructured.cleaners.core import clean
from tqdm import tqdm
import transformers
import torch
import chromadb
import gradio as gr
import random
import time
import nltk
import gdown
import re
import openai
from nltk import sent_tokenize
from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

nltk.download('punkt') 
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
llm = "codellama/CodeLlama-7b-Instruct-hf"

with open('NNPC_Knowledge_Base.txt', 'r') as file:
  full_text = file.read()

chroma_client = chromadb.Client()
try:
  collection = chroma_client.create_collection(name = 'nnpc')
except:
  chroma_client.delete_collection(name = 'nnpc')
  collection = chroma_client.create_collection(name = 'nnpc')

sentences = sent_tokenize(full_text)
documents = []
metadatas = []
ids = []
embeddings = []

def clean_whitespace(input_str):
  return re.sub(r'\n+', '\n', input_str)

for i in tqdm(range(len(sentences)), 'Generating Vector Database'):
  text = sentences[i]
  text = clean_whitespace(text)
  embedding = embedding_model.encode(text)

  embeddings.append(embedding.tolist())
  documents.append(text)
  metadatas.append({'source': 'The Nigerian National Petroleum Corporation'})
  ids.append(f'id{i}')

collection.add(
    embeddings=embeddings,
    documents=documents,
    metadatas=metadatas,
    ids=ids,
)

tokenizer = AutoTokenizer.from_pretrained(llm)
pipeline = transformers.pipeline(
    "text-generation",
    model=llm,
    torch_dtype=torch.float16,
    device_map="auto",
)

def respond(user_prompt, use_openai=False, api_key=""):
  context = collection.query(
    query_embeddings = [embedding_model.encode(user_prompt).tolist()],
    n_results = 2,
  )
  context = ''.join(context['documents'][0])
  if use_openai:
    openai.api_key=api_key
    system_prompt = f"""Use the provided context to answer the question
    Say you don't know if the context does not provide enough information
    \n Context: {context}"""
    #prompt = f"\n{system_prompt}\n{user_prompt} Response:"
    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
        {"role": "system", "content": f'{system_prompt}'},
        {"role": "user", "content": f'{user_prompt}'},
      ],
      temperature=0.1
    )
    return response.choices[0]['message']['content']
  else:    
    system_prompt = f"""Use the provided context to answer the question
    Say you don't know if the context does not provide enough information
    \n Context: {context}"""
    prompt = f"<s><<SYS>>\n{system_prompt}\n<</SYS>>\n\n\n{user_prompt} Response:"
    sequences = pipeline(
      prompt,
      do_sample=True,
      top_k=5,
      temperature=0.1,
      top_p=0.85,
      num_return_sequences=1,
      eos_token_id=tokenizer.eos_token_id,
      pad_token_id=tokenizer.eos_token_id,
      max_new_tokens=256,
      #max_length=1024,
      add_special_tokens=False,
    )
    response = sequences[0]['generated_text'].split(f'{user_prompt} Response:', 1)[1]
    response = clean_whitespace(response)
    return response

class User_Prompt(BaseModel):
  message: str
  use_openai: bool = False
  api_key: str = ""
    
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with the list of allowed origins if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/")
def home(user_prompt: User_Prompt):
  bot_response = respond(user_prompt.message, user_prompt.use_openai, user_prompt.api_key)
  return {"data": bot_response}

if __name__ == "__main__":
  uvicorn.run(app, port=8000)