import tkinter
from tkinter import ttk
from tkinter import messagebox 
from tkinter import Menu 
import sqlite3

janela = tkinter.Tk()

class funcs():
    def limpa_todas_as_entrys(self):
        for entry in self.lista_entrys:
            entry.delete(0, tkinter.END)
        self.partida_text.delete(1.0, tkinter.END)  # Limpa o widget de texto também

    def conecta_bd(self):
        self.conn = sqlite3.connect("partidas.bd")
        self.cursor = self.conn.cursor()
        print("conectando ao banco de dados")

    def desconecta_bd(self):
        self.conn.close()
        print("desconectado do banco de dados")

    def montaTabelas(self):
        self.conecta_bd()
        # criar tabela com nova coluna "Partida"
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS partidas (
                cod INTEGER PRIMARY KEY,
                Evento TEXT,
                Local_do_jogo TEXT,
                Data TEXT,
                Rodada TEXT,
                Brancas TEXT,
                Pretas TEXT,
                Resultado TEXT,
                Controle_tempo TEXT,
                Codigo_ECO TEXT,
                Abertura TEXT,
                Rating_Brancas INTEGER,
                Rating_Pretas INTEGER,
                Titulo_Brancas TEXT,
                Titulo_Pretas TEXT,
                Terminacao TEXT,
                Tabuleiro TEXT,
                Partida TEXT
            )
        """)
        self.conn.commit()
        print("banco de dados criado")
        self.desconecta_bd()

    def add_partida(self):
        self.conecta_bd()
        dados = [entry.get() for entry in self.lista_entrys]
        # Adiciona o conteúdo do widget de texto (Partida)
        dados.append(self.partida_text.get(1.0, tkinter.END).strip())
        
        self.cursor.execute("""
            INSERT INTO partidas (
                Evento, Local_do_jogo, Data, Rodada, Brancas, Pretas,
                Resultado, Controle_tempo, Codigo_ECO, Abertura,
                Rating_Brancas, Rating_Pretas, Titulo_Brancas, Titulo_Pretas,
                Terminacao, Tabuleiro, Partida
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, dados)
        self.conn.commit()
        print("Partida inserida no banco de dados")
        self.desconecta_bd()
        self.select_lista()
        self.limpa_todas_as_entrys()

    def select_lista(self):
        self.listaPar.delete(*self.listaPar.get_children())
        self.conecta_bd()
        lista = self.cursor.execute("""
            SELECT 
                cod, Evento, Local_do_jogo, Data, Rodada, Brancas, Pretas,
                Resultado, Controle_tempo, Codigo_ECO, Abertura,
                Rating_Brancas, Rating_Pretas, Titulo_Brancas, Titulo_Pretas,
                Terminacao, Tabuleiro, Partida
            FROM partidas
            ORDER BY Evento ASC;
        """)
        for i in lista:
            # Mostra todas as colunas incluindo a Partida
            self.listaPar.insert("", tkinter.END, values=i[1:], iid=i[0])
        self.desconecta_bd()

    def alterar_partida(self):
        selecionado = self.listaPar.focus()
        if not selecionado:
            print("Nenhuma partida selecionada para alterar")
            return

        # Pega os dados atuais dos Entrys e do Text
        dados = [entry.get() for entry in self.lista_entrys]
        dados.append(self.partida_text.get(1.0, tkinter.END).strip())
        
        # Conecta ao banco
        self.conecta_bd()
        
        # Atualiza no banco de dados usando o cod da linha selecionada
        self.cursor.execute("""
            UPDATE partidas
            SET Evento = ?, Local_do_jogo = ?, Data = ?, Rodada = ?, Brancas = ?, Pretas = ?,
                Resultado = ?, Controle_tempo = ?, Codigo_ECO = ?, Abertura = ?,
                Rating_Brancas = ?, Rating_Pretas = ?, Titulo_Brancas = ?, Titulo_Pretas = ?,
                Terminacao = ?, Tabuleiro = ?, Partida = ?
            WHERE cod = ?
        """, (*dados, selecionado))
        
        self.conn.commit()
        print("Partida alterada com sucesso")
        self.desconecta_bd()
        
        # Atualiza a Treeview
        self.select_lista()
        self.limpa_todas_as_entrys()

    def apagar_partida(self):
        selecionado = self.listaPar.focus()
        if not selecionado:
            print("Nenhuma partida selecionada para apagar")
            return

        # Confirmação opcional
        resposta = tkinter.messagebox.askyesno("Confirmação", "Deseja realmente apagar a partida selecionada?")
        if not resposta:
            return

        # Conecta ao banco e apaga a linha
        self.conecta_bd()
        self.cursor.execute("DELETE FROM partidas WHERE cod = ?", (selecionado,))
        self.conn.commit()
        print("Partida apagada com sucesso")
        self.desconecta_bd()

        # Atualiza a Treeview e limpa os campos
        self.select_lista()
        self.limpa_todas_as_entrys()

    def buscar_partida(self):
        # Obtém os valores das entrys (campos preenchidos)
        busca = [entry.get().strip().lower() for entry in self.lista_entrys]

        # Percorre todas as linhas da Treeview
        encontrado = False
        for iid in self.listaPar.get_children():
            valores = self.listaPar.item(iid, "values")
            # Compara apenas os campos preenchidos
            match = True
            for i, valor in enumerate(busca):
                if valor and valores[i].lower() != valor:
                    match = False
                    break
            if match:
                # Seleciona e foca no item encontrado
                self.listaPar.selection_set(iid)
                self.listaPar.focus(iid)
                self.listaPar.see(iid)
                self.mostrar_dados_selecionados(None)
                encontrado = True
                break

        if not encontrado:
            print("Nenhuma partida encontrada com os critérios informados.")

    def ordenar_treeview(self, coluna, reverso=False):
        # Obtém todos os itens da treeview
        itens = [(self.listaPar.set(iid, coluna), iid) for iid in self.listaPar.get_children('')]

        # Tenta converter para número, se possível
        try:
            itens = [(float(valor), iid) for valor, iid in itens]
        except ValueError:
            pass

        # Ordena os itens
        itens.sort(reverse=reverso)

        # Reorganiza na treeview
        for index, (valor, iid) in enumerate(itens):
            self.listaPar.move(iid, '', index)

        # Atualiza o cabeçalho para permitir ordenar reverso no próximo clique
        self.listaPar.heading(coluna, command=lambda: self.ordenar_treeview(coluna, not reverso))


