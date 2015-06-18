# -*- coding: utf-8 -*-
import sqlite3
import pandas as pd
from string import Template
from datetime import datetime, timedelta

db_name = 'productdata.sqlite'
table_switch = {'b': 'batchinfo', 'c' : 'batchinfo', 'd': 'batchinfo40'}

def namematch_id(search_str):
	search_str = '%' + search_str + '%'
	connection = sqlite3.connect('productdata.sqlite')
	cursor = connection.cursor()
	cursor.execute("""SELECT * FROM product WHERE keyname LIKE ?""", (search_str,))
	results = cursor.fetchall()
	connection.close()
	#results = pd.DataFrame(results)
	return results

	
def id_match_history(query_id):
	connection = sqlite3.connect('productdata.sqlite')
	cursor = connection.cursor()
	cursor.execute("""SELECT product_id, keydate, company, keyname, size, number, unit_price FROM history WHERE product_id = ?""", (query_id,))
	results = cursor.fetchall()
	connection.close()
	#results = pd.DataFrame(results)
	return results
	
	
def id_match_product(query_id):
	connection = sqlite3.connect('productdata.sqlite')
	cursor = connection.cursor()
	cursor.execute("""SELECT * FROM product WHERE id = ?""", (query_id,))
	results = cursor.fetchall()
	connection.close()
	#results = pd.DataFrame(results, columns = ['id', 'keyname', 'type', 'std_code', 'size'])
	return results

def priceinfo_list(pricelist):
	'''
	input a list of query pricelist from pickle
	the function return a neat output priceinfo list for visual
	'''
	key = []
	name = []
	type = []
	size = []
	for item in pricelist:
		unit_result = id_match_product(item[0])
		key.append(unit_result[0][1].split("::")[0])      # waiting for modify by update the database
		name.append(unit_result[0][1].split("::")[1])
		type.append(unit_result[0][2])
		size.append(unit_result[0][4])
 	priceinfo = pd.DataFrame(pricelist, columns = ['id', 'amount', 'unit_price'])
	priceinfo['key'] = key
	priceinfo['name'] = name
	priceinfo['type'] = type
	priceinfo['size'] = size
	priceinfo['price'] = priceinfo.amount * priceinfo.unit_price
	priceinfo['no'] = range(1, len(priceinfo)+1)
	priceinfo = priceinfo.reindex(columns = ['no','id', 'key','type', 'name', 'size', 'amount', 'unit_price', 'price'])
	return priceinfo

'''
YONGHUI
'''
# CREATE TABLE "batchinfo" ("batchID" TEXT PRIMARY KEY NOT NULL UNIQUE, "outpressure" FLOAT, "date" DATE NOT NULL, "modelID" TEXT NOT NULL, "modeltimes" INTEGER NOT NULL, "except_point" INTEGER NOT NULL, "original_text" TEXT NOT NULL, "mean" FLOAT, "std" FLOAT, "max" FLOAT, "min" FLOAT, "range" FLOAT,"count_l"INTEGER NOT NULL,"count_m"INTEGER NOT NULL,"count_t"INTEGER NOT NULL,"procedure_index"FLOAT NOT NULL, "upper_fail_rate" FLOAT NOT NULL, "lower_fail_rate" FLOAT NOT NULL, "total_fail_rate" FLOAT NOT NULL, "step_mean"FLOAT NOT NULL, "batchtype" TEXT);
def input_batch(Batch, batchtype):
	print batchtype
	connection = sqlite3.connect('productdata.sqlite')
	cursor = connection.cursor()
	try:
		cursor.execute("""INSERT INTO %s (batchID, outpressure, date, modelID, modeltimes, except_point, original_text, mean, std, max, min, range, 
						count_l, count_m, count_t, procedure_index, upper_fail_rate, lower_fail_rate, total_fail_rate, step_mean, batchtype) VALUES (?, ?, ?, ?, ?, ?, ?,?,?,?,?,?, ?, ?, ?, ?,?,?,?,?, ?)"""% table_switch[batchtype], 
						(Batch.batchID, Batch.outpressure, Batch.date, Batch.modelID, Batch.modeltimes, Batch.except_point, 
						Batch.original_text, Batch.get_mean(), Batch.get_std(), Batch.get_max(), 
						Batch.get_min(), Batch.get_range(), Batch.count_except('l'), Batch.count_except('m'), Batch.count_except('t'), 
						Batch.procedure_index_dev(), Batch.upper_fail_rate(), Batch.lower_fail_rate(), 
						Batch.total_fail_rate(), Batch.get_step_mean(), Batch.get_batchtype()))
		connection.commit()
		connection.close()
	except sqlite3.IntegrityError:
		print "unique problem"
		connection.close()
	
