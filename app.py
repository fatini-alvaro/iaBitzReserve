from flask import Flask, request, jsonify
import random
import logging
from datetime import datetime
from unidecode import unidecode
import time  # Importando o módulo time para adicionar o atraso

app = Flask(__name__)

# Dicionário de destinos e suas informações
destinos = {
    "praias": {
        "cidade": "Florianópolis, SC",
        "descricao": "Florianópolis é famosa por suas praias paradisíacas, com águas cristalinas e ótima infraestrutura para turismo.",
        "hoteis": [
            {
                "nome": "Hotel Faial",
                "avaliacao": "8.5",
                "preco": "R$ 220",
                "descricao": "Hotel à beira-mar com vista para a praia e piscina",
                "amenidades": ["Piscina", "Wi-Fi", "Estacionamento", "Café da manhã"]
            },
            {
                "nome": "Pousada dos Sonhos",
                "avaliacao": "9.0",
                "preco": "R$ 250",
                "descricao": "Pousada familiar com ambiente acolhedor e proximidade da praia",
                "amenidades": ["Café da manhã", "Wi-Fi", "Estacionamento", "Área de lazer"]
            }
        ]
    },
    "cultura italiana": {
        "cidade": "Bento Gonçalves, RS",
        "descricao": "Bento Gonçalves é um destino perfeito para quem gosta da cultura italiana, com vinícolas incríveis e ótima gastronomia.",
        "hoteis": [
            {
                "nome": "Hotel & Spa do Vinho",
                "avaliacao": "9.2",
                "preco": "R$ 800",
                "descricao": "Hotel luxuoso com spa completo e degustação de vinhos",
                "amenidades": ["Spa", "Degustação de vinhos", "Restaurante", "Piscina", "Wi-Fi"]
            },
            {
                "nome": "Dall'Onder Grande Hotel",
                "avaliacao": "8.8",
                "preco": "R$ 450",
                "descricao": "Hotel tradicional com arquitetura italiana e café da manhã típico",
                "amenidades": ["Café da manhã", "Estacionamento", "Wi-Fi", "Restaurante"]
            }
        ]
    },
    "cultura alema": {
        "cidade": "Pomerode, SC",
        "descricao": "Pomerode é conhecida como a cidade mais alemã do Brasil, com arquitetura típica, gastronomia germânica e eventos culturais.",
        "hoteis": [
            {
                "nome": "Hotel Bergblick",
                "avaliacao": "9.2",
                "preco": "R$ 350",
                "descricao": "Hotel com arquitetura típica alemã e café da manhã com produtos alemães",
                "amenidades": ["Café da manhã alemão", "Restaurante", "Wi-Fi", "Estacionamento"]
            },
            {
                "nome": "Pousada Casarão Schmidt",
                "avaliacao": "8.9",
                "preco": "R$ 280",
                "descricao": "Pousada histórica com decoração alemã e ambiente acolhedor",
                "amenidades": ["Café da manhã", "Wi-Fi", "Estacionamento", "Jardim"]
            }
        ]
    },
    "montanhas": {
        "cidade": "Gramado, RS",
        "descricao": "Gramado é uma cidade encantadora nas montanhas, conhecida pela sua arquitetura europeia e atrações turísticas durante o inverno.",
        "hoteis": [
            {
                "nome": "Hotel Alpestre",
                "avaliacao": "9.0",
                "preco": "R$ 400",
                "descricao": "Hotel com arquitetura alpina e piscina aquecida",
                "amenidades": ["Piscina aquecida", "Spa", "Wi-Fi", "Restaurante"]
            },
            {
                "nome": "Pousada Casa da Montanha",
                "avaliacao": "8.8",
                "preco": "R$ 350",
                "descricao": "Pousada rústica com vista para as montanhas e lareira",
                "amenidades": ["Lareira", "Wi-Fi", "Estacionamento", "Café da manhã"]
            }
        ]
    }
}

# Dicionário de cupons válidos
cupons = {
    "bitz10": {"desconto": 0.10, "valido": True},
    "bitz20": {"desconto": 0.20, "valido": True},
    "bitz30": {"desconto": 0.30, "valido": True}
}

