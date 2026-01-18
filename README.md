# Cosmopolian Backend - Contact API

Este é o back-end em FastAPI para armazenar contatos recebidos através do formulário do site. Ele utiliza PostgreSQL como banco de dados e está configurado para ser executado via Docker Compose.

## Estrutura do Projeto

- `backend/`: Código fonte da API FastAPI.
- `docker-compose.yml`: Configuração do Docker para subir a API e o Banco de Dados.
- `.env`: Variáveis de ambiente (credenciais do banco).

## Como subir na VPS (via Portainer)

### Pré-requisitos
- Docker & Portainer instalados.
- Uma rede Docker chamada `proxy_network` criada (necessária para o Reverse Proxy).

### Passo a Passo no Portainer

1. **Crie a rede externa** (se ainda não existir): No Portainer, vá em `Networks` > `Add Network` > Nome: `proxy_network`.
2. **Crie a Stack**: Vá em `Stacks` > `Add stack`.
3. **Configure a Stack**:
   - Dê um nome (ex: `cosmopolian`).
   - Cole o conteúdo do arquivo `docker-compose.yml`.
   - Na seção `Environment variables`, adicione as variáveis do arquivo `.env`.
4. **Deploy**: Clique em `Deploy the stack`.

## Reverse Proxy (Nginx Proxy Manager)
Como o backend não expõe portas públicas diretamente (por segurança), você deve usar o **Nginx Proxy Manager** para apontar seu domínio (ex: `api.dominio.com`) para o container `cosmopolian_backend` na porta `8000`.

## Notas Importantes
- O formulário no `index.html` deve apontar para o seu domínio final com HTTPS.
- O banco de dados persiste os dados no volume `postgres_data`.
