# Galeria de Fotos — Object Storage com MinIO

Projeto de estudo construído para aprofundar conceitos de **Object Storage** na prática: upload direto do navegador para o bucket via presigned URLs, listagem de objetos e exibição em galeria, sem o backend nunca tocar no arquivo binário.

## Arquitetura

```
Angular (Vercel)  ──POST /upload-url──>  FastAPI (Render)
Angular (Vercel)  ──POST direto──────>  MinIO (local)
Angular (Vercel)  ──GET /photos──────>  FastAPI (Render) ──> MinIO (local)
```

O fluxo de upload usa **presigned POST**: o backend apenas gera uma URL assinada temporária, e o navegador envia o arquivo diretamente para o bucket. O backend nunca recebe nem armazena o binário — só concede permissão temporária.

### Por que o MinIO roda só localmente

Por decisão de segurança, o MinIO **não está exposto publicamente**. Deixar um object storage acessível na internet (mesmo com credenciais) é uma superfície de ataque conhecida — é comum haver varreduras automatizadas atrás de buckets mal configurados. Por isso, o MinIO roda exclusivamente na máquina local, enquanto o backend FastAPI (que não armazena dados sensíveis, apenas emite URLs assinadas) é o único componente publicado no Render.

Isso significa que, em produção, os endpoints que dependem de listagem/leitura do bucket (`/photos`) só funcionam enquanto o MinIO local estiver acessível pelo backend (por exemplo, via túnel temporário como ngrok durante demonstrações). O deploy serve principalmente para validar que o backend builda e roda corretamente como serviço web.

## Stack

| Camada | Tecnologia |
|---|---|
| Frontend | Angular 22 (signals, `@Service()`, control flow `@if`/`@for`), Bootstrap 5 |
| Backend | FastAPI, boto3, uv |
| Object Storage | MinIO (imagem [Chainguard](https://github.com/chainguard-images/images), já que a MinIO descontinuou suas imagens Docker públicas) |
| Infraestrutura | Docker Compose (local), Render (backend), Vercel (frontend) |

## Funcionalidades

- Upload de imagens direto do navegador para o bucket via **presigned POST**
- Preview da imagem antes do envio, com limpeza automática após sucesso
- Listagem da galeria via **presigned GET URLs** com expiração configurável
- Atualização automática da galeria após cada upload, sem reload de página

## Rodando localmente

### Pré-requisitos

- Docker e Docker Compose
- Node.js + Angular CLI
- `uv` (gerenciador de pacotes Python)

### 1. Subir o backend + MinIO

```bash
cp .env.example .env
# edite o .env com suas credenciais
docker compose up --build
```

Isso sobe:
- MinIO em `http://localhost:9000` (API) e `http://localhost:9001` (console)
- Backend FastAPI em `http://localhost:8000`

### 2. Criar o bucket

Use o console do MinIO (`http://localhost:9001`) ou `boto3`/`mc` para criar o bucket definido em `MINIO_BUCKET_NAME`.

### 3. Rodar o frontend

```bash
cd front-end
npm install
ng serve
```

Acesse `http://localhost:4200`.

## Variáveis de ambiente

```env
MINIO_ENDPOINT=http://minio:9000
MINIO_PUBLIC_ENDPOINT=http://localhost:9000
MINIO_KEY_ACCESS=
MINIO_KEY_SECRET=
MINIO_BUCKET_NAME=
```

| Variável | Descrição |
|---|---|
| `MINIO_ENDPOINT` | Endpoint usado pelo backend para se conectar ao MinIO (rede interna do Docker) |
| `MINIO_PUBLIC_ENDPOINT` | Endpoint usado para **assinar** URLs que o navegador vai acessar |
| `MINIO_KEY_ACCESS` / `MINIO_KEY_SECRET` | Credenciais de acesso ao MinIO |
| `MINIO_BUCKET_NAME` | Nome do bucket usado pela aplicação |

## Principais aprendizados do projeto

- Diferença entre presigned **POST** (upload, assinatura via política de formulário) e presigned **GET** (download, assinatura inclui o host) — por isso é necessário usar clients boto3 distintos para operações internas e para assinatura de URLs públicas.
- `addressing_style: path` é necessário em ambientes sem DNS de subdomínio configurado (como MinIO local), diferente do `virtual` recomendado para S3 real.
- CORS precisa ser configurado em **cada camada** separadamente: no servidor MinIO (globalmente, via variável de ambiente na Community Edition) e no backend FastAPI (`CORSMiddleware`), já que são origens e protocolos distintos sendo acessados pelo navegador.
- Build de produção do Angular com SSR tenta prerenderizar rotas, o que quebra quando o componente depende de uma API indisponível durante o build — resolvido configurando `RenderMode.Client` para rotas dinâmicas.

## Licença

Projeto de estudo pessoal, sem licença de uso comercial definida.