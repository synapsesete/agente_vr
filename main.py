import logging

from agente_vr import AgenteVR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("debug.log"), logging.StreamHandler()],
)


def main():

    agente_vr = AgenteVR()
    agente_vr.invoke("Executar as instruções corretamente.")


if __name__ == "__main__":
    main()
