#Importando bibliotecas
import sys
import pandas as pd
import numpy as np
import streamlit as st
import time
import urllib
import reverse_geocode

sys.path.append('libs')
from felipe import verificaTaxonomia

class app_hub():

	#Atributos da classe app_hub:
	dicionario = ['Exe. 1: Valores vazios','Exe. 2: Nivel Taxonomico','Exe. 3: Filtros','Exe. 4: Avaliar Lon / Lat']
	linhas = []
	lista_completa = []

	def carregar(self, path):
		file = open(path, 'r', encoding='utf-8')
		self.linhas = file.readlines()
		df = pd.read_csv(path)
		lista = df.values.tolist()
		return df, lista

	def construir(self, path):
		# ifs provisórios ate resolver os bugs
		if path == 'Arquivos/df1.csv':
			file = open('Arquivos/portalbio_export_17-10-2019-13-06-22.csv', 'r', encoding='utf-8')
		if path == 'Arquivos/df2.csv':
			file = open('Arquivos/portalbio_export_16-10-2019-14-39-54.csv', 'r', encoding='utf-8')
		if path == 'Arquivos/df3.csv':
			file = open('Arquivos/portalbio_export_17-10-2019-13-15-00.csv', 'r', encoding='utf-8')
		self.linhas = file.readlines()
		self.lista_completa = [[item for item in itens.split(';')]for itens in self.linhas]
		return self.lista_completa

	#Metodo para contar os nulos
	def count_nulls(self, lista):

		#list compehension que retorna lista das colunas vazias
		def funcao(texto):
			return True if texto == 'Sem Informações' or texto == ' ' else False
		colunas_vazias = [sum([funcao(lista[linha][coluna]) for linha in range(len(lista))]) for coluna in range(len(lista[0]))]
		return colunas_vazias

	#Metodo para retornar a porcetagem de itens sem informação em cada coluna
	def media_nulls(self, lista, num):
	#Map aplicando a função lambda em cada item da lista
		return map(lambda item: item /num.shape[0], lista)