class Aplicacao(funcs):
    def __init__(self):
        self.janela = janela
        self.tela()
        self.frams_da_tela()
        self.montaTabelas()
        self.widgetsF1()
        self.lista_frame2()
        self.select_lista()
        self.Menus()
        janela.mainloop()


    def tela(self):
        self.janela.title("Clube de Xadrez do Méier")
        self.janela.configure(background="lightblue")
        self.janela.geometry("1200x600")  # Tamanho aumentado para acomodar todas as colunas
        self.janela.resizable(True, True)
        self.janela.minsize(width=1200, height=600)

    def frams_da_tela(self):
        self.frame_1 = tkinter.Frame(self.janela, bd=4, bg="white", highlightbackground="black", highlightthickness=3)
        self.frame_1.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.46)
        self.frame_2 = tkinter.Frame(self.janela, bd=4, bg="white", highlightbackground="black", highlightthickness=3)
        self.frame_2.place(relx=0.02, rely=0.5, relwidth=0.96, relheight=0.46)

    def widgetsF1(self):
        # Cria um canvas e scrollbar para o lado esquerdo (campos do formulário)
        left_canvas = tkinter.Canvas(self.frame_1, bg="white")
        left_canvas.place(relx=0, rely=0, relwidth=0.5, relheight=1)
        
        left_scrollbar = tkinter.Scrollbar(self.frame_1, orient="vertical", command=left_canvas.yview)
        left_scrollbar.place(relx=0.5, rely=0, relheight=1, width=15)
        
        left_canvas.configure(yscrollcommand=left_scrollbar.set)
        
        self.left_frame = tkinter.Frame(left_canvas, bg="white")
        left_canvas.create_window((0, 0), window=self.left_frame, anchor="nw")
        
        # Botões
        botoes = [("Limpar", self.limpa_todas_as_entrys),
                  ("Buscar", self.buscar_partida),
                  ("Novo", self.add_partida),
                  ("Alterar", self.alterar_partida),
                  ("Apagar", self.apagar_partida)]
        for i, (texto, cmd) in enumerate(botoes):
            btn = tkinter.Button(self.left_frame, text=texto, command=cmd)
            btn.grid(row=0, column=i, padx=5, pady=5, sticky="ew")

        # Labels + Entrys
        campos = [
            "Evento", "Local do jogo", "Data", "Rodada", "Brancas", "Pretas",
            "Resultado", "Controle de tempo", "Código ECO", "Abertura",
            "Rating Brancas", "Rating Pretas", "Título Brancas", "Título Pretas",
            "Terminação", "Tabuleiro"
        ]

        self.lista_entrys = []

        for i, campo in enumerate(campos, start=1):
            lbl = tkinter.Label(self.left_frame, text=campo)
            lbl.grid(row=i, column=0, padx=5, pady=5, sticky="w")
            
            entry = tkinter.Entry(self.left_frame, width=30)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            
            self.lista_entrys.append(entry)

        self.left_frame.grid_columnconfigure(1, weight=1)
        
        # Atualiza a região de scroll quando o left_frame muda de tamanho
        def configure_left_scrollregion(event):
            left_canvas.configure(scrollregion=left_canvas.bbox("all"))
        self.left_frame.bind("<Configure>", configure_left_scrollregion)

        # Lado direito - widget de texto para Partida
        right_frame = tkinter.Frame(self.frame_1, bg="white")
        right_frame.place(relx=0.52, rely=0, relwidth=0.47, relheight=1)
        
        lbl_partida = tkinter.Label(right_frame, text="Partida (PGN)")
        lbl_partida.pack(pady=(5, 0))
        
        self.partida_text = tkinter.Text(right_frame, wrap=tkinter.WORD)
        self.partida_text.pack(fill=tkinter.BOTH, expand=True, padx=5, pady=5)
        
        scroll_text = tkinter.Scrollbar(right_frame, command=self.partida_text.yview)
        scroll_text.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.partida_text.configure(yscrollcommand=scroll_text.set)

    def lista_frame2(self):
        # Mantém TODAS as colunas originais na treeview
        campos = [
            "Evento", "Local do jogo", "Data", "Rodada", "Brancas", "Pretas",
            "Resultado", "Controle de tempo", "Código ECO", "Abertura",
            "Rating Brancas", "Rating Pretas", "Título Brancas", "Título Pretas",
            "Terminação", "Tabuleiro", "Partida"
        ]
        
        self.listaPar = ttk.Treeview(self.frame_2, columns=campos, show='headings')
        
        # Define larguras das colunas (ajustadas para caber melhor)
        column_widths = {
            "Evento": 120, "Local do jogo": 100, "Data": 80, "Rodada": 60, 
            "Brancas": 100, "Pretas": 100, "Resultado": 70,
            "Controle de tempo": 100, "Código ECO": 80, "Abertura": 100,
            "Rating Brancas": 90, "Rating Pretas": 90, 
            "Título Brancas": 90, "Título Pretas": 90,
            "Terminação": 80, "Tabuleiro": 80, "Partida": 150
        }
        
        for campo in campos:
            self.listaPar.heading(campo, text=campo,
                                command=lambda c=campo: self.ordenar_treeview(c))
            self.listaPar.column(campo, width=column_widths.get(campo, 100))

        
        # Empacota a treeview com scrollbars
        h_scrollbar = ttk.Scrollbar(self.frame_2, orient="horizontal", command=self.listaPar.xview)
        v_scrollbar = ttk.Scrollbar(self.frame_2, orient="vertical", command=self.listaPar.yview)
        
        self.listaPar.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        
        self.listaPar.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        self.frame_2.grid_rowconfigure(0, weight=1)
        self.frame_2.grid_columnconfigure(0, weight=1)
        
        # Vincula evento de seleção - AGORA VAI FUNCIONAR!
        self.listaPar.bind("<<TreeviewSelect>>", self.mostrar_dados_selecionados)

    def mostrar_dados_selecionados(self, event):
        selecionado = self.listaPar.focus()
        if selecionado:
            # Obtém todos os valores da linha selecionada
            valores = self.listaPar.item(selecionado, 'values')
            
            if valores:
                # Limpa todos os campos primeiro
                self.limpa_todas_as_entrys()
                
                # Preenche os campos de entrada (os primeiros 16 valores)
                for i in range(min(len(valores) - 1, len(self.lista_entrys))):
                    self.lista_entrys[i].insert(0, valores[i] if valores[i] else "")
                
                # Preenche o widget de texto com a partida (último valor)
                if len(valores) > 16:
                    self.partida_text.delete(1.0, tkinter.END)
                    self.partida_text.insert(tkinter.END, valores[16])

    def Menus(self):
        menubar = Menu(self.janela)
        self.janela.config(menu= menubar)
        filemenu = Menu(menubar)
        filemenu2 = Menu(menubar)

        menubar.add_cascade(label = "Opções", menu= filemenu)
        menubar.add_cascade(label = "sobre", menu= filemenu2)

        filemenu.add_command(label = "sair")
        filemenu2.add_command(label = "limpa cliente")



Aplicacao()
