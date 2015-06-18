import numpy as np
import pandas as pd

def processdata(data, year = '2015'):
	cleanls = []
	for line in data:
		linels = line.strip().split()
		linels[0], linels[1] = moddate(linels[0], linels[1], year = year)
		cleanls.append(linels)

	donels = []
	new_model = []
	for line in cleanls:
		doneline = []
		if 'n' in line:
			new_model.append(cleanls.index(line))
			line.remove('n')
			temp_store_check = []
		for ele in line:
			if ('t' not in ele) and ('/' not in ele) and line.index(ele) > 2 and ele not in ['m', 'l', 'switch']:
				if not 'D' in line[1]:
					doneline.append('3.' + ele)
					if len(temp_store_check) > 0:
						doneline.extend(temp_store_check)
						temp_store_check = []
				else:
					if int(ele[0]) >= 5:
						doneline.append('3.' + ele)
					else:
						doneline.append('4.' + ele)
			elif '/' in ele:
				if not 'D' in line[1]:
					temp_store_check.append('/' + '3.' + ele[1: ])
				else:
					if int(ele[0]) >= 5:
						temp_store_check.append('/' + '3.' + ele[1: ])
					else:
						temp_store_check.append('/' + '4.' + ele[1: ])
			else:
				doneline.append(ele)
		donels.append(doneline)
	new_model.append(len(donels))
	for indx in range(len(new_model) - 1):
		n = 1
		for indx_label in range(new_model[indx] , new_model[indx + 1]):
			temp_batchID = "m" + donels[new_model[indx]][1]
			donels[indx_label].insert(3, temp_batchID)
			donels[indx_label].insert(4, indx_label - new_model[indx] + 1)		
	return donels

def clean_line(line, sep = '-', datesep = '.'):	
	linels = line.strip().split()
	datels = linels[0].split(datesep)
	datefm = sep.join(datels)
	year = datels[0]
	month = datels[1]
	batch = linels[1]
	if len(month) < 2:
		batchfm = year[2:] + sep + '0' + month + sep + batch.upper()
	else:
		batchfm = year[2:] + sep + month + sep + batch.upper()
	linels[0], linels[1] = datefm, batchfm
	doneline = []
	for ele in linels:
		if ('t' not in ele) and ('/' not in ele) and linels.index(ele) > 2 and ele not in ['m', 'l', 'switch']:
			if not 'D' in linels[1]:
				doneline.append('3.' + ele)
			else:
				if int(ele[0]) >= 5:
					doneline.append('3.' + ele)
				else:
					doneline.append('4.' + ele)
		else:
			doneline.append(ele)
	return doneline

def moddate(date,batch, year = '2014', sep = '-'):
	month, day = date.split('.')
	datefm = year + sep + month + sep + day
	if len(month) < 2:
		batchfm = year[2:] + sep + '0' + month + sep + batch.upper()
	else:
		batchfm = year[2:] + sep + month + sep + batch.upper()
	return datefm, batchfm
	

		
				