class app_grafica(app_hub):

	option = []
	option_01 = []
	path = 'Arquivos/df1.csv'

	def __init__(self, app = app_hub()):
		print('App Inicializado com Sucesso! =^.^=')

		st.sidebar.markdown('### @Desafio 02')
		self.option = st.sidebar.selectbox('Escolha o exercicio: ',app.dicionario)

		st.title('Hub IA - SENAI / Londrina')
		st.write('Voce selecionou a opcao: ', self.option)

		if st.sidebar.checkbox('Integrantes'):

			st.sidebar.markdown('##### @Savio')
			st.sidebar.markdown('##### @Leticia')
			st.sidebar.markdown('##### @Lucas')
			st.sidebar.markdown('##### @Jessica')
			st.sidebar.markdown(' ')

		if st.sidebar.checkbox('Caminho para a base de dados'):
			self.path = st.sidebar.text_input('Digite o caminho: ', 'Arquivos/df1.csv')

	def inicializar(self, app = app_hub()):

		opcoes = ['Quantidade de valores nao preenchidos', 'Porcetagem de dados faltantes por coluna']
		dados, lista = app.carregar(self.path)

			#Exercicio 01 valores vazios
		if self.option == app.dicionario[0]:
			self.option_01 = st.radio('Exercicio 01: Escolha o grafico:', opcoes)
			st.write('Para cada coluna identique a quantidade de linhas com dados faltantes (em alguns casos, o dado faltante é uma string vazia, em outros casos é uma string contendo algum valor do tipo: "sem informação"). Faça um método que retorna a média de dados faltantes por coluna')
			if self.option_01 == opcoes[0]:
				st.markdown('### Valores vazios ou faltantes: ')
				st.bar_chart(app.count_nulls(lista))
				#st.bar_chart(dados)
				if st.checkbox('Mostrar lista de dados faltantes'):
					#st.write(app.count_nulls(app.construir(app.linhas)))
					st.write(app.count_nulls(lista))

			if self.option_01 == opcoes[1]:
				st.markdown('### Porcetagem de valores faltantes por coluna: ')
				#st.bar_chart(app.media_nulls(app.count_nulls(app.construir(app.linhas))))
				st.bar_chart(app.media_nulls(app.count_nulls(lista),dados))
				if st.checkbox('Mostrar lista de porcetagem'):
					st.write(list(app.media_nulls(app.count_nulls(app.construir(self.path)))))

		#Exercicio 02 Nivel taxonomico
		if self.option == app.dicionario[1]:
			st.write('Para cada item identifique até qual nível taxônomico a ocorrência foi identificada.')
			#verificaTaxonomia metodo importado do felipe
			st.bar_chart(verificaTaxonomia(app.construir(self.path)))
			#st.bar_chart(verificaTaxonomia(app.construir(lista)))
			if st.checkbox('Valores por Coluna'):
				st.write(verificaTaxonomia(app.construir(self.path)))

		#Exercicio 03  Filtros
		if self.option == app.dicionario[2]:

			mapa_bio = pd.read_csv(self.path)
			mapa_bio.rename(columns={'Latitude':'lat','Longitude':'lon'}, inplace=True)

			st.write('Monte filtros de ocorrências por estados, nome de espécie (nome exato ou parte do nome) e categoria de ameaça, e outros filtros que julgar relevante.')
			lista_de_filtros = ['Municipio', 'Familia','Filo','Classe','Localidade', 'Nome cientifico']
			filtros = st.multiselect("Escolha os filtros: -> Municipio -> Familia -> Filo -> Classe -> Localidade -> Nome cientifico", lista_de_filtros)

			data = pd.DataFrame()
			f1,f2,f3,f4,f5,f6 = 1,1,1,1,1,1

			if filtros:
				 my_bar = st.progress(0)
				 for percent_complete in range(0, 100):
				 	my_bar.progress(percent_complete + 1)

			for item in filtros:
				if item == 'Municipio':
					municipios = st.multiselect('Escolha os municipios', list(set(mapa_bio['Municipio']))) #, ["Londrina"]
					if not municipios:
						f1 = 1
					else :
						f1 = mapa_bio['Municipio'].isin(municipios)

				if item == 'Familia':
					familias = st.multiselect('Escolha a familia', list(set(mapa_bio['Familia'])))
					if not familias:
						f2 = 1
					else :
						f2 = mapa_bio['Familia'].isin(familias)

				if item == 'Filo':
					filos = st.multiselect('Escolha o Filo', list(set(mapa_bio['Filo'])))
					if not filos:
						f3 = 1
					else :
						f3 = mapa_bio['Filo'].isin(filos)

				if item == 'Classe':
					classes = st.multiselect('Escolha a classe', list(set(mapa_bio['Classe'])))
					if not classes:
						f4 = 1
					else :
						f4 = mapa_bio['Classe'].isin(classes)

				if item == 'Localidade':
					localidades = st.multiselect('Escolha Localidade', list(set(mapa_bio['Localidade'])))
					if not localidades:
						f5 = 1
					else:
						f5 = mapa_bio['Localidade'].isin(localidades)

				if item == 'Nome cientifico':
					nomes =  st.multiselect('Escolha Nome cientifico', list(set(mapa_bio['Nome cientifico'])))

					if not nomes:
						f6 = 1
					else:
						f6 = mapa_bio['Nome cientifico'].isin(nomes)


				data = mapa_bio.loc[f1 & f2 & f3 & f4 & f5 & f6]

			st.deck_gl_chart(
    			viewport={
         		'latitude': -23.37,
         		'longitude': -51.28,
         		'zoom': 11,
         		'pitch': 50,
     			},
     			layers=[{
         		'type': 'HexagonLayer',
		         'data': data,
		         'radius': 200,
		         'elevationScale': 4,
		         'elevationRange': [0, 1000],
		         'pickable': True,
		         'extruded': True,
		     	}, {
		         'type': 'ScatterplotLayer',
		         'data': data,
		     	}])

			if st.checkbox('Mostrar dados'):
					st.dataframe(data)

		#Exercicio 04 - Geocode - Verificar se dados batem

hub_ia = app_grafica()
hub_ia.inicializar()
