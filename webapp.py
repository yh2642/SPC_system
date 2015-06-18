# -*- coding: utf-8 -*-
import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from sql_functions import namematch_id, id_match_history, priceinfo_list, input_batch
import sql_functions as sql
import pandas as pd
from pricelist import add_list, load_list, modify_item, remove_item
from werkzeug import secure_filename
import re
from clean_functions import data_clean, process2product, process2history, import2product, import2history
import numpy as np
from process_raw_data import processdata, clean_line
from io import StringIO
import matplotlib.pyplot as plt
from batchclass import Batch
from datetime import datetime
from historyclass import History
import spc_list
import pickle 
from regression import loadDataSet, standRegres


app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'webapp.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))

app.config.from_envvar('FLASKR_SETTINGS', silent=True)






# global variable
now = datetime.now()
today = str(now.year) + '-' + str(now.month) + '-' + str(now.day)
nav_list = [u'公司主页', u'产品查询', u'快捷报价', u'清单管理', 
		u'数据库更新', u'标签打印', u'爆破质量控制', u'爆破片生产过程控制']
nav_url = ['http://jhwuyue.1688.com/', '/query?keyname=RF150-30&id=1234', '/lsman', '/lsman', '/', '/']
info = {'title' : u'金华伍岳密封件有限公司', 'head' : u'伍岳信息管理平台',
	'query': u'产品查询', 'pricing' : u'快捷报价', 'lsman' : u'清单管理', 'lsmod' : u'修改清单', 'lsdownload' : u'下载清单', 'dbupdate' : u'数据库更新', 'label' : u'标签打印', 'qualitycontrol':u'爆破片单批次质量分析', 
	'history_qc' : u'爆破片历史检验数据统计', 'processcontrol' : u'爆破片生产过程控制', 'today' : today, 'model_qc':u'爆破片过程管控探索分析'}
batchinfo = '2015.3.10 c02 8.5  7 5 6 6 6 55 7 6 55 5 5 4 6 4 4 5 45 4 35 4 5 4 5 5 5 5 3 5 4 45 35 3 5 45 4 3 3 4 45 4 3 3 4  45 4 5 4 6 5 3 6 5 5 5'




@app.route('/')
def index():
	"""
	top page
	"""	
	query_content = ['', '']	
	return render_template('index.html', info = info, nav_list = nav_list, nav_url = nav_url, query_content = query_content)


@app.route('/query', methods = ['Post','Get'])
def show_records():
	query_content = [request.args['keyname'], request.args['id']]
	if len(query_content[0]) != 0:	
		table1 = namematch_id(query_content[0])
	else:
		table1 = []
	if len(query_content[1]) != 0:	
		table2 = id_match_history(query_content[1])
	else:
		table2 = []	
	caption1 = query_content[0] + u'垫片查询结果'
	caption2 = query_content[1] + u'号垫片生产记录'
	col1 = [u'编号', u'垫片名称', u'垫片类型', u'规格', u'尺寸']
	col2 = [u'编号', u'发货日期', u'客户单位', u'垫片名称', u'尺寸', u'数量', u'单价']

	return render_template('show_table.html', table1 = table1, table2 = table2, info = info, nav_list = nav_list, col1 = col1, col2 = col2, caption1 = caption1, caption2 = caption2, query_content = query_content, nav_url = nav_url)

@app.route('/pricing', methods = ['Post', 'Get'])
def add_item():
	new_item = request.args['new_item']
	new_item = new_item.split()
	try:	
		if len(new_item) == 3:
			new_item = [int(new_item[0]), int(new_item[1]), float(new_item[2])]
			add_list(new_item)
			flash(u'成功加入清单!')
			return redirect(url_for('show_list'))
		else:
			flash(u'输入错误！')
	except:
		flash(u'输入错误！')	
    	return redirect(url_for('index'))


