"""
Módulo de views para o sistema de chat.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import json
import uuid

# =====================================================
# BLUEPRINT
# =====================================================
chat_bp = Blueprint('chat', __name__)

# =====================================================
# SIMULAÇÃO DE BANCO DE DADOS EM MEMÓRIA
# =====================================================
# Em produção, isso deveria ser substituído por um modelo real
chat_messages = []
chat_sessions = {}

# =====================================================
# ENDPOINTS
# =====================================================

@chat_bp.route('/send-message', methods=['POST'])
@jwt_required()
def send_message():
    """
    Envia uma mensagem no chat e retorna a resposta do bot.
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Mensagem é obrigatória'}), 400
        
        user_id = get_jwt_identity()
        user_message = data['message'].strip()
        
        if not user_message:
            return jsonify({'error': 'Mensagem não pode estar vazia'}), 400
        
        # Criar mensagem do usuário
        user_msg = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'message': user_message,
            'sender': 'user',
            'timestamp': datetime.utcnow().isoformat(),
            'session_id': data.get('session_id', 'default')
        }
        
        chat_messages.append(user_msg)
        
        # Gerar resposta do bot baseada no contexto
        bot_response = generate_bot_response(user_message, user_id)
        
        # Criar mensagem do bot
        bot_msg = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'message': bot_response,
            'sender': 'bot',
            'timestamp': datetime.utcnow().isoformat(),
            'session_id': data.get('session_id', 'default')
        }
        
        chat_messages.append(bot_msg)
        
        return jsonify({
            'success': True,
            'user_message': user_msg,
            'bot_response': bot_msg,
            'session_id': data.get('session_id', 'default')
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@chat_bp.route('/messages', methods=['GET'])
@jwt_required()
def get_messages():
    """
    Retorna o histórico de mensagens do usuário.
    """
    try:
        user_id = get_jwt_identity()
        session_id = request.args.get('session_id', 'default')
        limit = int(request.args.get('limit', 50))
        
        # Filtrar mensagens do usuário e sessão
        user_messages = [
            msg for msg in chat_messages 
            if msg['user_id'] == user_id and msg['session_id'] == session_id
        ]
        
        # Ordenar por timestamp e limitar
        user_messages.sort(key=lambda x: x['timestamp'])
        user_messages = user_messages[-limit:]
        
        return jsonify({
            'success': True,
            'messages': user_messages,
            'session_id': session_id
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@chat_bp.route('/sessions', methods=['GET'])
@jwt_required()
def get_sessions():
    """
    Retorna as sessões de chat do usuário.
    """
    try:
        user_id = get_jwt_identity()
        
        # Agrupar mensagens por sessão
        sessions = {}
        for msg in chat_messages:
            if msg['user_id'] == user_id:
                session_id = msg['session_id']
                if session_id not in sessions:
                    sessions[session_id] = {
                        'session_id': session_id,
                        'last_message': msg['message'],
                        'last_timestamp': msg['timestamp'],
                        'message_count': 0
                    }
                sessions[session_id]['message_count'] += 1
        
        return jsonify({
            'success': True,
            'sessions': list(sessions.values())
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@chat_bp.route('/clear-session', methods=['POST'])
@jwt_required()
def clear_session():
    """
    Limpa uma sessão específica do chat.
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        session_id = data.get('session_id', 'default')
        
        # Remover mensagens da sessão
        global chat_messages
        chat_messages = [
            msg for msg in chat_messages 
            if not (msg['user_id'] == user_id and msg['session_id'] == session_id)
        ]
        
        return jsonify({
            'success': True,
            'message': f'Sessão {session_id} limpa com sucesso'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

# =====================================================
# FUNÇÕES AUXILIARES
# =====================================================

def generate_bot_response(user_message: str, user_id: str) -> str:
    """
    Gera uma resposta do bot baseada na mensagem do usuário.
    """
    message_lower = user_message.lower()
    
    # Respostas baseadas em palavras-chave
    if any(word in message_lower for word in ['olá', 'oi', 'hello', 'hi']):
        return "Olá! Como posso ajudá-lo com o sistema de propostas hoje?"
    
    elif any(word in message_lower for word in ['proposta', 'propostas']):
        return "Posso ajudá-lo com propostas! Você pode criar, editar ou visualizar propostas no sistema. Gostaria de saber mais sobre alguma funcionalidade específica?"
    
    elif any(word in message_lower for word in ['cliente', 'clientes']):
        return "Para gerenciar clientes, acesse a seção 'Clientes' no menu lateral. Lá você pode adicionar novos clientes, editar informações existentes e visualizar todos os clientes cadastrados."
    
    elif any(word in message_lower for word in ['serviço', 'serviços']):
        return "Os serviços são categorizados por tipo de atividade e regime tributário. Posso ajudá-lo a entender como configurar ou calcular serviços para suas propostas."
    
    elif any(word in message_lower for word in ['ajuda', 'help', 'suporte']):
        return "Estou aqui para ajudar! Posso esclarecer dúvidas sobre: propostas, clientes, serviços, regimes tributários e funcionalidades do sistema. O que você gostaria de saber?"
    
    elif any(word in message_lower for word in ['obrigado', 'valeu', 'thanks']):
        return "De nada! Estou sempre aqui para ajudar. Se precisar de mais alguma coisa, é só perguntar!"
    
    elif any(word in message_lower for word in ['tchau', 'bye', 'até']):
        return "Até logo! Tenha um ótimo dia e não hesite em voltar se precisar de ajuda!"
    
    else:
        return "Entendo sua pergunta! Para melhor ajudá-lo, posso esclarecer dúvidas sobre: criação de propostas, gestão de clientes, configuração de serviços, regimes tributários ou outras funcionalidades do sistema. O que você gostaria de saber especificamente?"
