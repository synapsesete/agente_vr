from agente_vr import AgenteVR

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)

def main():

    agente_vr = AgenteVR()
    agente_vr.invoke("Executar corretamente o que foi instruído a fazer.")


if __name__ == "__main__":
    main()