## show pricelist ##
@app.route('/lsman')
def show_list():
	pricelist = load_list()
        priceinfo = priceinfo_list(pricelist).values
	col = [u'序号', u'编号', u'名称', u'类型', u'规格', u'尺寸',u'数量',u'单价', u'价格']
	caption = u'垫片报价清单一览'
	return render_template('lsman.html', priceinfo = priceinfo, info = info, nav_list = nav_list, nav_url = nav_url, col = col, caption = caption)

## modify page ##
@app.route('/modls')
def mod_list():
	pricelist = load_list()
	priceinfo = priceinfo_list(pricelist).values
	col = [u'序号', u'编号', u'名称', u'类型', u'规格', u'尺寸', u'数量',u'单价', u'价格', u'修改', u'删除']
	caption = u'修改清单'
	return render_template('lsmod.html', priceinfo = priceinfo, info = info, nav_list = nav_list, col = col, caption = caption, nav_url = nav_url)


### modify delete and drop ###
@app.route('/mod_item/<row>', methods = ['Post', 'Get'])
def mod_item(row):
	row = int(row.encode('utf8'))	
	mod_item = request.form['change_item']
	mod_item = mod_item.split()
	try:	
		if len(mod_item) == 3:
			mod_item = [int(mod_item[0]), int(mod_item[1]), float(mod_item[2])]
			modify_item(row, mod_item)
			flash(u'修改成功!')
			return redirect(url_for('mod_list'))
		else:
			flash(u'输入错误！')
	except:
		flash(u'输入错误！')	
    	return redirect(url_for('mod_list'))

@app.route('/rm_item/<row>', methods = ['Post', 'Get'])
def rm_item(row):
	row = int(row.encode('utf8'))	
	remove_item(row)
    	return redirect(url_for('mod_list'))




### output pricelist ###
@app.route('/dl_list')
def dl_list():
	pricelist = load_list()
	priceinfo = priceinfo_list(pricelist)
	col = [u'序号', u'编号', u'名称', u'类型', u'规格', u'尺寸',u'数量',u'单价', u'价格']
	priceinfo.columns = col
	priceinfo.to_csv('static/out.csv', encoding = 'utf8', na_rep = 'NULL', index = False, header = True)
	return redirect('static/out.csv')

@app.route('/upload', methods = ['Post', 'Get'])
def upload_file():
	file_path = os.path.join(os.getcwd(), 'static')
	if request.method == 'POST':
		f = request.files['the_file']
		f.save(os.path.join(file_path, secure_filename(f.filename)))
		flash(u'文件上传成功！')
		return redirect(url_for('index'))

@app.route('/data_clean')
def data_process():
	names = ['date','no','type','std_code','size','number','unit_price','price','production','company','year']
	try:	
		data = pd.read_csv('static/daoru.csv', encoding = 'gbk', header = None, names = names)
		data = data_clean(data)
		data2 = process2product(data)
		data3 = process2history(data)
		table1 = data2.values
		table2 = data3.values	
	except IOError:
		flash(u'文件不存在！')
		table1 = []
		table2 = []
	col1 = [u'序号', u'名称',  u'类型', u'规格',u'尺寸']	
	col2 = [u'序号', u'名称', u'类型', u'尺寸',u'数量', u'单价', u'价格', u'日期', u'客户公司', u'生产编号']
	caption1 = u'新导入垫片'
	caption2 = u'新导入清单一览'
	data3.to_csv('static/history_temp.csv', encoding = 'gbk', na_rep = 'NULL', index = False, header = True)
	data2.to_csv('static/product_temp.csv', encoding = 'gbk', na_rep = 'NULL', index = False, header = True)
	return render_template('show_import.html', table1 = table1, table2 = table2, info = info, nav_list = nav_list, col1 = col1, col2 = col2, caption1 = caption1, caption2 = caption2, nav_url = nav_url)

