from typing import Optional, List
from langchain.callbacks.manager import (
    CallbackManagerForToolRun,
)
import os
from pydantic import BaseModel, Field

from langchain_core.tools.base import BaseTool

from schemas import CheckFileFileInput, UnzipFileInput


class CheckFileIsAlreadyUnziped(BaseTool):
    name: str = "CheckFileIsUnzip"
    description: str = (
        " Verifica ou checa se um determinado arquivo já foi descompactado anteriormente a partir de uma determinada pasta."
    )
    args_schema: type[BaseModel] = CheckFileFileInput
    return_direct: bool = False

    def _run(
        self,
        nome_arquivo: str,
        diretorio: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> bool:
        """Utiliza a ferramenta de forma síncrona."""
        print(
            f"Checando se o arquivo {nome_arquivo} já foi descompactado anteriormente a partir do diretório {diretorio}..."
        )

        file_count = 0
        for entry in os.listdir(diretorio):
            full_path = os.path.join(diretorio, entry)
            if os.path.isfile(full_path):
                file_count += 1

        return file_count > 1


class UnzipFileTool(BaseTool):
    name: str = "Unzip"
    description: str = (
        "Descompacta um determinado arquivo a partir de uma determinada pasta."
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

        print(f"Descomprimindo o arquivo {nome_arquivo} dentro da pasta {diretorio}...")

        full_path = os.path.join(diretorio, nome_arquivo)

        with zipfile.ZipFile(full_path, "r") as zip_ref:
            zip_ref.extractall(diretorio)

        directory_path = Path(diretorio)

        return [entry.name for entry in directory_path.iterdir() if entry.is_file()]
