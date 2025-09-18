from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field, ConfigDict


class UnzipFileInput(BaseModel):
    nome_arquivo: str = Field(description="O nome do arquivo a ser descompactado.")
    diretorio: str = Field(
        description="O nome da pasta onde o arquivo está localizado."
    )

class ReunirDadosInput(BaseModel):
    paths: list[str] | str = Field(description="os caminhos dos arquivos das planilhas que serão reunidos ou mesclados.")

class ObterDadosInput(BaseModel):
    path: str = Field(description="o caminho do arquivo da planilha cujos dados deseja-se obter.")

class ExtrairDadosColunasInput(BaseModel):
    path: str = Field(description="o caminho do arquivo da planilha cujas colunas deseja-se extrair.")
    nomes_colunas: list[str] | str = Field(description="Os nomes das colunas na planilha cujos dados deseja-se extrair.")

class EscreverDadosNaPlanilhaInput(BaseModel):
    path_origem: str = Field(description="O caminho do arquivo da planilha de origem cujos dados serão copiados para a planilha de destino.")
    path_destino: str = Field(description="O caminho do arquivo da planilha cujos dados serão preenchidos ou completados.")
    competencia: str = Field(description="A competência dos dados em mes e ano.")
#    nome_aba_planilha_destino: Optional[str] = Field(description="O nome da aba da planilha de destino (opcional).")

class CalcularQuantidadeDiasUteisInput(BaseModel):
    paths: list[str] | str = Field(description="os caminhos dos arquivos das planilhas cujos colaboradores terão seu dias úteis calculados.")
    dias_uteis_por_sindicato: dict[str,str] | str = Field(description="um relacionamento entre o nome do sindicato e os dias úteis correspondente.")