@app.route('/import_db')
def import_db():
	try:
		data2 = pd.read_csv('static/product_temp.csv', encoding = 'gbk')
		data3 = pd.read_csv('static/history_temp.csv', encoding = 'gbk')
		import2product(data2)
		import2history(data3)
		flash(u'成功导入数据库！')
		return redirect(url_for('data_process'))
	except IOError:
		flash(u'文件未正确上传!')
	return redirect(url_for('index'))

@app.route('/batch_analysis', methods = ['Post', 'Get'])
def batch_analysis():
	#create Batch class
	batchinfo = request.args['batchinfo']
	donels = clean_line(batchinfo)
	batch = Batch(donels)
	# plot production process records	
	records_plot = batch.process_plot()
	test_hist = batch.history_test_hist()
	scatter_plot = batch.history_scatter_subplot()
	hist_plot = batch.history_hist_subplot()
	# make the stat summary table
	col1 = [u'生产日期', u'机床压力', u'平均爆破压力（Mpa）', u'标准偏差值', u'波动范围', u'平均移动极差', u'工序能力指数Cp', u'上限不合格率（>3.6）', u'下限不合格率(<3.0)', u'批次不合格率']
	stat_data = batch.stat_info()
	
	return render_template('show_batch.html', hist_plot = hist_plot, scatter_plot = scatter_plot, test_hist = test_hist, stat_data = stat_data, records_plot = records_plot, col1 = col1, donels = donels, batch = batch, info = info, nav_list = nav_list, nav_url = nav_url)

@app.route('/history_qc', methods = ['Post', 'Get'])
def history_qc():
		
	raw_data = "static/raw_data/temp_files.txt"
	fr = open(raw_data)
	data = fr.readlines()
	fr.close()
	data2 = processdata(data, year = '2014')
	teststr = ""
	n = 0
	#for ele in data2:
		#temp_batch = Batch(ele)
		#print temp_batch.records
		#input_batch(temp_batch, temp_batch.get_batchtype())
		#print temp_batch.batchID

	
	startdate = request.args['startdate']
	enddate = request.args['enddate']
	pressure_type = request.args.get('batchtype', '')
	
	#try:
	history = History(startdate, enddate, pressure_type)
	test_hist = history.get_raw_test_hist()
	hist_plot = history.history_hist_subplot()
	scatter_plot = history.history_scatter_subplot()
	group_date_plot = history.data_groupby_day()
	return render_template('show_history.html', group_date_plot = group_date_plot, scatter_plot = scatter_plot, hist_plot = hist_plot, test_hist = test_hist, info = info, nav_list = nav_list, nav_url = nav_url)
	#except ValueError:
		#flash(u'所选时间段查无数据！')
		#return redirect(url_for('index'))
		
	
@app.route('/query_batchlist', methods = ['Post', 'Get'])
def query_batchlist():
	searchdate1 = request.args.get('startdate', '')
	searchdate2 = request.args.get('enddate', '')
	searchmodelID = request.args.get('modelID', '')
	searchbatchID = request.args.get('batchID', '')
	pressure_type = request.args.get('batchtype', '')
	
	if len(searchmodelID) > 0:
		batchtype = sql.get_batchtype(searchmodelID)
		feedback_info = sql.output_model(request.args['modelID'], batchtype)
		
	elif len(searchdate1) > 0 and len(searchdate2) > 0 and pressure_type >0:
		feedback_info = sql.output_history(request.args['startdate'], request.args['enddate'], request.args['batchtype'])	
	elif len(searchbatchID) > 0:
		batchtype = sql.get_batchtype(searchbatchID)
		feedback_info = sql.output_batch(searchbatchID, batchtype)
		
	# data_list = dig_data.dig_data()
	col1 = [u'生产批号', u'生产日期', u'机床压力', u'平均爆破压力（Mpa）', u'标准偏差值', u'波动跨度', 
			u'工序能力指数Cp', u'上限不合格率（>3.6）', u'下限不合格率(<3.0)', u'批次不合格率']
	show_columns = ['batchID', 'date', 'outpressure', 'means', 'stds', 'ranges', 'procedure_index', 'upper_fail_rate', 
					'lower_fail_rate', 'total_fail_rate']
	show_table = feedback_info.reindex(columns = show_columns)
	table_content = show_table.values	
	return render_template('show_batch_list.html', col1 = col1, table_content = table_content, info = info, nav_list = nav_list, nav_url = nav_url)

