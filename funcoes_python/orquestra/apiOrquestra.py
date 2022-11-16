from gerais import printError
from time import sleep
from requests import get, post, Request
from pandas import DataFrame
from dateutil import parser
import datetime 

class ApiOrquestra():
    def __init__(self, 
                tokens:list, 
                metodoRequisicao:str, 
                urlApi:str="https://elysia.zeev.it", 
                tipoUrl:str="/api/2/assignments"):

        self.tokens = tokens
        self.metodoRequisicao = metodoRequisicao
        self.urlApi = urlApi
        self.tipoUrl = tipoUrl

    def __requisicao(self, 
                    metodo:str, 
                    urlAcesso:str, 
                    tipoAcesso:str, 
                    head:dict={}, 
                    payload:dict={}) -> (Request | int):
        '''
            Funcao
            ------
                Funcao que retorna a requisicao desejada a partir do url de acesso e link de tipo de acesso.
                !Sendo permitido apenas metodos POST e GET!

            Parameters
            ----------

                metodo: str, opcional
                    Metodo a ser utilizado na requisicao, POST ou GET.
                    Se nao for especificado nenhum ele ira utilizar o metodo 'GET'.
                
                urlAcesso: str, opcional
                    Url usada na requisicao.
                    Se nao for especificado nenhum ele ira utilizar o URL que ja esta no funcao.
                
                tipoAcesso: str (OPCIONAL)
                    Url de acesso para o tipo de funcao na API, POST ou GET.
                    Se nao for especificado nenhum ele ira utilizar o URL que ja esta no funcao.
                    Ex.: **/api/2/assignments**
                
                head: str, obrigatorio
                    Autorizacao para acesso da API.
                    Ex.: {'Authorization': 'token_acesso'}
                
                payload: str, opcional
                    Parametros para acesso atraves de filtros na requisicao.
            
            Retorno
            -------

                req : requests.Reponse
                    Retorna o objeto response ou resposta de erro caso ocorra.\n
                    Ex.: <Response [200]>

                int : integer
                    Retorna -1 caso erro.
        '''
        # verifica qual tipo de requisicao foi pedida
        try:
            if metodo == 'GET':
                req = get(url=urlAcesso+tipoAcesso,headers=head,params=payload)
                return req
            elif metodo == 'POST':
                req = post(url=urlAcesso+tipoAcesso,headers=head,params=payload)
                return req
            else: 
                raise NameError('Nenhum metodo valido foi passado. Passe os metodos POST ou GET.')
        except Exception as e:
            printError(e)
            return -1

    def requisicao_Orquestra(self, filters:dict={}, forceRequisition:bool=False) -> list:
        
            try:
                    # Variaveis de controle
                    row = 1
                    i = 1
                    retorno = []
                    # filtros base para o payload
                    if not self.tipoUrl.lower().__contains__('report'):
                            print(">> Requisicao normal...")
                            filters['recordsPerPage'] = 100
                            seconds = 1
                    else:
                            if not forceRequisition: 
                                    print(">> Requisicao lenta...")
                                    filters['recordsPerPage'] = 30
                                    seconds = 3
                            else:
                                    print(">> Requisicao forçada...")
                                    filters['recordsPerPage'] = 100
                                    seconds = 1    

                    # Faz a busca para cada token
                    for tk in self.tokens:
                            # Reseta variaveis de controle
                            row = 1
                            i = 1
                            # Iteracao com token
                            authorization= {'Authorization': "Bearer " + tk}
                            while row != 0:
                                    # Aguardo x segundos devido ao limite de requisicoes - lembrando que a limite de requisicoes por segundos, minutos, horas, dias e meses
                                    sleep(seconds) 
                                    
                                    # Incremento de pagina
                                    filters['pageNumber'] = i
                                    
                                    # Requisicao
                                    getReq = self.__requisicao(metodo=self.metodoRequisicao, 
                                                            urlAcesso=self.urlApi, 
                                                            tipoAcesso=self.tipoUrl, 
                                                            head=authorization, 
                                                            payload=filters)
                                    
                                    # Resultado JSON da requisicao
                                    result = getReq.json()
                                            
                                    # Checa se esta vazio o resultado, o que significa que nao tem mais paginas
                                    if (len(result) == 0) or (getReq.status_code != 200):
                                            print(">> {}".format(str(getReq.status_code)))
                                            break
                                    else:
                                            # coloca cada retorno na lista
                                            print(">> {}".format(str(getReq.status_code)))
                                            retorno.append(result)
                                            i+=1
                    # Cada usuario do token fica em uma sublista da lista de retorno, por isto a necessidade de 'explodir' ela dentro de outra lista.
                    retornoLista = [item for sublista in retorno for item in sublista]
                    return retornoLista 
            except Exception as e:
                    print('--> Erro na funcao \'requisicao_Orquestra\' <--')
                    printError(e)
                    return []

    def requisicao_Intancias_Orquestra(self, 
                                       showFinishedInstanceTasks:bool=True, 
                                       showPendingInstanceTasks:bool=False, 
                                       activeInstances:bool=True, 
                                       forceReq:bool=False, 
                                       flowId:str='') -> (DataFrame | int):
        '''
            Funcao
            ------
                Funcao especifica para listas todas instâncias de solicitações que a pessoa relacionada ao token possui permissão de consultar de acordo com filtros.
            
            Parametros
            ----------
                
                Parametros de especial atencao:
                -------------------------------

                `showFinishedTasks` : boolean, (opcional)
                    Define se vai requisitar instancias fechadas das solicitacoes.
                
                `showPendingInstanceTasks` : boolean, (opcional)
                    Define se vai requisitar instancias abertas das solicitacoes.

                * Se nao optar por `showPendingInstanceTasks` ou `showFinishedTasks`, sera necessario colocar o parametro `forceReq` como `True`.\n
                * Se `showPendingInstanceTasks` ou `showFinishedTasks` estiverem `True` o parametro `forceReq` eh alterado para `False`, mesmo se ele for passado pela funcao.
                
                forceReq : boolean, (opcional)
                    Este parametro limita a quantidade de solicitacoes por segundo.

                activeInstances : boolean, (opcional)
                    Definir se a solicitacao esta `Finalizada` ou `Em andamento`.

                flowId : str, (opcional)
                    Filtrar pelo id de instancia.
            Retorno 
            -------
                Retorna um DataFrame(Pandas).
                * Se erro, retorna -1.
        '''
        try:
            # Filtro padrao - Solicitacoes Em andamento e com instancias Finalizadas
            f = {"startDateIntervalBegin": "2000-01-01T00:00:00",
                    "startDateIntervalEnd": "2030-12-31T23:59:59",
                    "showFinishedInstanceTasks": showFinishedInstanceTasks, 
                    "showPendingInstanceTasks": showPendingInstanceTasks,
                    "active": activeInstances}
                    
            # Filtro de ID para solicitacoes especificas
            if flowId != '': 
                f['flowId'] = flowId

            if showFinishedInstanceTasks == True | showPendingInstanceTasks == True:
                forceReq = False

            # Requisicao 
            lista = self.requisicao_Orquestra(filters=f, forceRequisition=forceReq)
            df = DataFrame(lista)
            return df
        except Exception as e:
            print('--> Erro na funcao \'instances_Report_Orquestra\' <--')
            printError(e)
            return DataFrame()

    def contagem_Instancias_Orquestra(nomeSolicitacao:str, nomeTarefa:str,per1:datetime,per2:datetime,dataFrame:DataFrame, status:str='endDateTime') -> int:
        '''
        Funcao
        ------
                Retorna a contagem de tarefas fechadas ou abertas para determinada solicitacao em um determinado periodo.

        Parameters
        ----------
            nomeSolicitacao: str (obrigatorio)
                Nome da solicitacao que sera buscada e contada a instancia.
            
            nomeTarefa: str (obrigatorio)
                Nome da tarefa para ser contada a sua quantidade.

            dataFrame: dataFrame Pandas (obrigatorio)
                Dataframe que sera utilizado como base de dados para a contagem.
            
            per1: datetime (obrigatorio)
                Periodo inicial para busca.

            per2: datetime (obrigatorio)
                Periodo final para busca.

            status: str (opcional)
                Status da data para verificar o periodo - podendo ser `endDateTime` ou `startDateTime`.
        Retorno
        -------
            int: Retorna a quantidade de instancias ja finalizadas desta tarefa.
            * Se erro, retorna -1   
        '''
        try:
            # Formatar parametros - remove espacos em branco, deixar em letra minuscula
            nomeSolicitacao = str(nomeSolicitacao).lower().replace(" ","")
            nomeTarefa = str(nomeTarefa).lower()
            # Projetos 
            projetos = dataFrame.loc[(dataFrame['requestName'].str.lower().str.replace(" ","").str.contains(nomeSolicitacao))]
            # Contagem
            cont=0
            # Percorre linha a linha do dataframe, verificando cada instancia aberta ou fechada da solicitacao 
            for row in projetos.values:
                for instance in row[19]:
                    task = str(instance['task']['name']) 
                    date = parser.parse(instance[status]).strftime("%Y-%m-%d")
                    if task.lower().__contains__(nomeTarefa):
                        if date >= per1 and date <= per2:
                            cont+=1
            return cont
        except Exception as e:
            print('--> Erro na funcao \'contagem_Instancias_Orquestra\' <--')
            printError(e)
            return -1

    # Getters e Setters
    def set_Tokens(self, tokens:list):
        self.tokens = tokens

    def set_MetodoRequisicao(self, metodoRequisicao:str):
        self.metodoRequisicao = metodoRequisicao
    
    def set_UrlApi(self, urlApi:str):
        self.urlApi = urlApi
    
    def set_TipoUrl(self, tipoUrl:str):
        self.tipoUrl = tipoUrl

    def get_Tokens(self):
        return self.tokens 

    def get_MetodoRequisicao(self):
        return self.metodoRequisicao 
    
    def get_UrlApi(self):
        return self.urlApi 
    
    def get_TipoUrl(self):
        return self.tipoUrl 