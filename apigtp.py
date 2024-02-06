from PyPDF2 import PdfReader
from openai import OpenAI
from flask import Flask, request, render_template, jsonify, session
import tempfile
import os
import tiktoken
import docx2txt

client = OpenAI()

app = Flask(__name__, template_folder='template')
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


custo_acumulado = [0]

@app.route('/chatpgm')
def index():
    return render_template('index.html')

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def extract_text_from_word(word_file):
    word_text = docx2txt.process(word_file)
    return word_text

def extract_text_from_pdf(pdf_file):
    pdf_text = ""
    pdf_reader = PdfReader(pdf_file)
    for page in pdf_reader.pages:
        pdf_text += page.extract_text()
    return pdf_text
    

@app.route('/resposta', methods=['POST'])
def resposta():
    try:

        uploaded_file = request.files['uploaded_file']

        if uploaded_file.filename != '':
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
            uploaded_file.save(file_path)
            session['file_path'] = file_path  

        
        pergunta = request.form['pergunta']
        conteudo = "Você está respondendo a perguntas sobre o conteúdo do documento, fique atento e extraia cada palavra para conseguir interpretar bem as perguntas, sendo que você é um procurador experiente do município do estado do Rio de Janeiro."


        file_path = session.get('file_path', '')

        if file_path:
            if file_path.endswith('.pdf'):
                text = extract_text_from_pdf(file_path)
            elif file_path.endswith('.docx'):
                text = extract_text_from_word(file_path)
            

            completion = client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=[
                    {"role": "system", "content": conteudo},
                    {"role": "user", "content": pergunta},
                    {"role": "assistant", "content": text}
                ]
            )

            resposta = completion.choices[0].message.content

            tokens_input = num_tokens_from_string(conteudo +  pergunta + text, "cl100k_base")
            tokens_output = num_tokens_from_string(resposta, "cl100k_base")
            tokens_estimados = tokens_input + tokens_output

            custo_input = (tokens_input / 1000) * 0.0010  
            custo_output = (tokens_output / 1000) * 0.0020  

            custo_total = ((custo_input + custo_output) * 1)
            custo_total_redondo = round(custo_total, 3)

            custo_acumulado[0] += custo_total_redondo
            custo_acumulado_redondo = round(custo_acumulado[0], 3)
        
        print(text)
        return render_template('index.html', resposta=resposta, pergunta=pergunta, tokens_estimados = tokens_estimados, custo_total = custo_total_redondo, custo_acumulado = custo_acumulado_redondo)
    
        
    except Exception:
        return render_template('erro.html')
    
    
if __name__ == '__main__':
    app.run(debug=False)