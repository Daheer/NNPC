from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from transformers import T5ForConditionalGeneration, AutoTokenizer
import nltk
from nltk.tokenize import sent_tokenize


class IncomingText(BaseModel):
  text: str

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with the list of allowed origins if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

nltk.download('punkt')

tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-base", device_map="auto")

def summarize(incoming_text: str):
  texts = sent_tokenize(incoming_text)
  texts = ['Write an excellent summary of the following text.'+' '.join(texts[i:i+5]) for i in range(0, len(texts), 5)]

  tokenized_texts = tokenizer(texts, return_tensors="pt", padding=True)
  input_ids = tokenized_texts.input_ids.to("cuda")
  attention_mask = tokenized_texts.attention_mask.to("cuda")

  outputs = model.generate(input_ids = input_ids, attention_mask = attention_mask, max_new_tokens=512)
  outputs = tokenizer.batch_decode(outputs, skip_special_tokens = True)
  return '\n'.join(outputs)

@app.post("/")
def home(incoming_text: IncomingText):
  summary = summarize(incoming_text.text)
  return {"summary": summary}

if __name__ == "__main__":
  uvicorn.run(app, port=8000)