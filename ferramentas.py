import logging
import os
import sys
from typing import List, Optional

import pandas as pd
from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain_core.tools.base import BaseTool
from pydantic import BaseModel

import os
from dotenv import load_dotenv
load_dotenv()

from schemas import *

if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO

import openpyxl
from openpyxl.worksheet.worksheet import Worksheet

import excel

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

        diretorio_destino = os.environ['OUTPUT_FOLDER']

        logging.info(
            f"Descomprimindo o arquivo {nome_arquivo} localizado na pasta {diretorio} para o diretório destino {diretorio_destino}..."
        )

        full_path = os.path.join(diretorio, nome_arquivo)

        with zipfile.ZipFile(full_path, "r") as zip_ref:
            zip_ref.extractall(diretorio_destino)

        directory_destino_path = Path(diretorio_destino)

        paths_arquivos_descompactados = [
            os.path.join(diretorio_destino, entry.name)
            for entry in directory_destino_path.iterdir()
            if entry.is_file()
        ]

        logging.info(f"Os arquivos descompactados são: {paths_arquivos_descompactados}")

        return paths_arquivos_descompactados


class ReunirDadosTool(BaseTool):

    name: str = "ReunirDados"
    description: str = (
        "Reune ou concatena os dados de uma ou mais planilhas. Retorna o caminho da planilha em Excel cujos dados foram mesclados."
    )
    return_direct: bool = False
    args_schema: type[BaseModel] = ReunirDadosInput

    def _run(
        self,
        paths: list[str] | str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:

        if isinstance(paths, list):
            paths_planilhas_excel = paths
        else:
            paths_planilhas_excel = [_.strip() for _ in paths.split(",")]

        logger.info(
            f"Reunindo os dados oriundos das planilhas localizadas em {paths_planilhas_excel} (total de {len(paths_planilhas_excel)} arquivos) ..."
        )

        return excel.mesclar(
            paths_planilhas_excel,
            PlanilhaTemporaria().obter_caminho_arquivo_temporario("merged.xlsx"),
        )


class EstadosDosSindicatosTool(BaseTool):
    name: str = "EstadosDosSindicatos"
    description: str = (
        "A partir da planilha contendo os nomes dos sindicatos, obter o mapeamento dos estados correspondentes. Retorna o caminho da planilha contendo para cada sindicato, o estado correspondente"
    )
    return_direct: bool = False
    args_schema: type[BaseTool] = None

    def _run(
        self,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:

        sindicato_estados = {
            "SINDPD RJ - SINDICATO PROFISSIONAIS DE PROC DADOS DO RIO DE JANEIRO": "Rio de Janeiro",
            "SINDPPD RS - SINDICATO DOS TRAB. EM PROC. DE DADOS RIO GRANDE DO SUL": "Rio Grande do Sul",
            "SINDPD SP - SIND.TRAB.EM PROC DADOS E EMPR.EMPRESAS PROC DADOS ESTADO DE SP": "São Paulo",
            "SINDPD SP - SIND.TRAB.EM PROC DADOS E EMPR.EMPRESAS PROC DADOS ESTADO DE SP.": "São Paulo",
            "SITEPD PR - SIND DOS TRAB EM EMPR PRIVADAS DE PROC DE DADOS DE CURITIBA E REGIAO METROPOLITANA": "Paraná",
            "SINDPD RJ - SINDICATO PROFISSIONAIS DE PROC DADOS DO RIO DE JANEIRO": "Rio de Janeiro",
        }

        column_names = ["Sindicato", "Estado"]

        df_sindicato_vs_estado = pd.DataFrame(
            sindicato_estados.items(), columns=column_names
        )
        df_sindicato_vs_estado = df_sindicato_vs_estado.set_index("Sindicato")

        return PlanilhaTemporaria().exportar_dados_planilha_temporaria(
            df_sindicato_vs_estado, "sindicatos_x_estados.xlsx"
        )


class RemoverColaboradoresNaPlanilhaTool(BaseTool):
    name: str = "RemoverDadosNaPlanilha"
    description: str = (
        "Remove dados de colaboradores em função dos cargos enumerados."
    )
    return_direct: bool = False
    args_schema: type[BaseModel] = RemoverDadosNaPlanilhaInput

    def _run(
             self,
            path_planilha_dados_colaboradores: str,
            cargos: str,
            run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        
        cargos_list = cargos.split(',')
        logger.info("Removendo colaboradores da planilha %s em relação aos cargos %s...",path_planilha_dados_colaboradores,cargos_list)

        excel.remover_registros_planilha_por_valores_especificos_coluna(path_planilha_dados_colaboradores,'Cargo',cargos_list)
        excel.remover_registros_planilha_por_valores_especificos_coluna(path_planilha_dados_colaboradores,'Situação',cargos_list)


class EscreverDadosNaPlanilhaTool(BaseTool):
    name: str = "EscreverDadosNaPlanilha"
    description: str = (
        "Escreve ou copia os dados em uma planilha destino, completando a mesma."
    )
    return_direct: bool = True
    args_schema: type[BaseModel] = EscreverDadosNaPlanilhaInput

    def _run(
        self,
        path_origem: str,
        path_destino: str,
        competencia: str,
        percentual_custo_empresa: float,
        percentual_custo_empregado: float,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:

        logger.info(
            f"Exportando os dados oriundos da planilha {path_origem} para a planilha final em {path_destino} e competencia {competencia} com os percentuais de {percentual_custo_empresa}% para empresa e {percentual_custo_empregado}% para o empregado..."
        )

        excel.preencher_planilha(
            path_origem, path_destino, 1, 2, max_col_planilha_destino=6
        )

        wb_destino = openpyxl.load_workbook(path_destino)

        ws_destino = wb_destino.active

        wb_origem = openpyxl.load_workbook(path_origem)
        ws_origem = wb_origem.active

        # Preenche a compentência na coluna Competencia:

        num_primeira_linha_nao_preenchida = 4

        i = num_primeira_linha_nao_preenchida
        j = excel.buscar_indice_row_por_similaridade("Competencia", ws_destino[2])
        for row in ws_destino.iter_rows(min_row=num_primeira_linha_nao_preenchida):
            if row[0].value:
                ws_destino.cell(
                    row=i, column=j + 1, value=competencia.replace(".", "/")
                )
            i += 1

        assert j != None

        # Vamos definir a formula total:
        ws_destino["G1"].value = f"=SUM($G2:$G{ws_destino.max_row})"

        if percentual_custo_empresa > 1:
            percentual_custo_empresa /= 100.

        if percentual_custo_empregado > 1:
            percentual_custo_empregado /= 100.

        for row_num in range(3,ws_destino.max_row):
            ws_destino[f'G{row_num}'].value = f'=$E{row_num}*$F{row_num}'
            ws_destino[f'H{row_num}'].value = f'=$G{row_num}*{percentual_custo_empresa}'
            ws_destino[f'I{row_num}'].value = f'=$G{row_num}*{percentual_custo_empregado}'


        #Vamos remover todos os registros incompletos:
        indice_matricula = excel.buscar_indice_row_por_similaridade("Matricula", ws_destino[2]) + 1
        indice_sindicato = excel.buscar_indice_row_por_similaridade("Sindicato", ws_destino[2]) + 1
        for row_num in range(5,ws_destino.max_row):
            cadastro_value = ws_destino.cell(row=row_num,column=indice_matricula).value
            if cadastro_value==None:
                ws_destino.delete_rows(row_num,1)
            sindicato_value = ws_destino.cell(row=row_num,column=indice_sindicato).value
            logger.info("sindicato_value=%s",sindicato_value)
            if sindicato_value==None:
                ws_destino.delete_rows(row_num,1)

        excel.autofit(ws_destino)

        wb_destino.save(path_destino)

        logger.info(f"Planilha {path_destino} preenchida.")

        return path_destino


import atexit
import shutil
import tempfile


class PlanilhaTemporaria:

    def __init__(self):
        self.__temp_dir = tempfile.mkdtemp()
        atexit.register(self.__cleanup_function, "Closing files")

    def exportar_dados_planilha_temporaria(
        self, df: type[pd.DataFrame], filename: str
    ) -> str:
        excel_destino = os.path.join(self.obter_caminho_arquivo_temporario(filename))
        df.to_excel(excel_destino)
        logger.info(f"Os dados foram escritos com sucesso em {excel_destino}")
        return excel_destino

    def obter_caminho_arquivo_temporario(self, filename: str) -> str:
#        return  os.path.join('data/',filename)
        return os.path.join(self.__temp_dir, filename)

    def __cleanup_function(self, message):
        logger.info(message)
        try:
            shutil.rmtree(self.__temp_dir)
        except IOError:
            sys.stderr.write("Failed to clean up temp dir {}".format(self.__temp_dir))
