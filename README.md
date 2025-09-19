# Sistema de Automação de VR/VA com Langchain

Este projeto implementa um sistema automatizado para processamento de dados de Vale Refeição (VR) e Vale Alimentação (VA) utilizando Langchain, Python e técnicas de busca de strings por aproximação usando o algoritmo Levenshtein distance devido a erros de escritas em nomes das colunas de algumas planilhas consultadas.

## 📋 Descrição

O sistema processa múltiplas planilhas Excel contendo dados de colaboradores, aplica regras de negócio específicas e gera uma planilha final com os valores de VR a serem concedidos, considerando:

- Colaboradores elegíveis (excluindo diretores, estagiários, aprendizes, afastados, etc.)
- Dias úteis por sindicato
- Valores específicos por sindicato
- Regras de desligamento
- Cálculo de custos (80% empresa, 20% colaborador)

Estas regras de negócio estão descritas em um arquivo de prompt de nome instructions.md e o agente através da arquitetura de agent reAct ("Reasoning and Reacting") ele lê esse prompt, raciocina e através de ferramentas customizadas, ele age nas planilhas objetivando gerar a planilha final.

### Componentes Principais

1. **Agente VR ReAct (`agente_vr.py`)**
   - Responsável definir o nosso agente que irá criar a planilha final
   - Instancia as ferramentas que o agente utilizará e atribuí o toolkit a ele
   - Atribui a LLM do Google Gemini (gemini-2.5-flash-lite) que será o "cérebro" de nosso agente
   - Carrega o prompt do agente para que ele tenha um comportamente ReAct
   - Instrui ao agente o que ele deve fazer ao carregar o arquivo de instruções instructions.md

2. **Toolkit de Ferramentas (`ferramentas.py`)**
   - Define as ferramentas customizadas que o nosso agente irá utilizar
   - Ferramentas especializadas em gerenciar arquivos (descomprimir arquivos) e arquivos temporários
   - Ferramentas especializadas em operar planilhas em Excel
   - Ferramentas de mesclagens de planilhas Excel de forma "inteligente" com o uso de algoritmo Levenshtein distance e uso do Pandas
   - Ferramentas que calcula valores de VR e gera a planilha final

3. **Aplicação Principal (`main.py`)**
   - Ponto principal de entrada da aplicação
   - Instancia o nosso único agente e invoca o mesmo ordenando que execute as instruções de negócio corretamente.

## 📁 Projeto:

```
├── data/                         # Pasta que contém o arquivo zipado com as planilhas
│   ├── Desafio 4 - Dados.zip     # Arquivo zipado com as planilhas que o agente irá descomprimir e trabalhar.
├── doc/                          # Pasta de documentação do desafio
├── instructions.md               # Prompt que contém as instruções para a geração da planilha de VR que o agente deverá executar
├── scripts/                      # Scripts Python
│   ├── agente_vr.py              # Agente VR
│   ├── excel.py 		  # Biblioteca com funções utilitárias para trabalho de planilhas em Excel 
│   ├── schemas.py 		  # Define a estrutura das ferramentas para o Pydantic
│   ├── parsers.py 		  # Define um parser customizado para parâmetros de entrada e saída das ferramentas utilizadas pelo agente
│   ├── ferramentas.py            # Ferramentas criadas para o agente trabalhar nas planilhas
│   └── main.py                   # Entrada principal do sistema.
├── output/                      # Pasta de saída que contém as planilhas que foram explodidas pelo agente e a planilha final VR MENSAL 05.2025.xlsx
│   ├── VR MENSAL 05.2025.xlsx   # Planilha final gerada.
├── .env                         # Variáveis de ambiente
├──  env.example                 # Arquivo .env de template (copiar para o nome .env)
├──  run.sh                      # Script de instalação e execução do projeto (para ambientes Linux)
├── requirements.txt             # Dependências
└── README.md                    # Este arquivo
```

## 🚀 Instalação e Uso

### Pré-requisitos

- Python 3.11+
- Chave de API Google API configurada

### Instalação

1. Clone ou baixe o projeto
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure as variáveis de ambiente no arquivo `.env`:
   ```
   GOOGLE_API_KEY=chave
   LLM_MODEL=gemini-2.5-flash-lite
   OUTPUT_FOLDER=./output
   DATA_FOLDER=./data
   INSTRUCOES_PATH=./instructions.md
   ```
   ...Ou copie o arquivo env.example para .env

### Execução

Execute a aplicação principal:
```bash
python scripts/main.py
```
Ou execute o script run.sh diretamente (somente Linux)

## 📊 Resultados

### Arquivos Gerados
- `output/VR MENSAL 05.2025.xlsx` - Planilha Excel final

## 🤖 Modelo LLM Utilizado

**Modelo**: `gemini-2.5-flash-lite`

## 🔧 Funcionalidades Técnicas

### Processamento de Dados
- **Leitura**: pandas + openpyxl
- **Cálculos**: Dias úteis, valores por sindicato
- **Saída**: Excel

### Regras de Negócio Implementadas
1. **Exclusões automáticas**:
   - Diretores
   - Estagiários
   - Aprendizes
   - Afastados
   - Colaboradores no exterior

2. **Cálculo de dias úteis**:
   - Por sindicato específico
   - Considerando férias e afastamentos
   - Regras de desligamento (até dia 15)

3. **Valores por sindicato**:
   - São Paulo: R$ 37,50/dia
   - Rio Grande do Sul: R$ 35,00/dia
   - Outros: valores específicos

4. **Divisão de custos**:
   - Empresa: 80%
   - Colaborador: 20%


## Autores - Grupo Synapse 7:

- [Adriana Rocha Castro de Paula](adrianarcdepaula@gmail.com)
- [Conrado Gornic](cgornic@gmail.com)
- [Lia Yumi Morimoro](yumi.lia.mori@gmail.com)
- [Luiz Fernando Rezende](rio2040@gmail.com)
- [Rodrigo Mibielli Peixoto](rodrigo.mibielli@gmail.com)
- [Saulo Brotto](haredo.i@gmail.com)