# Função para criar uma reserva
def criar_reserva(hotel, preco, cupom=None):
    # Gera um código de reserva aleatório
    codigo_reserva = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=8))
    
    # Gera um código PIX aleatório
    codigo_pix = ''.join(random.choices('0123456789', k=32))
    
    # Calcula o preço final com desconto se houver cupom
    preco_final = preco
    if cupom and cupom.lower() in cupons:
        desconto = cupons[cupom.lower()]["desconto"]
        preco_final = f"R$ {float(preco.replace('R$ ', '').replace(',', '.')) * (1 - desconto):.2f}"
    
    return {
        "codigo": codigo_reserva,
        "codigo_pix": codigo_pix,
        "preco_final": preco_final
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
    
    # Mapeamento de números para destinos
    destinos_numericos = {
        "1": "praias",
        "2": "cultura italiana",
        "3": "cultura alema",
        "4": "montanhas"
    }
    
    # Se a mensagem for um número, converte para o destino correspondente
    if mensagem_normalizada in destinos_numericos:
        destino = destinos_numericos[mensagem_normalizada]
        info = destinos[destino]
        return {
            "destino": destino,
            "resposta": f"{info['cidade']} é um ótimo destino! {info['descricao']} Quer ver algumas opções de hospedagem?"
        }
    
    # Palavras-chave para cada tipo de destino
    palavras_chave = {
        "praias": ["praia", "litoral", "mar", "costa", "beach"],
        "cultura italiana": ["italiana", "italia", "italiano", "vinho", "vinicula", "gastronomia"],
        "cultura alema": ["alema", "alemanha", "alemao", "germania", "germanica"],
        "montanhas": ["montanha", "serra", "frio", "inverno", "gramado"]
    }
    
    # Procura por palavras-chave na mensagem
    for destino, palavras in palavras_chave.items():
        if any(palavra in mensagem_normalizada for palavra in palavras):
            info = destinos[destino]
            return {
                "destino": destino,
                "resposta": f"{info['cidade']} é um ótimo destino! {info['descricao']} Quer ver algumas opções de hospedagem?"
            }
    
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
        time.sleep(1)

        if not mensagem:
            return jsonify({"resposta": "Por favor, envie uma mensagem."})

        user_id = dados.get("user_id", "default_user")
        mensagem_normalizada = normalizar_texto(mensagem)

        # Limpa o contexto se o usuário começar uma nova conversa
        if "ola" in mensagem_normalizada or "oi" in mensagem_normalizada:
            usuarios_contexto.clear()

        # Verifica se está no contexto de confirmação de pagamento
        if user_id in usuarios_contexto and usuarios_contexto[user_id] == "aguardando_pagamento":
            if mensagem_normalizada == "pago":
                codigo_reserva = usuarios_contexto.get(f"{user_id}_codigo_reserva")
                hotel = usuarios_contexto.get(f"{user_id}_hotel")
                usuarios_contexto.clear()
                return jsonify({
                    "resposta": f"✅ Pagamento identificado com sucesso!\n\nSua reserva no {hotel} foi confirmada!\nCódigo da Reserva: {codigo_reserva}\n\n🎁 Bônus de Indicação:\nVocê recebeu um cupom de indicação: BITZINDICA\n\nCompartilhe este código com 5 amigos e você ganha:\n- 20% de desconto na sua próxima reserva\n- Participação no sorteio de uma estadia gratuita\n\nTenha uma ótima viagem! 🎉\n\nPosso ajudar com mais alguma coisa?"
                })
            else:
                return jsonify({"resposta": "Aguardando confirmação do pagamento. Digite 'PAGO' quando o pagamento for realizado."})

        # Verifica se está no contexto de cupom
        if user_id in usuarios_contexto and usuarios_contexto[user_id] == "aguardando_cupom":
            if mensagem_normalizada in cupons and cupons[mensagem_normalizada]["valido"]:
                reserva = criar_reserva(
                    usuarios_contexto[f"{user_id}_hotel"],
                    usuarios_contexto[f"{user_id}_preco"],
                    mensagem_normalizada
                )
                usuarios_contexto[user_id] = "aguardando_pagamento"
                usuarios_contexto[f"{user_id}_codigo_reserva"] = reserva["codigo"]
                usuarios_contexto[f"{user_id}_hotel"] = usuarios_contexto[f"{user_id}_hotel"]
                
                return jsonify({
                    "reserva": True,
                    "codigo_reserva": reserva["codigo"],
                    "codigo_pix": reserva["codigo_pix"],
                    "preco_final": reserva["preco_final"],
                    "resposta": f"Ótimo! Sua reserva foi criada com sucesso!\n\nCódigo da Reserva: {reserva['codigo']}\nValor final: {reserva['preco_final']}\n\nPara pagar via PIX, use o código: {reserva['codigo_pix']}\n\nApós realizar o pagamento, digite 'PAGO' para confirmarmos sua reserva."
                })
            elif mensagem_normalizada == "nao":
                reserva = criar_reserva(
                    usuarios_contexto[f"{user_id}_hotel"],
                    usuarios_contexto[f"{user_id}_preco"]
                )
                usuarios_contexto[user_id] = "aguardando_pagamento"
                usuarios_contexto[f"{user_id}_codigo_reserva"] = reserva["codigo"]
                usuarios_contexto[f"{user_id}_hotel"] = usuarios_contexto[f"{user_id}_hotel"]
                
                return jsonify({
                    "reserva": True,
                    "codigo_reserva": reserva["codigo"],
                    "codigo_pix": reserva["codigo_pix"],
                    "preco_final": reserva["preco_final"],
                    "resposta": f"Perfeito! Sua reserva foi criada com sucesso!\n\nCódigo da Reserva: {reserva['codigo']}\nValor: {reserva['preco_final']}\n\nPara pagar via PIX, use o código: {reserva['codigo_pix']}\n\nApós realizar o pagamento, digite 'PAGO' para confirmarmos sua reserva."
                })
            else:
                return jsonify({"resposta": "Cupom inválido ou já utilizado. Deseja continuar com o preço original? (sim/não)"})

        # Verifica se está no contexto de seleção de hotel
        if user_id in usuarios_contexto and usuarios_contexto[user_id] == "aguardando_selecao_hotel":
            try:
                indice_hotel = int(mensagem) - 1
                destino = usuarios_contexto[f"{user_id}_destino"]
                if 0 <= indice_hotel < len(destinos[destino]["hoteis"]):
                    hotel = destinos[destino]["hoteis"][indice_hotel]
                    usuarios_contexto[user_id] = "aguardando_cupom"
                    usuarios_contexto[f"{user_id}_hotel"] = hotel["nome"]
                    usuarios_contexto[f"{user_id}_preco"] = hotel["preco"]
                    return jsonify({
                        "resposta": f"Ótima escolha! Você selecionou o {hotel['nome']} por {hotel['preco']}.\n\nVocê tem algum cupom de desconto? (Ex: BITZ10, BITZ20, BITZ30)\nSe não tiver, digite 'não' para continuar."
                    })
            except ValueError:
                pass
            return jsonify({"resposta": "Por favor, selecione um número válido de hotel."})

        # Verifica se está no contexto de hospedagem
        if user_id in usuarios_contexto and usuarios_contexto[user_id] == "aguardando_hospedagem":
            if confirmar_resposta(mensagem):
                destino = usuarios_contexto.get(f"{user_id}_destino")
                if destino:
                    resposta = f"Ótimo! Aqui estão as opções de hotéis em {destinos[destino]['cidade']}:\n\n"
                    for i, hotel in enumerate(destinos[destino]["hoteis"], 1):
                        resposta += f"{i}. {hotel['nome']}\n"
                        resposta += f"   Avaliação: {hotel['avaliacao']}\n"
                        resposta += f"   Preço: {hotel['preco']}\n"
                        resposta += f"   {hotel['descricao']}\n"
                        resposta += f"   Amenidades: {', '.join(hotel['amenidades'])}\n\n"
                    resposta += "Digite o número do hotel que você deseja reservar:"
                    
                    usuarios_contexto[user_id] = "aguardando_selecao_hotel"
                    return jsonify({"resposta": resposta})
                else:
                    return jsonify({"resposta": "Não consegui identificar o destino. Pode repetir?"})
            else:
                usuarios_contexto.pop(user_id, None)
                return jsonify({"resposta": "Tudo bem! Me avise se precisar de mais informações."})

        # Verifica se está no contexto de preferências
        if user_id in usuarios_contexto and usuarios_contexto[user_id] == "aguardando_preferencias":
            try:
                indice = int(mensagem) - 1
                destinos_lista = list(destinos.keys())
                if 0 <= indice < len(destinos_lista):
                    destino = destinos_lista[indice]
                    info = destinos[destino]
                    usuarios_contexto[user_id] = "aguardando_hospedagem"
                    usuarios_contexto[f"{user_id}_destino"] = destino
                    return jsonify({"resposta": f"{info['cidade']} é um ótimo destino! {info['descricao']} Quer ver algumas opções de hospedagem?"})
            except ValueError:
                pass
            return jsonify({"resposta": "Por favor, selecione uma opção válida (1-4):"})

        # Verifica se a mensagem é um cumprimento
        resposta = cumprimentar(mensagem)
        if resposta:
            return jsonify({"resposta": resposta})

        # Verifica se é uma solicitação de viagem
        if "viajar" in mensagem_normalizada or "viagem" in mensagem_normalizada or "conhecer" in mensagem_normalizada:
            # Primeiro tenta identificar um destino específico
            palavras_chave = {
                "praias": ["praia", "litoral", "mar", "costa", "beach"],
                "cultura italiana": ["italiana", "italia", "italiano", "vinho", "vinicula", "gastronomia"],
                "cultura alema": ["alema", "alemanha", "alemao", "germania", "germanica"],
                "montanhas": ["montanha", "serra", "frio", "inverno", "gramado"]
            }
            
            # Procura por palavras-chave na mensagem
            for destino, palavras in palavras_chave.items():
                if any(palavra in mensagem_normalizada for palavra in palavras):
                    info = destinos[destino]
                    usuarios_contexto[user_id] = "aguardando_hospedagem"
                    usuarios_contexto[f"{user_id}_destino"] = destino
                    return jsonify({"resposta": f"{info['cidade']} é um ótimo destino! {info['descricao']} Quer ver algumas opções de hospedagem?"})
            
            # Se não encontrou um destino específico, mostra o menu de opções
            usuarios_contexto[user_id] = "aguardando_preferencias"
            return jsonify({"resposta": "Que tipo de viagem você está pensando em fazer? Gosta de:\n\n1. Praias e litoral\n2. Cultura italiana (vinícolas e gastronomia)\n3. Cultura alemã (arquitetura e tradições)\n4. Montanhas e clima frio\n\nDigite o número da sua preferência:"})

        return jsonify({"resposta": "Desculpe, não entendi. Pode reformular sua pergunta?"})
    except Exception as e:
        return jsonify({"resposta": f"Ocorreu um erro: {str(e)}"})

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app.run(debug=True)
