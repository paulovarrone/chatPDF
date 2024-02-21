from PyPDF2 import PdfReader
from openai import OpenAI
from flask import Flask, request, render_template, jsonify, session
import tempfile
import os
import tiktoken
import docx2txt
import datetime

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

        data_atual = datetime.datetime.now()
        numero_mes = data_atual.month

        mes_str = {
            1: "Janeiro",
            2: "Fevereiro",
            3: "Março",
            4: "Abril",
            5: "Maio",
            6: "Junho",
            7: "Julho",
            8: "Agosto",
            9: "Setembro",
            10: "Outubro",
            11: "Novembro",
            12: "Dezembro"
        }[numero_mes]

        data_formatada = data_atual.strftime("%d de {} de %Y".format(mes_str))     

        pergunta = request.form['pergunta']
        conteudo = f"""Faça uma contestação.

        Certifique-se de incluir:

        AGRAVO DE INSTRUMENTO
        Nº do Processo: 
        Agravante: 
        Agravados: 

        Breve resumo do agravo de instrumento.

        Análise da Tempestividade: Confirme se a contestação está sendo feita dentro do prazo legal.

        Impugnação Específica dos Fatos: Indique como negar, admitir ou declarar desconhecimento dos fatos alegados pela parte autora.

        Fundamentação Legal: Apresente as leis, jurisprudências e doutrinas que suportam a defesa.

        Apresentação de Provas: Especifique as provas que serão usadas para contestar as alegações da parte autora, como documentos, testemunhos, entre outros.

        Questões Preliminares e Processuais: Argumente sobre eventuais questões processuais que possam desqualificar a petição inicial ou exigir sua completa reformulação.

        Formulação do Mérito e do Pedido: Desenvolva os argumentos de mérito contra os pedidos da parte autora e formule os pedidos específicos na contestação.

        Endereçamento Correto e Evitar a Preclusão: Garanta que a contestação esteja corretamente endereçada e discuta estratégias para evitar a preclusão de defesas e argumentos. 

        
        Deve ser incluido no final da resposta com apenas uma quebra de linha:
            as informações do advogado, nome do advogado e seu registro de OAB. 
            {data_formatada} no documento.
        """


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