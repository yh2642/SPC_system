import re
import pandas as pd
import numpy as np
import sql_functions
import sqlite3
import pandas as pd
import os
import numpy as np
import pandas as pd

def clean_col(name_col):
	'''
	remove the space sign in each name, 
	it should input the whole coloum and modify it automatically
	'''
	for indx in range(len(name_col)):
		if ' ' in name_col[indx]:
			pieces = [x.strip() for x in name_col[indx].split()]
			name_col[indx] = '_'.join(pieces)
			
def classify_col(type_col):
	'''
	this function comes from the first step the phase of classify each product
	it will get the first string before _ of each type name
	'''
	for indx in range(len(type_col)):
		if '_' in type_col[indx]:
			pieces = type_col[indx].split('_')[0]
			# waiting for a dictionary
			type_col[indx] = pieces
			
			

def combine_col(col1, col2, col3 = None, sep = '::'):
	'''
	the function mainly used to combine names and std_code
	it combine to two col and return a new list
	before we use this function, we should dropna the argument col1
	'''
	result = []
	for indx in range(len(col1)):
		if not col2[indx] is 'unknown':
			result.append(col1[indx] + sep + col2[indx])
	 	elif not col3[indx] is 'unknown':
		  	result.append(col1[indx] + sep + col3[indx])
		else:
			result.append(col1[indx])
	return result

def combine_col2(col1, col2, col3 = None, sep = '::'):
	'''
	just for the year col, how to string it?
	'''
	result = []
	for indx in range(len(col1)):
		if not col2[indx] is 'unknown':
			result.append(str(col1[indx]) + sep + str(col2[indx]))
	 	elif not col3[indx] is 'unknown':
		  	result.append(col1[indx] + sep + col3[indx])
		else:
			result.append(col1[indx])
	return result
	
def date_generate(col_date):
	'''
	the function take the date coloumn as input modify the dateformat into mm.dd
	if there not two digit in each row, the function would delete the row immidately
	'''
	date = col_date.dropna()
	regex = re.compile('[0-9]+')
	indlist = list(date.index)
	dropls = []
	for indx in indlist:
		templist = regex.findall(date[indx])
		if len(templist) == 2:
			col_date[indx] = '-'.join(templist)
		else:
			if len(col_date[indx]) < 2:
				col_date[indx] = np.nan
			else:
				dropls.append(indx)
	return dropls
	
def match_type_col(typer, typecol):
	'''
	this function aims to formats the type col into very tidy form
	it take a codelist as input
	and modify the col automatically
	'''
	# typerlist = [(typer.ix[i][0], typer.ix[i][1], typer.ix[i][2]) for i in range(len(typer))]
	typename = list(typer.typename)
	typematch = list(typer.match)
	for indx in range(len(typer) - 1):
		for row in range(len(typecol)):
			if typematch[indx] in typecol[row]:
				typecol[row] = typename[indx]
			#if typematch[indx] in typecol[row]:
			#	typecol[row] = typename[indx]
	zeros = []
	for row in range(len(typecol)):
		if typecol[row] == u'0':
			zeros.append(row)
		if not typecol[row] in list(typer.typename):
			typecol[row] = typename[-1]
	return zeros

def data_clean(data):
	"""
	this function is designed to finish the first step of data_process
	the function canbe use in several occasions
	"""
	index = (data['type'].notnull() & (data['std_code'].notnull() | data['size'].notnull())) #(data['no'].notnull())
	data = data[index]

	index = data['no'].notnull()
	data = data[index]

	data.index = range(len(data))
	data = data.fillna({'std_code': 'unknown', 'size': 'unknown', 'production': 'None'})
	# clean the name colomn
	clean_col(data['type'])
	# clean the std_code coloum
	clean_col(data['std_code'])
	# clean the size colomn
	clean_col(data['size'])

	# combine the name and std_code into key_name col to make it more specifically
	data['keyname'] = combine_col(data['type'], data['std_code'], data['size'])

	# data = data.drop(['production', 'price'], axis = 1)



	# process the date col and return a list of row index needed to be drop
	droplist = date_generate(data['date'])
	data = data.drop(droplist)

	# distribute the year to each row and convert it into string for next step
	data = data.fillna(method = 'ffill')
	#data.year = data.year.fillna(method = 'ffill')
	#data.company = data.company.fillna(method = 'ffill')
	data.year = data.year.astype(int)

	# combine year and date which produce a new col called keydate
	data.index = range(len(data))
	data['keydate'] = combine_col2(data.year, data.date, sep = '-')


	colnames = ['no','keydate', 'date', 'keyname', 'type', 'std_code', 'size', 'number', 'unit_price', 'price', 'production', 'company', 'year']
	data = data.reindex(columns = colnames)
	# classfy the type col
	classify_col(data.type)
	# read the type_complier code
	typer = pd.read_csv('static/type_compiler.csv', encoding = 'gbk')


	zeros = match_type_col(typer, data.type)
	data = data.drop(zeros)
	data.index = range(len(data))
	return data

def process2product(data):
	"""
	this function process the cleaned data info the dataframe which is ready 
	to import into the product table
	"""
	col = ['keyname', 'type', 'std_code', 'size']
	data2 = data.ix[:, col]
	data2 = data2.drop_duplicates('keyname')
	data2.index = range(len(data2))
	data2['id'] = range(1, len(data2) + 1)
	data2 = data2.reindex(columns = ['id', 'keyname', 'type', 'std_code', 'size'])
	return data2

def process2history(data):
	data['id'] = range(1, len(data)+1)
	data3 = data.reindex(columns = ['id', 'keyname', 'type', 'size', 'number', 'unit_price', 'price','keydate', 'company', 'production'])
	return data3




def import2product(data2):
	connection = sqlite3.connect('productdata.sqlite')

	cursor = connection.cursor()

	cursor.execute("SELECT keyname FROM product")

	result = cursor.fetchall()
	keylist = []
	for indx in range(len(result)):
		keylist.append(result[indx][0])


	# cursor.execute(query)
	test_list = []
	for indx in range(len(data2)):
		# id = data2.ix[indx][0]
		keyname = data2.ix[indx][1]
		type = data2.ix[indx][2]
		std_code = data2.ix[indx][3]
		size = data2.ix[indx][4]
		if not keyname in keylist:
			test_list.append(keyname)
			cursor.execute("INSERT INTO product(keyname, type, std_code, size) VALUES (?, ?, ?, ?)", (keyname, type, std_code, size))
			connection.commit()
			
	connection.close()

def import2history(data3):
	connection = sqlite3.connect('productdata.sqlite')
	cursor = connection.cursor()
	for indx in range(len(data3)):
		current_name = data3.keyname[indx]
		cursor.execute("SELECT id FROM product WHERE keyname = ?", (current_name, ))
		current_id = cursor.fetchone()[0]
		id, keyname, type, size, number, unit_price, price, keydate, company, production = list(data3.ix[indx])
		cursor.execute("INSERT INTO history (product_id, keyname, type, size, number, unit_price, price, keydate, company, production) VALUES (?,?,?,?,?,?,?,?,?,?)", (current_id, keyname, type, size, number, unit_price, price, keydate, company, production))
		connection.commit()

	connection.close()
