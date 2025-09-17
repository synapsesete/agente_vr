from typing import Optional, List
from unittest.mock import Base
from langchain.callbacks.manager import (
    CallbackManagerForToolRun,
)
import os
from pydantic import BaseModel, Field

from langchain_core.tools.base import BaseTool

from schemas import *

import pandas as pd

import logging

import sys
if sys.version_info[0] < 3: 
    from StringIO import StringIO
else:
    from io import StringIO

import csv
import openpyxl 
from openpyxl.worksheet.worksheet import Worksheet

logger = logging.getLogger(__name__)

class UnzipFileTool(BaseTool):
    name: str = "Unzip"
    description: str = (
        """
            Descompacta um determinado arquivo a partir de uma determinada pasta. 
            Retorna uma lista contendo os caminhos dos arquivos descompactados.
        """
    )
    args_schema: type[BaseModel] = UnzipFileInput
    return_direct: bool = False

    def _run(
        self,
        nome_arquivo: str,
        diretorio: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> List[str]:
        """Utiliza a ferramenta de forma síncrona."""
        import zipfile
        from pathlib import Path

        logging.info(f"Descomprimindo o arquivo {nome_arquivo} dentro da pasta {diretorio}...")

        full_path = os.path.join(diretorio, nome_arquivo)

        with zipfile.ZipFile(full_path, "r") as zip_ref:
            zip_ref.extractall(diretorio)

        directory_path = Path(diretorio)

        paths_arquivos_descompactados = [os.path.join(diretorio,entry.name) for entry in directory_path.iterdir() if entry.is_file()]

        logging.info(f"Os arquivos descompactados são: {paths_arquivos_descompactados}")

        return paths_arquivos_descompactados
    


class ReunirDadosTool(BaseTool):

    name: str = "ReunirDados"
    description: str = "Reune ou concatena os dados de uma ou mais planilhas. Retorna o caminho da planilha em Excel cujos dados foram mesclados."
    return_direct: bool = False
    args_schema: type[BaseModel] = ReunirDadosInput

    def _run(self,
        paths: list[str] | str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        
        if isinstance(paths,list):
            paths_planilhas_excel = paths
        else:
            paths_planilhas_excel = [ _.strip() for _ in paths.split(",")]
        
        logger.info(f"Reunindo os dados oriundos das planilhas localizadas em {paths_planilhas_excel} (total de {len(paths_planilhas_excel)} arquivos) ...")

        dfs = []

        for path_planilha_excel in paths_planilhas_excel:
            df = pd.read_excel(path_planilha_excel,index_col=0)
            dfs.append(df)

        assert len(dfs) == len(paths_planilhas_excel)

        dados_concatenados = pd.concat(dfs,axis=1)

        logging.info(dados_concatenados.head())

        planilha_temporaria = PlanilhaTemporaria()

        return planilha_temporaria.exportar_dados_planilha_temporaria(dados_concatenados)
    

class ExtrairDadosColunasTool(BaseTool):
    name: str = "ExtrairDadosColunas"
    description: str = "Extrai ou obtém os dados das colunas de uma determinada planilha. Retorna o caminho da planilha em Excel cujos dados das colunas foram extraídos."
    return_direct: bool = False
    args_schema: type[BaseModel] = ExtrairDadosColunasInput

    def _run(self,
             path: str,
             nomes_colunas: list[str] | str,
            run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        
        if isinstance(nomes_colunas,list):
            colunas_filtradas = nomes_colunas
        else:
            colunas_filtradas = [ _.strip() for _ in nomes_colunas.split(",")]

        logger.info(f"Extraindo os dados das colunas {colunas_filtradas} da planilha {path}...")

        df = pd.read_excel(path,index_col=0)

        df = df[colunas_filtradas]

        df.to_excel(path)

        return path



class ObterDadosTool(BaseTool):
    name: str = "ObterDados"
    description: str = "Obtem os dados de uma planilha determinada. Retorna o numero de linhas que esta planilha possui."
    return_direct: bool = False
    args_schema: type[BaseModel] = ObterDadosInput

    def _run(self,
        path: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> int:
        
        logger.info(f"Obtendo os dados da planilha {path} ...")

        dados = pd.read_excel(path)

        logger.info(f"Total de linhas: {dados.shape[0]}")

        return dados.shape[0]


class EscreverDadosNaPlanilhaTool(BaseTool):
    name: str = "EscreverDadosNaPlanilhaTool"
    description: str = "Escreve ou copia os dados em uma planilha destino, completando a mesma."
    return_direct: bool = True
    args_schema: type[BaseModel] = EscreverDadosNaPlanilhaInput

    def _run(
        self,
        path_origem: str,
        path_destino: str,
#        nome_aba_planilha_destino: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:

        logger.info(f"Exportando os dados oriundos da planilha {path_origem} para a planilha final em {path_destino}...")

        wb_destino = openpyxl.load_workbook(path_destino)

        ws_destino = wb_destino.active
        i = self.__index_first_empty_row(ws_destino)

        wb_origem = openpyxl.load_workbook(path_origem)
        ws_origem = wb_origem.active

        for row in ws_origem.iter_rows(min_row=2):
            j = 1
            for cell in row:            
                ws_destino.cell(row=i,column=j,value=cell.value)
                j += 1
            i += 1

        wb_destino.save(path_destino)

        return path_destino


    def __index_first_empty_row(self,ws: type[Worksheet]) -> int:
        for row_index in range(1, ws.max_row + 2):  # Iterate up to one row beyond max_row
            is_empty = True
            for col_index in range(1, ws.max_column + 1):
                cell_value = ws.cell(row=row_index, column=col_index).value
                if cell_value is not None:
                    is_empty = False
                    break  # Found a non-empty cell in this row, so it's not empty
            if is_empty:
                return row_index

import tempfile
import shutil
import atexit
class PlanilhaTemporaria:
    
    def __init__(self):
        self.__temp_dir = tempfile.mkdtemp()
        atexit.register(self.__cleanup_function, "Closing files")

    def exportar_dados_planilha_temporaria(self,df: type[pd.DataFrame]) -> str:
        excel_destino =  os.path.join(self.__temp_dir,"output.xlsx")
        df.to_excel(excel_destino)
        logger.info(f"Os dados foram escritos com sucesso em {excel_destino}")
        return excel_destino    

    def __cleanup_function(self,message):
        logger.info(message)
        try:
            shutil.rmtree(self.__temp_dir)
        except IOError:
            sys.stderr.write('Failed to clean up temp dir {}'.format(self.__temp_dir))

