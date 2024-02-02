from PyPDF2 import PdfReader
from openai import OpenAI
from flask import Flask, request, render_template, jsonify, session
import tempfile
import os
import tiktoken

client = OpenAI()

app = Flask(__name__, template_folder='template')
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


custo_acumulado = [0]

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


@app.route('/chatPDF')
def index():
    return render_template('index.html')


def extract_text_from_pdf(pdf_file):
    pdf_text = ""
    pdf_reader = PdfReader(pdf_file)
    for page in pdf_reader.pages:
        pdf_text += page.extract_text()
    return pdf_text

@app.route('/resposta', methods=['POST'])
def resposta():
    uploaded_file = request.files['pdf_file']

    if uploaded_file.filename != '':
        pdf_file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
        uploaded_file.save(pdf_file_path)
        session['pdf_file_path'] = pdf_file_path  

    
    pergunta = request.form['pergunta']
    conteudo = "Você está respondendo a perguntas sobre o conteúdo do documento, fique atento e extraia cada palavra para conseguir interpretar bem as perguntas, sendo que você é um procurador experiente do município do estado do Rio de Janeiro."


    pdf_file_path = session.get('pdf_file_path', '')

    if pdf_file_path:
        
        pdf_text = extract_text_from_pdf(pdf_file_path)

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {"role": "system", "content": conteudo},
                {"role": "user", "content": pergunta},
                {"role": "assistant", "content": pdf_text}
            ]
        )

        resposta = completion.choices[0].message.content

        tokens_input = num_tokens_from_string(conteudo +  pergunta + pdf_text, "cl100k_base")
        tokens_output = num_tokens_from_string(resposta, "cl100k_base")
        tokens_estimados = tokens_input + tokens_output

        custo_input = (tokens_input / 1000) * 0.0010  
        custo_output = (tokens_output / 1000) * 0.0020  
        custo_total = ((custo_input + custo_output) * 1)
        custo_acumulado[0] += custo_total

    print(pdf_text)
    return render_template('index.html', resposta=resposta, pergunta=pergunta, tokens_estimados = tokens_estimados, custo_total = custo_total, custo_acumulado = custo_acumulado[0])

if __name__ == '__main__':
    app.run(debug=True)