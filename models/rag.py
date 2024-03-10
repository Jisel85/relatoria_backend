import torch
import textwrap

from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForCausalLM
from langchain.embeddings import HuggingFaceEmbeddings
from langchain import HuggingFacePipeline
from langchain.chains import RetrievalQA

from langchain.vectorstores import FAISS
from .semantic_search import search
from langchain.text_splitter import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100,
)

tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-chat-hf")

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-chat-hf",
    device_map='auto',
    torch_dtype=torch.float16,
    use_auth_token=True,
)

pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    max_new_tokens=1024,
    do_sample=True,
    top_k=10,
    num_return_sequences=1,
    eos_token_id=tokenizer.eos_token_id,
)

llm = HuggingFacePipeline(pipeline=pipe, model_kwargs={'temperature': 0})

embedding = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')

def chatbot(prompt):
    summary = ''
    results = search({
        'text': prompt,
        'top_k': 3,
    })['matches']
    for result in results:
        summary += (result['metadata'].get('extract_summary', '') + '\n' + result['metadata'].get('Tema - subtema', '')).strip()

    print(summary)
    splits = text_splitter.split_text(summary)
    text_chunks = text_splitter.create_documents(splits)

    vectorstore = FAISS.from_documents(text_chunks, embedding)
    chain = RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff", return_source_documents=True, retriever=vectorstore.as_retriever())
    result = chain({
            "query": f'RESPONDE SOLO EN ESPAÑOL (NO DEBES CAMBIAR BAJO NINGUN MOTIVO EL LENGUAJE): {prompt}'
        }, 
        return_only_outputs=True
    )
    return textwrap.fill(result['result'], width=500)
