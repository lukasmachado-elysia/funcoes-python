import pyodbc

class Banco:
    def __init__(self, server:str, user:str, password:str, dataBaseName:str):
        self.server = server
        self.user = user 
        self.password = password
        self.dataBaseName = dataBaseName

    # faz a conexao com o SQL Server e consulta a um banco de dados 
    def conexao_Banco(self) -> (pyodbc.Connection | str):
        """
            Funcao que faz conexao com o banco de dados do tipo: `ODBC Driver 18 for SQL Server.`\n
            Retorna a conexao com o banco.

            Exemplo de Codigo
            --------------
            Exemplo::
            
                    # pegando acesso do banco
                    db = Banco(server='nomeServidor,porta', user='usuarioServidor', password='senha', dataBaseName='nomeBanco')
                    conn = db.conexaoBanco()

                    # pegando o nome de todos os colaboradores
                    cursor = conn.cursor()
                    cursor.execute("select * from vendedores;")
                    column = cursor.fetchone()
                    
                    # printando nome de todos
                    while column:
                        print(column[1])
                        column = cursor.fetchone()

            Retorno
            -------
                obj : pyodbc.Connection
                    Retorna a conexao com o banco.
                obj : str
                    Retorna string em caso de erro.

        """
        instancia = 'DRIVER={ODBC Driver 18 for SQL Server};' +'SERVER=' + self.server + ';' + 'DATABASE=' + self.dataBaseName + ';' + 'TrustServerCertificate=YES;' +  'UID=' + self.user + ';' + 'PWD=' + self.password + ';'
        
        #print(f'Instancia de conexao: {instancia}')
        try:
            conn = pyodbc.connect(instancia)
            print('\n------------------------------------') 
            print(' Conexao estabelecida com sucesso!')
            print('------------------------------------\n') 
            return conn
        except Exception as e:
            print('\n------------------------------------') 
            print('Nao foi possível realizar a conexao!')
            print('------------------------------------\n') 

            templateError = '!!! ---> Um erro do tipo: "{0}" ocorreu <--- !!!\nArgumentos:\n{1}'
            messageError = templateError.format(type(e).__name__,e.args)
            print(messageError)

            return messageError
    