@app.route('/process_control', methods = ['Post', 'Get'])
def process_control():
	batchtype = request.args.get('batchtype', '')
	worker = batchtype
	try:
		current_batch = spc_list.load_records(batchtype)
		process_plot = current_batch.process_plot()
		col1 = [u'刻槽压力', u'抽检序号', u'抽检1 (Mpa)', u'复检', u'抽检2 (Mpa)', u'复检', u'抽检3 (Mpa)', u'复检', u'抽检4 (Mpa)', u'复检',
			u'抽检5 (Mpa)', u'复检']
		tt_value = current_batch.get_raw_records()
		ct_value = current_batch.get_check_records()
		nof = range(1, len(tt_value), 5)
		nol = range(5, len(tt_value) + 5, 5)
		no = [(str(nof[indx]) + '~'+ str(nol[indx])) for indx in range(0,len(nof))]
		outpressure = current_batch.update_outpressure()
		
		return render_template('process_control.html', ct_value = ct_value, col1 = col1, current_batch = current_batch, outpressure = outpressure, no = no, tt_value = tt_value, process_plot = process_plot, worker = worker, info = info, nav_list = nav_list, nav_url = nav_url)
	except IOError:
		flash(u'无先前数据记录， 请先创建批次!')
		return render_template('new_batch.html', worker = worker, info = info, nav_list = nav_list, nav_url = nav_url)
		
		
@app.route('/new_batch', methods = ['Post', 'Get'])
def new_batch():
	batchID = request.args.get('batchID', '')
	date = request.args.get('date', '')
	outpressure = request.args.get('outpressure', '')
	optional_records = request.args.get('optional_records', '')
	new_model = request.args.get('new_model', '')

	new_ele_str = ' '.join([date, batchID, outpressure, optional_records])
	donels = clean_line(new_ele_str, datesep = '-')
	
	# 处理模具名问题
	if new_model == 'n':
		modelname = 'm' + donels[1]
		donels.insert(3, modelname)
		donels.insert(4, 1)
		batch = Batch(donels)
	else:
		print donels
		batch = Batch(donels)
		
		batchtype = batch.get_batchtype()
		modelname, modeltimes = sql.query_modelinfo(batchtype)
		batch.update_modelinfo(modelname, modeltimes)
	print 'batchtype is ', batch.get_batchtype()
	if spc_list.new_batch(batch, batch.get_batchtype()):
		flash(u'成功创建新批次！')
	else:
		flash(u'无法创建新批次！')
	return redirect('/process_control?batchtype=%s'%batch.get_batchtype())
	
@app.route('/add_new_test', methods = ['Post', 'Get'])	
def add_new_test():
	new_record = request.args.get('new_record', '')
	worker = request.args.get('workerID', '')
	delete = request.args.get('pop', '')
	drop = request.args.get('drop', '')
	print delete
	print worker
	print len(new_record)
	current_batch = spc_list.load_records(worker)
	if len(new_record) > 0:
		current_batch.add_record(new_record)
	if delete == '1':
		print 'here'
		current_batch.pop_record()
	if drop == 1:
		pass
	
	spc_list.new_batch(current_batch, worker)



	#redirect('/process_control?batchtype=%s'%current_batch.get_batchtype())
	return redirect('/process_control?batchtype=%s'%current_batch.get_batchtype())
	
if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0')


#raw_data = "static/raw_data/15.4-3.3.txt"
#	fr = open(raw_data)
#	data = fr.readlines()
#	fr.close()
#	data2 = processdata(data)
#	teststr = ""
#	for ele in data2:
#		temp_batch = Batch(ele)
		#input_batch(temp_batch)