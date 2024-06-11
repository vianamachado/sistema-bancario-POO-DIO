import textwrap
from abc import ABC, abstractclassmethod, abstractproperty

class Usuario:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)
    
class Pessoa_Fisica(Usuario):
    def __init__(self, nome, data_de_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_de_nascimento = data_de_nascimento
        self.cpf = cpf

class Conta:
    def __init__(self, numero, usuario):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._usuario = usuario
        self.historico = Historico()
    
    @classmethod
    def nova_conta(cls, numero, usuario):
        return cls(numero, usuario)
    
    @property
    def saldo(self):
        return self._saldo
    
    @property
    def numero(self):
        return self._numero
    
    @property
    def agencia(self):
        return self._agencia
    
    @property
    def usuario(self):
        return self._usuario

    @property
    def historico(self):
        return self._historico
    
    def sacar(self, valor):
        saldo = self.saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
            print("Operação cancelada pois o saldo em conta é insuficiente!")

        elif valor > 0:
            self._saldo -= valor
            print("Saque realizado com sucesso!")
            return True
        
        else:
            print("Operação cancelada pois o valor informado é inválido!")

        return False
    
    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("Depósito realizado com sucesso!")

        else:
            print("Operação cancelada pois o valor informado é inválido!")
            return  False
        
        return True

class Conta_Corrente(Conta):
    def __init__(self, numero, usuario, limite=500, limite_saques=3):
        super().__init__(numero, usuario)
        self.limite = limite
        self.limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len([transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__])

        excedeu_limite = valor > self.limite
        excedeu_saques = numero_saques > self.limite_saques

        if excedeu_limite:
            print("Operação cancelada pois o valor do saque excede o limite disponível!")       

        elif excedeu_saques:
            print("Operação cancelada pois o número de saques disponíveis foi atingido!")

        else:
            return super().sacar(valor)

        return False

    def __str__(self):
        return f"""Agência: {self.agencia}
                   Conta Corrente: {self.numero}
                   Titular: {self.usuario.nome}"""

class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes
    
    def adicionar_transacao(self, transacao):
        self._transacoes.append({
            "tipo": transacao.__class__.__name__,
            "valor": transacao.valor,
        })
        
class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass

    @abstractclassmethod
    def registrar(self, conta):
        pass

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor
    
    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

def menu():
    menu = """\n
    [1] depositar
    [2] sacar
    [3] extrato
    [4] nova conta
    [5] listar contas
    [6] novo usuário
    [7] sair
    -> """
    return input(textwrap.dedent(menu))

def filtrar_usuario(cpf, usuarios):
    usuarios_filtrados = [usuario for usuario in usuarios if usuario.cpf == cpf]
    return usuarios_filtrados[0] if usuarios_filtrados else None

def recuperar_conta_usuario(usuario):
    if not usuario.contas:
        print("Cliente não localizado no sistema.")
        return

    return usuario.contas[0]

def depositar(usuarios):
    cpf = input("Informe seu CPF: ")
    usuario = filtrar_usuario(cpf, usuarios)

    if not usuario:
        print("Cliente não localizado no sistema.")
        return

    valor = float(input("Informe o valor do depósito a ser realizado: "))
    transacao = Deposito(valor)

    conta = recuperar_conta_usuario(usuario)
    if not conta:
        return

    usuario.realizar_transacao(conta, transacao)

def sacar(usuarios):
    cpf = input("Informe o seu CPF: ")
    usuario = filtrar_usuario(cpf, usuarios)

    if not usuario:
        print("Cliente não localizado no sistema.")
        return

    valor = float(input("Informe o valor do saque desejado: "))
    transacao = Saque(valor)

    conta = recuperar_conta_usuario(usuario)
    if not conta:
        return

    usuario.realizar_transacao(conta, transacao)

def exibir_extrato(usuarios):
    cpf = input("Informe seu CPF: ")
    usuario = filtrar_usuario(cpf, usuarios)

    if not usuario:
        print("Cliente não localizado no sistema.")
        return
    
    conta = recuperar_conta_usuario(usuario)
    if not conta:
        return
    
    print("EXTRATO")
    transacoes = conta.historico.transacoes

    extrato = ""
    if not transacoes:
        extrato = "Não foram realizadas movimentações nesta conta."

    else:
        for transacao in transacoes:
            extrato += f"{transacao["tipo"]}: R$: {transacao["valor"]:.2f}"

    print(extrato)
    print(f"Saldo: R$ {conta.saldo:.2f}")

    print("EXTRATO")
    print("não foram realizadas movimentações nesta conta!" if not extrato else extrato)
    print(f"Saldo: R$ {conta.saldo:.2f}")

def criar_usuario(usuarios):
    cpf = input("Informe seu CPF: ")
    usuario = filtrar_usuario(cpf, usuarios)

    if usuario:
        print("Já existe um cliente cadastrado sob esse CPF!")
        return

    nome = input("Informe o nome completo: ")
    data_de_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço (logradouro, número, bairro, cidade/UF): ")

    usuario = Pessoa_Fisica(nome=nome, data_de_nascimento=data_de_nascimento, cpf=cpf, endereco=endereco)
    usuario.append(usuario)

    print("Cliente acadastrado com sucesso em nosso sistema!")

def criar_conta(numero_da_conta, usuarios, contas):
    cpf = input("Informe seu CPF: ")
    usuario = filtrar_usuario(cpf, usuarios)

    if not usuario:
        print("Cliente não localizado em nosso sistema")
        return

    conta = Conta_Corrente.nova_conta(usuario=usuario, numero_da_conta=numero_da_conta)
    contas.append(conta)
    usuario.contas.append(conta)

    print("Conta criada com sucesso!")
 
def listar_contas(contas):
    for conta in contas:
        print(textwrap.dedent(str(conta)))

def main():
    usuarios = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "1":
            depositar(usuarios)

        elif opcao == "2":
            sacar(usuarios)

        elif opcao == "3":
            exibir_extrato(usuarios)

        elif opcao == "6":
            criar_usuario(usuarios)

        elif opcao == "4":
            numero_da_conta = len(contas) + 1
            conta = criar_conta(numero_da_conta, usuarios, contas)

            if conta:
                contas.append(conta)

        elif opcao == "5":
            listar_contas(contas)

        elif opcao == "7":
            break

        else:
            print("Operação inválida. Retorne ao menu e selcione uma opção válida!")

main()
