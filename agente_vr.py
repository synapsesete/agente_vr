from typing import List, Any
import os
from langchain_core.runnables.base import Runnable

from langchain.agents import AgentExecutor, create_react_agent

from langchain_core.tools import tool, Tool
from rsa import decrypt

from ferramentas import *

class AgenteVR:

    def __init__(self):
        """
        Inicializar o Agente de VR/VA passando para ele o texto de prompt do que deve ser feito.
        """
        tools = self._set_toolkit()
        llm = self._load_llm()
        llm_with_tools = llm.bind_tools(tools)
        prompt = self._load_prompt()

        from parsers import CustomAgentOutputParser

        agent = create_react_agent(
            llm=llm_with_tools,
            tools=tools,
            prompt=prompt,
            output_parser=CustomAgentOutputParser(),
        )

        self.__agent_executor = AgentExecutor(
            agent=agent, tools=tools, handle_parsing_errors=True, verbose=True
        )

    def _set_toolkit(self) -> List[str]:
        from langchain_community.agent_toolkits import FileManagementToolkit

        toolkit = FileManagementToolkit(selected_tools=["copy_file"])
        tools = [
            UnzipFileTool(),
            ReunirDadosTool(),
#            ObterDadosTool(),
            EscreverDadosNaPlanilhaTool(),
#            ExtrairDadosColunasTool(),
 #           CalcularQuantidadeDiasUteisTool()
        ]
        tools.extend(toolkit.get_tools())
        return tools

    def _load_llm(self) -> Runnable:
        from dotenv import load_dotenv

        load_dotenv()
        from langchain_ollama import ChatOllama
        from langchain_google_genai import ChatGoogleGenerativeAI

        if os.environ.get("GOOGLE_API_KEY"):
            llm = ChatGoogleGenerativeAI(model=os.environ["LLM_MODEL"], temperature=0)
        else:
            llm = ChatOllama(
                temperature=0,
                model=os.environ["OLLAMA_LLM_MODEL"],
                base_url=os.environ["OLLAMA_URL"],
            )

        return llm

    def _load_prompt(self):
        from langchain import hub

        prompt = hub.pull("langchain-ai/react-agent-template")
        prompt = prompt.partial(instructions=self._load_instructions())

        return prompt

    def _load_instructions(self) -> str:

        prompt_path = os.path.join(".", "instructions.md")
        with open(prompt_path, "r", encoding="utf-8") as f:
            custom_prompt = f.read()

        print("Instruções do agente carregada com sucesso!")

        return custom_prompt

    def invoke(self, instruction: str) -> None:
        self.__agent_executor.invoke({"input": instruction})
