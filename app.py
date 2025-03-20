from flask import Flask, request, jsonify
import random
import logging
from datetime import datetime
from unidecode import unidecode
import time  # Importando o módulo time para adicionar o atraso

app = Flask(__name__)

destinos = {
    "cultura italiana": {
        "cidade": "Bento Gonçalves, RS",
        "descricao": "Bento Gonçalves é um destino perfeito para quem gosta da cultura italiana, com vinícolas incríveis e ótima gastronomia.",
        "hoteis": [
            {"nome": "Hotel & Spa do Vinho", "avaliacao": "9.2", "preco": "R$ 800"},
            {"nome": "Dall’Onder Grande Hotel", "avaliacao": "8.8", "preco": "R$ 450"}
        ]
    },
    "cultura alema": {
        "cidade": "Pomerode, SC",
        "descricao": "Pomerode é conhecida como a cidade mais alemã do Brasil, com arquitetura típica, gastronomia germânica e eventos culturais.",
        "hoteis": [
            {"nome": "Hotel Bergblick", "avaliacao": "9.2", "preco": "R$ 350"},
            {"nome": "Pousada Casarão Schmidt", "avaliacao": "8.9", "preco": "R$ 280"}
        ]
    },
    "praias": {
        "cidade": "Florianópolis, SC",
        "descricao": "Florianópolis é famosa por suas praias paradisíacas, com águas cristalinas e ótima infraestrutura para turismo.",
        "hoteis": [
            {"nome": "Hotel Faial", "avaliacao": "8.5", "preco": "R$ 220"},
            {"nome": "Pousada dos Sonhos", "avaliacao": "9.0", "preco": "R$ 250"}
        ]
    },
    "montanhas": {
        "cidade": "Gramado, RS",
        "descricao": "Gramado é uma cidade encantadora nas montanhas, conhecida pela sua arquitetura europeia e atrações turísticas durante o inverno.",
        "hoteis": [
            {"nome": "Hotel Alpestre", "avaliacao": "9.0", "preco": "R$ 400"},
            {"nome": "Pousada Casa da Montanha", "avaliacao": "8.8", "preco": "R$ 350"}
        ]
    }
}

# Função para remover acentos e tornar a comparação insensível a maiúsculas/minúsculas
def normalizar_texto(texto):
    return unidecode(texto.lower())  # Normaliza o texto para minúsculas e remove acentos

# Função para responder cumprimentos
def cumprimentar(mensagem):
    cumprimentos = ["ola", "bom dia", "boa noite", "oi"]
    
    # Normalizar os cumprimentos e a mensagem recebida
    cumprimentos_normalizados = [normalizar_texto(cumprimento) for cumprimento in cumprimentos]
    mensagem_normalizada = normalizar_texto(mensagem)

    if mensagem_normalizada in cumprimentos_normalizados:
        hora_atual = datetime.now().hour
        if "bom dia" in mensagem_normalizada:
            return "Bom dia! Como posso te ajudar hoje?"
        elif "boa noite" in mensagem_normalizada:
            return "Boa noite! Como posso te ajudar?"
        elif "oi" in mensagem_normalizada:
            if hora_atual < 12:
                return "Oi! Bom dia, como posso ajudar você?"
            elif hora_atual < 18:
                return "Oi! Boa tarde, em que posso te ajudar?"
            else:
                return "Oi! Boa noite, como posso te ajudar?"
        elif "ola" in mensagem_normalizada:
            return "Olá! Como posso te ajudar?"
    
    return None  # Retorna None caso não seja um cumprimento

# Função para sugerir destinos e atividades
def sugerir_destino(mensagem):
    mensagem_normalizada = normalizar_texto(mensagem)
    for chave, info in destinos.items():
        if chave in mensagem_normalizada:
            return f"{info['cidade']} é um ótimo destino! {info['descricao']} Quer ver algumas opções de hospedagem?"
    return None

# Função para perguntar sobre hospedagem com base no destino
def perguntar_hospedagem(destino):
    return f"Você gostaria de saber sobre hotéis em {destino}?"

# Função para tratar respostas como "sim" para confirmar interesse
def confirmar_resposta(mensagem):
    mensagem_normalizada = normalizar_texto(mensagem)
    if "sim" in mensagem_normalizada:
        return True
    elif "nao" in mensagem_normalizada:
        return False
    return None

def obter_hospedagem(mensagem):
    mensagem_normalizada = normalizar_texto(mensagem)
    for chave, info in destinos.items():
        if chave in mensagem_normalizada:
            resposta = f"Aqui estão algumas opções de hospedagem em {info['cidade']}:\n"
            for hotel in info["hoteis"]:
                resposta += f"🏨 {hotel['nome']} - Avaliação: {hotel['avaliacao']} - Preço: {hotel['preco']}\n"
            return resposta
    return None

# Dicionário para armazenar o contexto da conversa (somente para testes simples)
# Em um sistema mais complexo, use um banco de dados ou sessão do usuário
usuarios_contexto = {}

@app.route('/')
def home():
    return open("index.html").read()

@app.route('/chat', methods=['POST'])
def chat():
    try:
        dados = request.get_json()
        mensagem = dados.get('mensagem', '').strip()
        time.sleep(1)  # Simulando processamento

        if not mensagem:
            return jsonify({"resposta": "Por favor, envie uma mensagem."})

        # Obtém o ID do usuário da requisição (simulação)
        user_id = dados.get("user_id", "default_user")

        # Se o usuário já está no contexto esperando uma resposta sobre hospedagem
        if user_id in usuarios_contexto and usuarios_contexto[user_id] == "aguardando_hospedagem":
            if confirmar_resposta(mensagem):  # Se a resposta for "sim"
                destino = usuarios_contexto.get(f"{user_id}_destino")
                if destino:
                    resposta = obter_hospedagem(destino)
                    usuarios_contexto.pop(user_id, None)  # Remove o estado de espera
                    usuarios_contexto.pop(f"{user_id}_destino", None)  # Remove o destino salvo
                    return jsonify({"resposta": resposta})
                else:
                    return jsonify({"resposta": "Não consegui identificar o destino. Pode repetir?"})
            else:
                usuarios_contexto.pop(user_id, None)  # Remove estado de espera
                return jsonify({"resposta": "Tudo bem! Me avise se precisar de mais informações."})

        # Verifica se a mensagem é um cumprimento
        resposta = cumprimentar(mensagem)
        if resposta:
            return jsonify({"resposta": resposta})

        # Verifica se é um destino
        resposta = sugerir_destino(mensagem)
        if resposta:
            # Salva o estado de espera da resposta do usuário
            usuarios_contexto[user_id] = "aguardando_hospedagem"
            usuarios_contexto[f"{user_id}_destino"] = mensagem
            return jsonify({"resposta": resposta})

        return jsonify({"resposta": "Desculpe, não entendi. Pode reformular sua pergunta?"})
    except Exception as e:
        return jsonify({"resposta": f"Ocorreu um erro: {str(e)}"})

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app.run(debug=True)
