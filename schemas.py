from typing import Optional, List

from pydantic import BaseModel, Field


class CheckFileFileInput(BaseModel):
    nome_arquivo: str = Field(
        description="O nome do arquivo a ser checado se existe ou não."
    )
    diretorio: str = Field(
        description="O nome da pasta onde o arquivo está localizado."
    )


class UnzipFileInput(BaseModel):
    nome_arquivo: str = Field(description="O nome do arquivo a ser descompactado.")
    diretorio: str = Field(
        description="O nome da pasta onde o arquivo está localizado."
    )
