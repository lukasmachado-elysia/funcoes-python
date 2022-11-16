from orquestra import apiOrquestra
import pandas as pd
def main():
    api = apiOrquestra.ApiOrquestra(tokens=['3Lzf1s6YuSVLM%2Bz%2FxAEaXUgeiX8UZUW4TpQz8Dkf9KQDX4yLt5mN997v9KtsYbua'],metodoRequisicao='GET')
    req = api.requisicao_Orquestra()
    df = pd.DataFrame(req)
    print(api.get_MetodoRequisicao())
    print(df)
if __name__ == "__main__":
    main()