def select_date(end, delta):
	datefm = tuple([int(ele) for ele in end.split('-')])
	enddate = datetime(datefm[0], datefm[1], datefm[2])
	startdate = enddate - timedelta(delta)
	start = startdate.strftime('%Y-%m-%d')
	return start, end
	
def history_select_date(datelist):
	donels = []
	for date in datelist:
		datefm = tuple([int(ele) for ele in date.split('-')])
		donels.append(datetime(datefm[0], datefm[1], datefm[2]))
	return donels


def output_stat_data(end, timedelta, batchtype):
	start, end = select_date(end, timedelta)
	connection = sqlite3.connect('productdata.sqlite')
	cursor = connection.cursor()
	cursor.execute("""SELECT mean, std, range, outpressure, original_text, procedure_index, upper_fail_rate, lower_fail_rate, total_fail_rate, step_mean FROM %s WHERE date between ? and ?;""" % table_switch[batchtype], (str(start), str(end)))
	results = cursor.fetchall()
	print end, start
	connection.close()
	results = pd.DataFrame(results, columns = ['means','stds','ranges', 'outpressure','text', 'procedure_index', 'upper_fail_rate', 'lower_fail_rate', 'total_fail_rate', 'step_mean'])
	return results

def get_batchtype(batch):   #B C or D?
	if 'B' in batch:
		return 'b'
	elif 'C' in batch:
		return 'c'
	elif 'D' in batch:
		return 'd'

def output_history(start, end, batchtype):
	connection = sqlite3.connect('productdata.sqlite')
	cursor = connection.cursor()
	cursor.execute("""SELECT batchID, outpressure, date, modelID, modeltimes, except_point, original_text, mean, std, max, min, range, procedure_index, upper_fail_rate, lower_fail_rate, total_fail_rate, step_mean FROM %s WHERE date between ? and ?;"""% table_switch[batchtype], (str(start), str(end)))
	results = cursor.fetchall()
	connection.close()
	results = pd.DataFrame(results, columns = ['batchID', 'outpressure', 'date', 'modelID', 'modeltimes', 'except_point', 'text', 'means', 'stds', 'maxs', 'mins', 'ranges',
												'procedure_index', 'upper_fail_rate', 'lower_fail_rate', 'total_fail_rate', 'step_mean'])
	return results

	
	
	
def output_model(modelID, batchtype):
	connection = sqlite3.connect('productdata.sqlite')
	cursor = connection.cursor()
	cursor.execute("""SELECT batchID, outpressure, date, modelID, modeltimes, except_point, original_text, mean, std, max, min, range, procedure_index, upper_fail_rate, lower_fail_rate, total_fail_rate, step_mean 
						FROM %s WHERE modelID = ?;"""% table_switch[batchtype], (modelID, ))
	results = cursor.fetchall()
	connection.close()
	results = pd.DataFrame(results, columns = ['batchID', 'outpressure', 'date', 'modelID', 'modeltimes', 'except_point', 'text', 'means', 'stds', 'maxs', 'mins', 'ranges',
												'procedure_index', 'upper_fail_rate', 'lower_fail_rate', 'total_fail_rate', 'step_mean'])
	return results
	
def output_batch(batchID, batchtype):
	connection = sqlite3.connect('productdata.sqlite')
	cursor = connection.cursor()
	cursor.execute("""SELECT batchID, outpressure, date, modelID, modeltimes, except_point, original_text, mean, std, max, min, range, procedure_index, 
					upper_fail_rate, lower_fail_rate, total_fail_rate FROM %s WHERE batchID = ?;"""% table_switch[batchtype], (batchID, ))
	results = cursor.fetchall()
	connection.close()
	results = pd.DataFrame(results, columns = ['batchID', 'outpressure', 'date', 'modelID', 'modeltimes', 'except_point', 'text', 'means', 'stds', 'maxs', 'mins', 'ranges',
												'procedure_index', 'upper_fail_rate', 'lower_fail_rate', 'total_fail_rate'])
	return results
	
def query_modelinfo(batchtype):
	'''
	select modelID, max(date) from batchinfo where modeltimes = 1 and modeltype = b;
	'''
	connection = sqlite3.connect('productdata.sqlite')
	cursor = connection.cursor()
	cursor.execute("""select modelID, max(date) from %s where modeltimes = 1 and batchtype = ?;"""% table_switch[batchtype], (batchtype, ))
	results = cursor.fetchall()
	modelID = results[0][0]
	cursor.execute("""select modelID, max(modeltimes) from %s where modelID = ?;"""% table_switch[batchtype], (modelID, ))
	results = cursor.fetchall()
	connection.close()
	modeltimes = results[0][1] + 1
	return modelID, modeltimes