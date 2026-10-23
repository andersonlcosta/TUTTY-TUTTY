import os
import base64
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
from dotenv import load_dotenv
from groq import Groq  #  Biblioteca oficial do Groq
import uvicorn

load_dotenv()

app = FastAPI(title="Tutor IA - Exclusivo Celular")

#  SUA CHAVE DO GROQ MANTIDA CONFORME SOLICITADO
api_key = "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"
client = Groq(api_key=api_key)

INSTRUCAO_SISTEMA = (
    "Seu nome é TUTTY, você é o tutor oficial da ESCOLA ROBERTO TONELLOTTI. "
    "Você é um tutor de apoio escolar carinhoso, brincalhão, paciente e extremamente acolhedor para todas as disciplinas da educação básica, "
    "baseado estritamente no Currículo Paulista da SEDUC-SP. "
    "Aqui no Tutty, se precisar tem um assitente de libras digital."
    "Caso o aluno ou usuário pedir, o ensine a fazer um currículo e se precisar oriente como fazer jovem aprendiz. "
    "Você também é especialista em Educação Especial Inclusiva, aplicando conceitos da Análise do Comportamento Aplicada (ABA) para adaptar sua comunicação "
    "caso o aluno seja autista ou precise de suporte especializado. "
    "DIRETRIZES OBRIGATÓRIAS DE INTERAÇÃO:\n"
    "1. PROIBIDO DAR RESPOSTAS PRONTAS: Nunca, sob nenhuma circunstância, dê o resultado final. Ensine brincando, de forma lúdica e interativa.\n"
    "2. ABORDAGEM ABA E INCLUSIVA: Use linguagem clara, direta e sem ambiguidades. Divida tarefas complexas em passos muito pequenos e sequenciais. "
    "Dê instruções de uma em uma. Se o aluno acertar um pequeno passo, use REFORÇO POSITIVO imediato e entusiasmado (ex: 'Isso mesmo! Você foi incrível! 🌟 Agora vamos para o próximo passo?').\n"
    "3. TOM DE VOZ: Seja extremamente afetuoso, use emojis acolhedores, valide os sentimentos do aluno com carinho e mantenha um clima de brincadeira saudável e encorajadora.\n"
    "Se o aluno enviar a foto de uma atividade ou apostila, analise atentamente a imagem, extraia o problema e guie-o passo a passo sem dar a resposta pronta.\n"
    "Responda sempre em português brasileiro, com frases curtas e fáceis de ler, demonstrando imenso orgulho de fazer parte da Escola Roberto Tonellotti."
)

class MensagemItem(BaseModel):
    role: str
    text: Optional[str] = ""
    image_base64: Optional[str] = None

class ConversaInput(BaseModel):
    historico: List[MensagemItem]

@app.get("/", response_class=HTMLResponse)
def obter_interface_teste():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"<h1>Erro ao carregar o arquivo index.html: {str(e)}</h1>"

@app.post("/perguntar")
def perguntar_tutor(dados: ConversaInput):
    try:
        if not dados.historico:
            return {"resposta": "Histórico vazio."}

        # Captura os dados do último envio do aluno
        ultima_interacao = dados.historico[-1]
        ultima_mensagem_texto = ultima_interacao.text.strip() if ultima_interacao.text else ""
        imagem_atual = ultima_interacao.image_base64

        #  CONSTRUÇÃO E ALINHAMENTO DO HISTÓRICO PARA A API DO GROQ
        mensagens_groq = []
        
        # Reconstrói as mensagens anteriores da conversa de forma limpa (como strings)
        for msg in dados.historico[:-1]:
            role_map = "user" if msg.role == "user" else "assistant"
            if msg.text and msg.text.strip():
                mensagens_groq.append({"role": role_map, "content": msg.text.strip()})

        # Monta a estrutura da mensagem atual do aluno e define o modelo correto
        if imagem_atual and len(imagem_atual.strip()) > 50:
            # Garante que a string base64 possua o prefixo de Data URI exigido pela API do Groq
            url_imagem = imagem_atual.strip()
            if not url_imagem.startswith("data:"):
                url_imagem = f"data:image/jpeg;base64,{url_imagem}"

            # MODO VISÃO (Para processar a imagem da apostila)
            diretriz_ajuste = f"[DIRETRIZ DE COMPORTAMENTO OBRIGATÓRIA: {INSTRUCAO_SISTEMA}]\n\n"
            texto_pergunta = ultima_mensagem_texto if ultima_mensagem_texto else "Analise a imagem da minha apostila e me ajude a resolver este exercício seguindo nossas regras pedagógicas."
            
            conteudo_atual = [
                {
                    "type": "text",
                    "text": f"{diretriz_ajuste}Pergunta do aluno: {texto_pergunta}"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": url_imagem
                    }
                }
            ]
            # ID OFICIAL CORRIGIDO: qwen/qwen3.8-27b ativo na camada vision do Groq
            modelo_escolhido = "qwen/qwen3.8-27b"
            mensagens_groq.append({"role": "user", "content": conteudo_atual})
        else:
            #  MODO TEXTO PURO (Usando o modelo flagship do seu painel)
            mensagens_groq.insert(0, {"role": "system", "content": INSTRUCAO_SISTEMA})
            mensagens_groq.append({"role": "user", "content": ultima_mensagem_texto})
            
            # Modelo padrão de texto que gerou sucesso nos logs da sua conta
            modelo_escolhido = "openai/gpt-oss-120b"

        # Executa a inferência de alta velocidade no Groq
        chat_completion = client.chat.completions.create(
            messages=mensagens_groq,
            model=modelo_escolhido,
            temperature=0.7,
        )
        
        #  Resposta extraída da primeira escolha do SDK
        resposta_final = chat_completion.choices[0].message.content
        return {"resposta": resposta_final}
        
    except Exception as e:
        return {"resposta": f"Ops! O TUTTY teve um probleminha para processar. Detalhes: {str(e)}"}

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=porta)
