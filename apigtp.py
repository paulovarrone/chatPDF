from PyPDF2 import PdfReader
from openai import OpenAI
from flask import Flask, request, render_template, jsonify
import tempfile
import os

client = OpenAI()

app = Flask(__name__, template_folder='template')
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp() 

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

    # Extrair texto do PDF
    pdf_text = extract_text_from_pdf(pdf_file_path)

    
    pergunta = request.form['pergunta']
    conteudo = "Você está respondendo a perguntas sobre o conteúdo do PDF."

    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
            {"role": "system", "content": conteudo},
            {"role": "user", "content": pergunta},
            {"role": "assistant", "content": pdf_text}
        ]
    )

    resposta = completion.choices[0].message.content

    return render_template('index.html', resposta = resposta, pergunta = pergunta)


if __name__ == '__main__':
    app.run(debug=True)