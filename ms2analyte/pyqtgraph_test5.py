import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import pyqtgraph as pg
import numpy as np
import os
import pandas
import random
import time
import pickle
from pyqtgraph.Qt import QtCore, QtGui
import datetime as dt

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QLineEdit, QTabWidget, \
				  QGridLayout, QVBoxLayout
				  


from file_handling import data_import

########### Data Import #################

def fetch_sample_list(input_structure, input_type):
	sample_list = data_import.name_extract(input_structure, input_type)

	return sample_list



#######################################################################################
def import_dataframe(input_structure, input_type, sample_name):
	with open((os.path.join(input_structure.output_directory, input_type, sample_name + "_all_replicates_blanked_dataframe.pickle")), 'rb') as f:
		df = pickle.load(f)
	f.close()

	return df


#######################################################################################
def import_experiment_dataframe(input_structure):
	with open((os.path.join(input_structure.output_directory,  input_structure.experiment_name + "_experiment_analyte_overview_tableau_output.csv"))) as f:
		df = pandas.read_csv(f)

	return df
    
	

	
def import_mz_blankOff_nullOff(input_structure, input_type, sample_name):
	with open((os.path.join(input_structure.output_directory, input_type, sample_name + "_all_replicates_blanked_dataframe.pickle")), 'rb') as f:
		df = pickle.load(f)
	f.close()
		#print(df)
	df['blank_analyte'].replace('',np.nan, inplace=True)
	df.dropna(subset=['blank_analyte'],inplace=True)
	df[df.blank_analyte != 'False']
	sorted_df = df.sort_values(by=['blank_analyte'])
	#df.drop(['True'], inplace = True )

	#df[df.blank_analyte != 'NaN']
	#print(df)

	#df['blank_analyte'].replace('',np.nan, inplace=True)
	#print(df.blank_analyte)
	#print(df.to_string())

	#sorted_df = df.sort_values(by=['mz'])
	
	#print(sorted_df)
	mz_array = []





	for analyte_id in sorted_df.analyte_id.unique():
		mz_array.append([sorted_df[sorted_df["analyte_id"] == analyte_id]["mz"].to_numpy(),
                         sorted_df[sorted_df["analyte_id"] == analyte_id]["intensity"].to_numpy()])


	return mz_array
	
	


input_structure = data_import.input_data_structure()
input_type = "Samples"

sample_names = fetch_sample_list(input_structure, input_type)


#################################### Start GUI  ##################################################
class Window (QMainWindow):



	def __init__(self):
		super(Window, self).__init__()
		

        # changing the background color to yellow 
		self.setStyleSheet("background-color: white;")
		
		
		#self.setGeometry(50, 50, 3500, 1650)

		self.setWindowTitle("Ms2Analyte")
		self.setWindowIcon(QIcon('MS2Analyte.png'))
		
		pg.setConfigOption('background', 'w')


		self.border1 = QLabel("", self)
		self.border1.setStyleSheet("border: 2px solid black;")
		self.border1.resize(2970,1600)
		self.border1.move(10,196)
		
		extractAction = QAction("&Quit", self)
		extractAction.setShortcut("Ctrl+Q")
		extractAction.setStatusTip('Leave The App')
		extractAction.triggered.connect(self.close_application)
		
		self.statusBar()
		
		mainMenu = self.menuBar()
		mainMenu.resize(100,100)
		
		fileMenu = mainMenu.addMenu('&File')
		fileMenu.addAction(extractAction)
		toolsMenu = mainMenu.addMenu('&Tools')


		self.comboBox = QComboBox(self)
		self.comboAnalyte = QComboBox(self)
		self.comboBox.currentTextChanged.connect(self.region_2)
		n = 0
		while n < len(sample_names):
			self.comboBox.addItem(sample_names[n])
			
			n+=1	
		self.comboBox.move(3020, 260)
		self.comboBox.resize(400,50)
		


		
		self.region_1()
		self.region_2()
		self.region_3()
		#self.Replicate()
		self.Plot()
		
		
######## Hide some plots initially ########
		
		self.mz_r1_plot.hide()
		self.mz_r2_plot.hide()
		self.mz_r3_plot.hide()

		self.rt_r1_plot.hide()
		self.rt_r2_plot.hide()
		self.rt_r3_plot.hide()
		
		self.mz_r1_bOn_nOff_plot.hide()
		self.mz_r2_bOn_nOff_plot.hide()
		self.mz_r3_bOn_nOff_plot.hide()
		self.rt_r1_bOn_nOff_plot.hide()
		self.rt_r2_bOn_nOff_plot.hide()
		self.rt_r3_bOn_nOff_plot.hide()
		self.mz_bOn_nOff_plot.hide()
		self.rt_bOn_nOff_plot.hide()
		self.mz_bOff_nOn_plot.hide()
		self.rt_bOff_nOn_plot.hide()
		self.mz_bOff_nOff_plot.hide()
		self.rt_bOff_nOff_plot.hide()
		self.ex_bOn_plot.hide()
		self.ex_bOff_plot.hide()
		#self.grid = QGridLayout()
		self.showMaximized()


	def region_1(self):
	

		
		self.btn2 = QPushButton("Sample", self)
		self.btn2.clicked.connect(self.show_sample)
		self.btn2.clicked.connect(self.hide_replicate)
		self.btn2.clicked.connect(self.hide_experiment)
		self.btn2.clicked.connect(self.hide_diversity)
		self.btn2.resize(500,90)
		self.btn2.move(0,106)
		self.btn2.setDisabled(True)

		
		self.btn3 = QPushButton("Replicate", self)
		self.btn3.clicked.connect(self.hide_sample)
		self.btn3.clicked.connect(self.show_replicate)
		self.btn3.clicked.connect(self.hide_experiment)
		self.btn3.clicked.connect(self.hide_diversity)
		self.btn3.resize(500,90)
		self.btn3.move(500,106)

		self.btn4 = QPushButton("Experiment", self)
		self.btn4.clicked.connect(self.hide_sample)
		self.btn4.clicked.connect(self.hide_replicate)
		self.btn4.clicked.connect(self.show_experiment)
		self.btn4.clicked.connect(self.hide_diversity)
		self.btn4.resize(500,90)
		self.btn4.move(1000,106)
		
		self.btn5 = QPushButton("Diversity", self)
		self.btn5.clicked.connect(self.hide_sample)
		self.btn5.clicked.connect(self.hide_replicate)
		self.btn5.clicked.connect(self.hide_experiment)
		self.btn5.clicked.connect(self.show_diversity)
		self.btn5.resize(500,90)
		self.btn5.move(1500,106)
		
		#btn6 = QPushButton("Network", self)
		#btn6.resize(500,90)
		#btn6.move(2000,106)
		
		extractAction = QAction(QIcon('zoom.png'), 'Quit', self)
		extractAction.triggered.connect(self.close_application)
		
		
		
		self.toolBar = self.addToolBar("Tools")
		self.toolBar.addAction(extractAction)
		self.toolBar.resize(100,100)
		
		
		self.mz_replicate_label = QLabel("mz intensity sample only",self)
		self.mz_replicate_label.resize(500,100)
		self.mz_replicate_label.move(30,150 + 60)
		self.mz_replicate_label.hide()
		self.btn3.clicked.connect(self.mz_replicate_label.show)
		self.btn4.clicked.connect(self.mz_replicate_label.hide)
		self.btn5.clicked.connect(self.mz_replicate_label.hide)
		self.btn2.clicked.connect(self.mz_replicate_label.hide)
		
		
		self.rt_replicate_label = QLabel("rt intensity sample only",self)
		self.rt_replicate_label.resize(500,100)
		self.rt_replicate_label.move(30,950 + 60)
		self.rt_replicate_label.hide()
		self.btn3.clicked.connect(self.rt_replicate_label.show)

		self.btn4.clicked.connect(self.rt_replicate_label.hide)
		self.btn5.clicked.connect(self.rt_replicate_label.hide)
		self.btn2.clicked.connect(self.rt_replicate_label.hide)
		
		#self.grid = QGridLayout()

		#self.grid.addWidget(self.btn2, 0, 0)
		#self.setLayout(self.grid)

##################### Right hand side of interface (Region 2) #########################


	def region_2(self):
		move_x=60
		self.chooseSample = QLabel("Choose Sample", self)
		self.chooseSample.resize(500,50)
		self.chooseSample.move(3020,150 + move_x)
		
		self.chooseAnalyte = QLabel("Choose Analyte", self)
		self.chooseAnalyte.resize(500,50)
		self.chooseAnalyte.move(3020,275 + move_x)
		
	
		#self.comboBox.currentTextChanged.connect(self.Plot)
		#self.comboBox.currentTextChanged.connect(self.region_2)
		


		self.plotButton = QPushButton("Plot", self)
		self.plotButton.clicked.connect(self.Plot)

		self.plotButton.clicked.connect(self.region_2)

		self.plotButton.resize(500, 90)
		self.plotButton.move(3000,1700)


		self.showBlanks = QLabel("Show Blanks", self)
		self.showBlanks.resize(500,100)
		self.showBlanks.move(3020,450 + move_x)
		
		self.showNull = QLabel("Show Null Data", self)
		self.showNull.resize(500,100)
		self.showNull.move(3020,385 + move_x)

		comboText=self.comboBox.currentText()



		total_df = import_dataframe(input_structure, input_type, comboText)
		total_df['analyte_id'].replace('',np.nan, inplace=True)
		total_df.dropna(subset=['analyte_id'],inplace=True)

		sorted_df = total_df.sort_values(by=['analyte_id'])
		total_df['analyte_id'].replace('',np.nan, inplace=True)
		mz_array=[]
		analyte_array=[]

		for analyte_id in sorted_df.analyte_id.unique():
			mz_array.append([sorted_df[sorted_df["analyte_id"] == analyte_id]["mz"].to_numpy(),
		                     sorted_df[sorted_df["analyte_id"] == analyte_id]["intensity"].to_numpy()])

			analyte_array.append(analyte_id)

		self.comboAnalyte.clear()
		self.comboAnalyte.addItem('Show All')


		n = 0
		while n < len(analyte_array):

			self.comboAnalyte.addItem(str(analyte_array[n]))
			
			n+=1	
		self.comboAnalyte.move(3020, 385)
		self.comboAnalyte.resize(400,50)
		

  



################ Center Left of interface (Region 3) ###################
		
	def region_3(self):
		move_x = 60
		move_y = -15
		
############## Null On Off ####################

		# creating a push button 
		self.Nullbutton = QPushButton("On", self) 

		# setting geometry of button 
		self.Nullbutton.setGeometry(200, 150, 100, 40)
		self.Nullbutton.move(3300,415 + move_x) 

		# setting checkable to true 
		self.Nullbutton.setCheckable(True) 

		# setting calling method by button 

		self.Nullbutton.clicked.connect(self.nullButton)

		# setting default color of button to light-grey 
		self.Nullbutton.setStyleSheet("background-color : lightgreen") 

		# show all the widgets 
		#self.update() 
############## Blank On Off ####################

		# creating a push button 
		self.Blankbutton = QPushButton("On", self) 

		# setting geometry of button 
		self.Blankbutton.setGeometry(200, 150, 100, 40)
		self.Blankbutton.move(3300,475 + move_x) 

		# setting checkable to true 
		self.Blankbutton.setCheckable(True) 

		# setting calling method by button 

		self.Blankbutton.clicked.connect(self.blankButton)

		# setting default color of button to light-grey 
		self.Blankbutton.setStyleSheet("background-color : lightgreen") 

		# show all the widgets 
		#self.update() 


		pg.setConfigOption('background', 'w')
################################################# Sample
		self.mz_plot = pg.PlotWidget(self)
		self.mz_plot.move(20,220 + move_y)
		self.mz_plot.resize(1900,780)
		self.mz_plot.setLabel(axis='bottom',text='mz')
		self.mz_plot.setLabel(axis='left',text='Intensity')
		
		self.rt_plot = pg.PlotWidget(self)
		self.rt_plot.move(20,1020+ move_y)
		self.rt_plot.resize(1900,780)
		self.rt_plot.setLabel(axis='bottom',text='rt')
		self.rt_plot.setLabel(axis='left',text='Intensity')
		
		self.ms1_plot = pg.PlotWidget(self)
		self.ms1_plot.move(1970,220+ move_y)
		self.ms1_plot.resize(1000,780)
		
		self.ms2_plot = pg.PlotWidget(self)
		self.ms2_plot.move(1970,1020+ move_y)
		self.ms2_plot.resize(1000,780)

################################################# Replicate
		move_y = 100
		move_x = 100
############# Blank On Null On #############################
		self.mz_r1_plot = pg.PlotWidget(self)
		self.mz_r1_plot.move(20 + move_x,220 + move_y)
		self.mz_r1_plot.resize(2800,200)
		self.mz_r1_plot.setLabel(axis='bottom',text='mz')
		self.mz_r1_plot.setLabel(axis='left',text='Intensity')
		
		self.mz_r2_plot = pg.PlotWidget(self)
		self.mz_r2_plot.move(20+ move_x,450 + move_y)
		self.mz_r2_plot.resize(2800,200)
		self.mz_r2_plot.setLabel(axis='bottom',text='mz')
		self.mz_r2_plot.setLabel(axis='left',text='Intensity')
		
		self.mz_r3_plot = pg.PlotWidget(self)
		self.mz_r3_plot.move(20+ move_x,680 + move_y)
		self.mz_r3_plot.resize(2800,200)
		self.mz_r3_plot.setLabel(axis='bottom',text='mz')
		self.mz_r3_plot.setLabel(axis='left',text='Intensity')
		
		move_y = 905
		
		self.rt_r1_plot = pg.PlotWidget(self)
		self.rt_r1_plot.move(20+ move_x,220 + move_y)
		self.rt_r1_plot.resize(2800,200)
		self.rt_r1_plot.setLabel(axis='bottom',text='rt')
		self.rt_r1_plot.setLabel(axis='left',text='Intensity')
		
		self.rt_r2_plot = pg.PlotWidget(self)
		self.rt_r2_plot.move(20+ move_x,450 + move_y)
		self.rt_r2_plot.resize(2800,200)
		self.rt_r2_plot.setLabel(axis='bottom',text='rt')
		self.rt_r2_plot.setLabel(axis='left',text='Intensity')
		
		self.rt_r3_plot = pg.PlotWidget(self)
		self.rt_r3_plot.move(20+ move_x,680 + move_y)
		self.rt_r3_plot.resize(2800,200)
		self.rt_r3_plot.setLabel(axis='bottom',text='rt')
		self.rt_r3_plot.setLabel(axis='left',text='Intensity')
	
############# Blank On Null Off #############################

		
		move_y = -15
		self.mz_bOn_nOff_plot = pg.PlotWidget(self)
		self.mz_bOn_nOff_plot.move(20,220 + move_y)
		self.mz_bOn_nOff_plot.resize(1900,780)
		self.mz_bOn_nOff_plot.setLabel(axis='bottom',text='mz')
		self.mz_bOn_nOff_plot.setLabel(axis='left',text='Intensity')
		
		self.rt_bOn_nOff_plot = pg.PlotWidget(self)
		self.rt_bOn_nOff_plot.move(20,1020+ move_y)
		self.rt_bOn_nOff_plot.resize(1900,780)
		self.rt_bOn_nOff_plot.setLabel(axis='bottom',text='rt')
		self.rt_bOn_nOff_plot.setLabel(axis='left',text='Intensity')
		
		move_y = 100
		move_x = 100
		
		self.mz_r1_bOn_nOff_plot = pg.PlotWidget(self)
		self.mz_r1_bOn_nOff_plot.move(20 + move_x,220 + move_y)
		self.mz_r1_bOn_nOff_plot.resize(2800,200)
		self.mz_r1_bOn_nOff_plot.setLabel(axis='bottom',text='mz')
		self.mz_r1_bOn_nOff_plot.setLabel(axis='left',text='Intensity')
		self.mz_r1_bOn_nOff_plot.hide()
			
		self.mz_r2_bOn_nOff_plot = pg.PlotWidget(self)
		self.mz_r2_bOn_nOff_plot.move(20+ move_x,450 + move_y)
		self.mz_r2_bOn_nOff_plot.resize(2800,200)
		self.mz_r2_bOn_nOff_plot.setLabel(axis='bottom',text='mz')
		self.mz_r2_bOn_nOff_plot.setLabel(axis='left',text='Intensity')
		self.mz_r2_bOn_nOff_plot.hide()
		
		self.mz_r3_bOn_nOff_plot = pg.PlotWidget(self)
		self.mz_r3_bOn_nOff_plot.move(20+ move_x,680 + move_y)
		self.mz_r3_bOn_nOff_plot.resize(2800,200)
		self.mz_r3_bOn_nOff_plot.setLabel(axis='bottom',text='mz')
		self.mz_r3_bOn_nOff_plot.setLabel(axis='left',text='Intensity')
		self.mz_r3_bOn_nOff_plot.hide()
		
		move_y = 905
		
		self.rt_r1_bOn_nOff_plot = pg.PlotWidget(self)
		self.rt_r1_bOn_nOff_plot.move(20+ move_x,220 + move_y)
		self.rt_r1_bOn_nOff_plot.resize(2800,200)
		self.rt_r1_bOn_nOff_plot.setLabel(axis='bottom',text='mz')
		self.rt_r1_bOn_nOff_plot.setLabel(axis='left',text='Intensity')
		self.rt_r1_bOn_nOff_plot.hide()
			
		self.rt_r2_bOn_nOff_plot = pg.PlotWidget(self)
		self.rt_r2_bOn_nOff_plot.move(20+ move_x,450 + move_y)
		self.rt_r2_bOn_nOff_plot.resize(2800,200)
		self.rt_r2_bOn_nOff_plot.setLabel(axis='bottom',text='mz')
		self.rt_r2_bOn_nOff_plot.setLabel(axis='left',text='Intensity')
		self.rt_r2_bOn_nOff_plot.hide()
		
		self.rt_r3_bOn_nOff_plot = pg.PlotWidget(self)
		self.rt_r3_bOn_nOff_plot.move(20+ move_x,680 + move_y)
		self.rt_r3_bOn_nOff_plot.resize(2800,200)
		self.rt_r3_bOn_nOff_plot.setLabel(axis='bottom',text='mz')
		self.rt_r3_bOn_nOff_plot.setLabel(axis='left',text='Intensity')
		self.rt_r3_bOn_nOff_plot.hide()
############# Blank Off Null On #############################
		move_y = -15
		self.mz_bOff_nOn_plot = pg.PlotWidget(self)
		self.mz_bOff_nOn_plot.move(20,220 + move_y)
		self.mz_bOff_nOn_plot.resize(1900,780)
		self.mz_bOff_nOn_plot.setLabel(axis='bottom',text='mz')
		self.mz_bOff_nOn_plot.setLabel(axis='left',text='Intensity')
		
		self.rt_bOff_nOn_plot = pg.PlotWidget(self)
		self.rt_bOff_nOn_plot.move(20,1020+ move_y)
		self.rt_bOff_nOn_plot.resize(1900,780)
		self.rt_bOff_nOn_plot.setLabel(axis='bottom',text='rt')
		self.rt_bOff_nOn_plot.setLabel(axis='left',text='Intensity')
		move_y = 100
		move_x = 100
		self.mz_r1_bOff_nOn_plot = pg.PlotWidget(self)
		self.mz_r1_bOff_nOn_plot.move(20 + move_x,220 + move_y)
		self.mz_r1_bOff_nOn_plot.resize(2800,200)
		self.mz_r1_bOff_nOn_plot.setLabel(axis='bottom',text='mz')
		self.mz_r1_bOff_nOn_plot.setLabel(axis='left',text='Intensity')
		self.mz_r1_bOff_nOn_plot.hide()
			
		self.mz_r2_bOff_nOn_plot = pg.PlotWidget(self)
		self.mz_r2_bOff_nOn_plot.move(20+ move_x,450 + move_y)
		self.mz_r2_bOff_nOn_plot.resize(2800,200)
		self.mz_r2_bOff_nOn_plot.setLabel(axis='bottom',text='mz')
		self.mz_r2_bOff_nOn_plot.setLabel(axis='left',text='Intensity')
		self.mz_r2_bOff_nOn_plot.hide()
		
		self.mz_r3_bOff_nOn_plot = pg.PlotWidget(self)
		self.mz_r3_bOff_nOn_plot.move(20+ move_x,680 + move_y)
		self.mz_r3_bOff_nOn_plot.resize(2800,200)
		self.mz_r3_bOff_nOn_plot.setLabel(axis='bottom',text='mz')
		self.mz_r3_bOff_nOn_plot.setLabel(axis='left',text='Intensity')
		self.mz_r3_bOff_nOn_plot.hide()

		move_y = 905
		
		self.rt_r1_bOff_nOn_plot = pg.PlotWidget(self)
		self.rt_r1_bOff_nOn_plot.move(20 + move_x,220 + move_y)
		self.rt_r1_bOff_nOn_plot.resize(2800,200)
		self.rt_r1_bOff_nOn_plot.setLabel(axis='bottom',text='mz')
		self.rt_r1_bOff_nOn_plot.setLabel(axis='left',text='Intensity')
		self.rt_r1_bOff_nOn_plot.hide()
			
		self.rt_r2_bOff_nOn_plot = pg.PlotWidget(self)
		self.rt_r2_bOff_nOn_plot.move(20+ move_x,450 + move_y)
		self.rt_r2_bOff_nOn_plot.resize(2800,200)
		self.rt_r2_bOff_nOn_plot.setLabel(axis='bottom',text='mz')
		self.rt_r2_bOff_nOn_plot.setLabel(axis='left',text='Intensity')
		self.rt_r2_bOff_nOn_plot.hide()
		
		self.rt_r3_bOff_nOn_plot = pg.PlotWidget(self)
		self.rt_r3_bOff_nOn_plot.move(20+ move_x,680 + move_y)
		self.rt_r3_bOff_nOn_plot.resize(2800,200)
		self.rt_r3_bOff_nOn_plot.setLabel(axis='bottom',text='mz')
		self.rt_r3_bOff_nOn_plot.setLabel(axis='left',text='Intensity')
		self.rt_r3_bOff_nOn_plot.hide()
		
		
		
############# Blank Off Null Off #############################
		move_y = -15
		self.mz_bOff_nOff_plot = pg.PlotWidget(self)
		self.mz_bOff_nOff_plot.move(20,220 + move_y)
		self.mz_bOff_nOff_plot.resize(1900,780)
		self.mz_bOff_nOff_plot.setLabel(axis='bottom',text='mz')
		self.mz_bOff_nOff_plot.setLabel(axis='left',text='Intensity')
		
		self.rt_bOff_nOff_plot = pg.PlotWidget(self)
		self.rt_bOff_nOff_plot.move(20,1020+ move_y)
		self.rt_bOff_nOff_plot.resize(1900,780)
		self.rt_bOff_nOff_plot.setLabel(axis='bottom',text='rt')
		self.rt_bOff_nOff_plot.setLabel(axis='left',text='Intensity')
		move_y = 100
		move_x = 100
		self.mz_r1_bOff_nOff_plot = pg.PlotWidget(self)
		self.mz_r1_bOff_nOff_plot.move(20 + move_x,220 + move_y)
		self.mz_r1_bOff_nOff_plot.resize(2800,200)
		self.mz_r1_bOff_nOff_plot.setLabel(axis='bottom',text='mz')
		self.mz_r1_bOff_nOff_plot.setLabel(axis='left',text='Intensity')
		self.mz_r1_bOff_nOff_plot.hide()
			
		self.mz_r2_bOff_nOff_plot = pg.PlotWidget(self)
		self.mz_r2_bOff_nOff_plot.move(20+ move_x,450 + move_y)
		self.mz_r2_bOff_nOff_plot.resize(2800,200)
		self.mz_r2_bOff_nOff_plot.setLabel(axis='bottom',text='mz')
		self.mz_r2_bOff_nOff_plot.setLabel(axis='left',text='Intensity')
		self.mz_r2_bOff_nOff_plot.hide()
		
		self.mz_r3_bOff_nOff_plot = pg.PlotWidget(self)
		self.mz_r3_bOff_nOff_plot.move(20+ move_x,680 + move_y)
		self.mz_r3_bOff_nOff_plot.resize(2800,200)
		self.mz_r3_bOff_nOff_plot.setLabel(axis='bottom',text='mz')
		self.mz_r3_bOff_nOff_plot.setLabel(axis='left',text='Intensity')
		self.mz_r3_bOff_nOff_plot.hide()

		move_y = 905
		
		self.rt_r1_bOff_nOff_plot = pg.PlotWidget(self)
		self.rt_r1_bOff_nOff_plot.move(20 + move_x,220 + move_y)
		self.rt_r1_bOff_nOff_plot.resize(2800,200)
		self.rt_r1_bOff_nOff_plot.setLabel(axis='bottom',text='mz')
		self.rt_r1_bOff_nOff_plot.setLabel(axis='left',text='Intensity')
		self.rt_r1_bOff_nOff_plot.hide()
			
		self.rt_r2_bOff_nOff_plot = pg.PlotWidget(self)
		self.rt_r2_bOff_nOff_plot.move(20+ move_x,450 + move_y)
		self.rt_r2_bOff_nOff_plot.resize(2800,200)
		self.rt_r2_bOff_nOff_plot.setLabel(axis='bottom',text='mz')
		self.rt_r2_bOff_nOff_plot.setLabel(axis='left',text='Intensity')
		self.rt_r2_bOff_nOff_plot.hide()
		
		self.rt_r3_bOff_nOff_plot = pg.PlotWidget(self)
		self.rt_r3_bOff_nOff_plot.move(20+ move_x,680 + move_y)
		self.rt_r3_bOff_nOff_plot.resize(2800,200)
		self.rt_r3_bOff_nOff_plot.setLabel(axis='bottom',text='mz')
		self.rt_r3_bOff_nOff_plot.setLabel(axis='left',text='Intensity')
		self.rt_r3_bOff_nOff_plot.hide()


############# Experiment Blank On #############################
		move_y = -15
		self.ex_bOn_plot = pg.PlotWidget(self)
		self.ex_bOn_plot.move(60,250 + move_y)
		#limit = pg.LinearRegionItem([100,100])
		#limit.setZValue(-10)
		#self.ex_bOn_plot.addItem(limit)
		if len(sample_names) < 16:
			self.ex_bOn_plot.resize(2900,100*len(sample_names))
		else:
			self.ex_bOn_plot.resize(2900,1500)
			self.ex_bOn_plot.setYRange(0 , 15 , padding =0)
		self.ex_bOn_plot.setLabel(axis='bottom',text='Max Mass')

		#scroll_bar=QScrollBar()
		#scroll_bar.setValue(60)
		#self.ex_bOn_plot.addScrollBarWidget(scroll_bar, Qt.AlignLeft)



############# Experiment Blank Off #############################
		move_y = -15
		self.ex_bOff_plot = pg.PlotWidget(self)
		self.ex_bOff_plot.move(60,250 + move_y)
		if len(sample_names) < 16:
			self.ex_bOff_plot.resize(2900,100*len(sample_names))
		else:
			self.ex_bOff_plot.resize(2900,1500)
			self.ex_bOn_plot.setYRange(0 , 15 , padding =0)
		self.ex_bOff_plot.setLabel(axis='bottom',text='Max Mass')
################### Plots #################################
	
	def Plot(self):
	


		comboText=self.comboBox.currentText()
		

	
		
		mz_blankOff_nullOff_array = import_mz_blankOff_nullOff(input_structure, input_type, comboText)
		
		############### Fetch data for mz_plot and plot sample from comboBox ###############
		total_df = import_dataframe(input_structure, input_type, comboText)

		total_df=total_df[total_df.replicate != 2]
		total_df=total_df[total_df.replicate != 3]
		sorted_df = total_df.sort_values(by=['mz'])

		mz_array = []


		for analyte_id in sorted_df.analyte_id.unique():
			mz_array.append([sorted_df[sorted_df["analyte_id"] == analyte_id]["mz"].to_numpy(),
		                     sorted_df[sorted_df["analyte_id"] == analyte_id]["intensity"].to_numpy()])
		                 


		self.mz_plot.clear()
		colour=5
		for analyte in mz_array:


			#symbol_color = random.randint(0, 255)
			x=analyte[0]
			y=analyte[1]

			self.mz_plot.plot(title= "Test", x=x, y=y, pen=None, symbolPen=pg.intColor(colour, hues=20, values=5), symbolBrush=pg.intColor(colour,hues=20,values=5),symbol='o', symbolSize=4)
			colour+=1


		############### Fetch data for rt plot and plot sample from comboBox ###############

		
		total_df = import_dataframe(input_structure, input_type, comboText)

		total_df=total_df[total_df.replicate != 2]
		total_df=total_df[total_df.replicate != 3]
		sorted_df = total_df.sort_values(by=['rt'])

		#print(sorted_replicate_df.loc['2'])
		
		rt_array = []
		
		for analyte_id in sorted_df.analyte_id.unique():
			rt_array.append([sorted_df[sorted_df["analyte_id"] == analyte_id]["rt"].to_numpy(),
		                     sorted_df[sorted_df["analyte_id"] == analyte_id]["intensity"].to_numpy()])



		self.rt_plot.clear()
		colour = 5
		for analyte in rt_array:

			symbol_color = random.randint(0, 255)
			x=analyte[0]
			y=analyte[1]


			self.rt_plot.plot(title= "Test", x=x, y=y, pen=None, symbolPen=pg.intColor(colour, hues=20, values=5), symbolBrush=pg.intColor(colour, hues=20,values=5),symbol='o', symbolSize=4)
			colour+=1
			
			
######################## Replicate Level Plot ########################
		total_df = import_dataframe(input_structure, input_type, comboText)

		total_df=total_df[total_df.replicate != 2]
		total_df=total_df[total_df.replicate != 3]
		sorted_df = total_df.sort_values(by=['mz'])
		mz_array = []


		for analyte_id in sorted_df.analyte_id.unique():
			mz_array.append([sorted_df[sorted_df["analyte_id"] == analyte_id]["mz"].to_numpy(),
		                     sorted_df[sorted_df["analyte_id"] == analyte_id]["intensity"].to_numpy()])
		self.mz_r1_plot.clear()
		colour=5
		for analyte in mz_array:


			#symbol_color = random.randint(0, 255)
			x=analyte[0]
			y=analyte[1]

			self.mz_r1_plot.plot(title= "Test", x=x, y=y, pen=None, symbolPen=pg.intColor(colour, hues=20, values=5), symbolBrush=pg.intColor(colour,hues=20,values=5),symbol='o', symbolSize=4)
			colour+=1


#################################################



		total_df = import_dataframe(input_structure, input_type, comboText)

		total_df=total_df[total_df.replicate != 2]
		total_df=total_df[total_df.replicate != 3]
		sorted_df = total_df.sort_values(by=['rt'])

		#print(sorted_replicate_df.loc['2'])
		
		rt_array = []
		
		for analyte_id in sorted_df.analyte_id.unique():
			rt_array.append([sorted_df[sorted_df["analyte_id"] == analyte_id]["rt"].to_numpy(),
		                     sorted_df[sorted_df["analyte_id"] == analyte_id]["intensity"].to_numpy()])

		self.rt_r1_plot.clear()
		colour = 5
		for analyte in rt_array:

			symbol_color = random.randint(0, 255)
			x=analyte[0]
			y=analyte[1]


			self.rt_r1_plot.plot(title= "Test", x=x, y=y, pen=None, symbolPen=pg.intColor(colour, hues=20, values=5), symbolBrush=pg.intColor(colour, hues=20,values=5),symbol='o', symbolSize=4)
			colour+=1



#################################################



		
		total_df = import_dataframe(input_structure, input_type, comboText)

		total_df=total_df[total_df.replicate != 1]
		total_df=total_df[total_df.replicate != 3]
		sorted_df = total_df.sort_values(by=['rt'])


		
		rt_r2_array = []
		
		for analyte_id in sorted_df.analyte_id.unique():
			rt_r2_array.append([sorted_df[sorted_df["analyte_id"] == analyte_id]["rt"].to_numpy(),
		                     sorted_df[sorted_df["analyte_id"] == analyte_id]["intensity"].to_numpy()])

		self.rt_r2_plot.clear()
		colour = 5
		for analyte in rt_r2_array:

			symbol_color = random.randint(0, 255)
			x=analyte[0]
			y=analyte[1]


			self.rt_r2_plot.plot(title= "Test", x=x, y=y, pen=None, symbolPen=pg.intColor(colour, hues=20, values=5), symbolBrush=pg.intColor(colour, hues=20,values=5),symbol='o', symbolSize=4)
			colour+=1



#################################################





		total_df = import_dataframe(input_structure, input_type, comboText)

		total_df=total_df[total_df.replicate != 1]
		total_df=total_df[total_df.replicate != 2]
		sorted_df = total_df.sort_values(by=['rt'])

		#print(sorted_replicate_df.loc['2'])
		
		rt_r3_array = []
		
		for analyte_id in sorted_df.analyte_id.unique():
			rt_r3_array.append([sorted_df[sorted_df["analyte_id"] == analyte_id]["rt"].to_numpy(),
		                     sorted_df[sorted_df["analyte_id"] == analyte_id]["intensity"].to_numpy()])

		self.rt_r3_plot.clear()
		colour = 5
		for analyte in rt_r3_array:

			symbol_color = random.randint(0, 255)
			x=analyte[0]
			y=analyte[1]


			self.rt_r3_plot.plot(title= "Test", x=x, y=y, pen=None, symbolPen=pg.intColor(colour, hues=20, values=5), symbolBrush=pg.intColor(colour, hues=20,values=5),symbol='o', symbolSize=4)
			colour+=1



#################################################




		total_df = import_dataframe(input_structure, input_type, comboText)

		total_df=total_df[total_df.replicate != 1]
		total_df=total_df[total_df.replicate != 3]
		sorted_df = total_df.sort_values(by=['mz'])

		mz_r2_array = []


		for analyte_id in sorted_df.analyte_id.unique():
			mz_r2_array.append([sorted_df[sorted_df["analyte_id"] == analyte_id]["mz"].to_numpy(),
		                     sorted_df[sorted_df["analyte_id"] == analyte_id]["intensity"].to_numpy()])

		self.mz_r2_plot.clear()
		colour = 5
		for analyte in mz_r2_array:

			symbol_color = random.randint(0, 255)
			x=analyte[0]
			y=analyte[1]


			self.mz_r2_plot.plot(title= "Test", x=x, y=y, pen=None, symbolPen=pg.intColor(colour, hues=20, values=5), symbolBrush=pg.intColor(colour, hues=20,values=5),symbol='o', symbolSize=4)
			colour+=1




#################################################





		total_df = import_dataframe(input_structure, input_type, comboText)

		total_df=total_df[total_df.replicate != 1]
		total_df=total_df[total_df.replicate != 2]
		sorted_df = total_df.sort_values(by=['mz'])
		#print(sorted_df)
		mz_r3_array = []


		for analyte_id in sorted_df.analyte_id.unique():
			mz_r3_array.append([sorted_df[sorted_df["analyte_id"] == analyte_id]["mz"].to_numpy(),
		                     sorted_df[sorted_df["analyte_id"] == analyte_id]["intensity"].to_numpy()])

		self.mz_r3_plot.clear()
		colour = 5
		for analyte in mz_r3_array:

			symbol_color = random.randint(0, 255)
			x=analyte[0]
			y=analyte[1]


			self.mz_r3_plot.plot(title= "Test", x=x, y=y, pen=None, symbolPen=pg.intColor(colour, hues=20, values=5), symbolBrush=pg.intColor(colour, hues=20,values=5),symbol='o', symbolSize=4)
			colour+=1
			
############ Data frame containing Null Off, Blank On data and Plot


######### mz_r1, rt_r1 Data

		total_df = import_dataframe(input_structure, input_type, comboText)
		#print(total_df.analyte_id)
		total_df = total_df.dropna(subset=['analyte_id'])
		#df = total_df[total_df.blank_analyte !=False]
		#print(total_df.analyte_id)
		#total_df = total_df['analyte_id'].replace('',np.nan, inplace=True)
		#print(total_df)
		#total_df.dropna(subset=['blank_analyte'],inplace=True)


		#total_df = total_df.dropna(subset=['analyte_id'],inplace=True)
		#total_df=total_df[total_df.analyte_id != ]
		#total_test_df = total_df.analyte_id
		#print(total_test_df)
		total_df=total_df[total_df.replicate != 2]
		sorted_replicate_df=total_df[total_df.replicate != 3]
		#total_df.drop('1',inplace=True)



		sorted_rt_df = sorted_replicate_df.sort_values(by=['rt'])
		sorted_mz_df = sorted_replicate_df.sort_values(by=['mz'])

		mz_array_NullOff = []
		




		for analyte_id in sorted_mz_df.analyte_id.unique():
			mz_array_NullOff.append([sorted_mz_df[sorted_mz_df["analyte_id"] == analyte_id]["mz"].to_numpy(),
		                     sorted_mz_df[sorted_mz_df["analyte_id"] == analyte_id]["intensity"].to_numpy()])
		                     
		                     
		self.mz_r1_bOn_nOff_plot.clear()
		colour=5
		for analyte in mz_array_NullOff:


			#symbol_color = random.randint(0, 255)
			x=analyte[0]
			y=analyte[1]

			self.mz_r1_bOn_nOff_plot.plot(title= "Test", x=x, y=y, pen=None, symbolPen=pg.intColor(colour, hues=20, values=5), symbolBrush=pg.intColor(colour,hues=20,values=5),symbol='o', symbolSize=4)
			colour+=1
			
		for analyte in mz_array_NullOff:


			#symbol_color = random.randint(0, 255)
			x=analyte[0]
			y=analyte[1]

			self.mz_bOn_nOff_plot.plot(title= "Test", x=x, y=y, pen=None, symbolPen=pg.intColor(colour, hues=20, values=5), symbolBrush=pg.intColor(colour,hues=20,values=5),symbol='o', symbolSize=4)
			colour+=1
		
		rt_array_NullOff = []
		for analyte_id in sorted_rt_df.analyte_id.unique():
			rt_array_NullOff.append([sorted_rt_df[sorted_rt_df["analyte_id"] == analyte_id]["rt"].to_numpy(),
		                     sorted_rt_df[sorted_rt_df["analyte_id"] == analyte_id]["intensity"].to_numpy()])
		self.rt_r1_bOn_nOff_plot.clear()
		colour=5
		for analyte in rt_array_NullOff:


			#symbol_color = random.randint(0, 255)
			x=analyte[0]
			y=analyte[1]

			self.rt_r1_bOn_nOff_plot.plot(title= "Test", x=x, y=y, pen=None, symbolPen=pg.intColor(colour, hues=20, values=5), symbolBrush=pg.intColor(colour,hues=20,values=5),symbol='o', symbolSize=4)
			colour+=1
			
		for analyte in rt_array_NullOff:


			#symbol_color = random.randint(0, 255)
			x=analyte[0]
			y=analyte[1]

			self.rt_bOn_nOff_plot.plot(title= "Test", x=x, y=y, pen=None, symbolPen=pg.intColor(colour, hues=20, values=5), symbolBrush=pg.intColor(colour,hues=20,values=5),symbol='o', symbolSize=4)
			colour+=1
			
######### mz_r2, rt_r2 Data

		total_df = import_dataframe(input_structure, input_type, comboText)




		total_df = total_df.dropna(subset=['analyte_id'])
		sorted_replicate_df=total_df.set_index(['replicate'])
		sorted_replicate_df = sorted_replicate_df.loc['2']




		#print(total_df)
		sorted_rt_df = sorted_replicate_df.sort_values(by=['rt'])
		sorted_df = sorted_replicate_df.sort_values(by=['mz'])

		mz_array_NullOff = []




		for analyte_id in sorted_df.analyte_id.unique():
			mz_array_NullOff.append([sorted_df[sorted_df["analyte_id"] == analyte_id]["mz"].to_numpy(),
		                     sorted_df[sorted_df["analyte_id"] == analyte_id]["intensity"].to_numpy()])
		self.mz_r2_bOn_nOff_plot.clear()
		colour=5
		for analyte in mz_array_NullOff:


			#symbol_color = random.randint(0, 255)
			x=analyte[0]
			y=analyte[1]

			self.mz_r2_bOn_nOff_plot.plot(title= "Test", x=x, y=y, pen=None, symbolPen=pg.intColor(colour, hues=20, values=5), symbolBrush=pg.intColor(colour,hues=20,values=5),symbol='o', symbolSize=4)
			colour+=1
			
		rt_array_NullOff = []
		for analyte_id in sorted_rt_df.analyte_id.unique():
			rt_array_NullOff.append([sorted_rt_df[sorted_rt_df["analyte_id"] == analyte_id]["rt"].to_numpy(),
		                     sorted_rt_df[sorted_rt_df["analyte_id"] == analyte_id]["intensity"].to_numpy()])
		self.rt_r2_bOn_nOff_plot.clear()
		colour=5
		for analyte in rt_array_NullOff:


			#symbol_color = random.randint(0, 255)
			x=analyte[0]
			y=analyte[1]

			self.rt_r2_bOn_nOff_plot.plot(title= "Test", x=x, y=y, pen=None, symbolPen=pg.intColor(colour, hues=20, values=5), symbolBrush=pg.intColor(colour,hues=20,values=5),symbol='o', symbolSize=4)
			colour+=1

######### mz_r3, rt_r3 Data

		total_df = import_dataframe(input_structure, input_type, comboText)




		total_df = total_df.dropna(subset=['analyte_id'])
		sorted_replicate_df=total_df.set_index(['replicate'])
		sorted_replicate_df = sorted_replicate_df.loc['3']




		#print(total_df)
		sorted_df = sorted_replicate_df.sort_values(by=['mz'])
		sorted_rt_df = sorted_replicate_df.sort_values(by=['rt'])
		mz_array_NullOff = []




		for analyte_id in sorted_df.analyte_id.unique():
			mz_array_NullOff.append([sorted_df[sorted_df["analyte_id"] == analyte_id]["mz"].to_numpy(),
		                     sorted_df[sorted_df["analyte_id"] == analyte_id]["intensity"].to_numpy()])
		self.mz_r3_bOn_nOff_plot.clear()
		colour=5
		for analyte in mz_array_NullOff:


			#symbol_color = random.randint(0, 255)
			x=analyte[0]
			y=analyte[1]

			self.mz_r3_bOn_nOff_plot.plot(title= "Test", x=x, y=y, pen=None, symbolPen=pg.intColor(colour, hues=20, values=5), symbolBrush=pg.intColor(colour,hues=20,values=5),symbol='o', symbolSize=4)
			colour+=1

		rt_array_NullOff = []
		for analyte_id in sorted_rt_df.analyte_id.unique():
			rt_array_NullOff.append([sorted_rt_df[sorted_rt_df["analyte_id"] == analyte_id]["rt"].to_numpy(),
		                     sorted_rt_df[sorted_rt_df["analyte_id"] == analyte_id]["intensity"].to_numpy()])
		self.rt_r3_bOn_nOff_plot.clear()
		colour=5
		for analyte in rt_array_NullOff:


			#symbol_color = random.randint(0, 255)
			x=analyte[0]
			y=analyte[1]

			self.rt_r3_bOn_nOff_plot.plot(title= "Test", x=x, y=y, pen=None, symbolPen=pg.intColor(colour, hues=20, values=5), symbolBrush=pg.intColor(colour,hues=20,values=5),symbol='o', symbolSize=4)
			colour+=1
			

############ Data frame containing Null On, Blank Off data

######### mz_r1, rt_r1 Data

		total_df = import_dataframe(input_structure, input_type, comboText)





		total_df=total_df[total_df.replicate != 3]
		total_df=total_df[total_df.replicate != 2]
		total_df=total_df[total_df.blank_analyte != True]



		#print(sort)
		sorted_rt_df = total_df.sort_values(by=['rt'])
		sorted_mz_df = total_df.sort_values(by=['mz'])

		mz_array_NOn_BOff = []
		




		for analyte_id in sorted_mz_df.analyte_id.unique():
			mz_array_NOn_BOff.append([sorted_mz_df[sorted_mz_df["analyte_id"] == analyte_id]["mz"].to_numpy(),
		                     sorted_mz_df[sorted_mz_df["analyte_id"] == analyte_id]["intensity"].to_numpy()])
		                     
		                 

		self.mz_bOff_nOn_plot.clear()
		colour=5
		for analyte in mz_array_NullOff:


			#symbol_color = random.randint(0, 255)
			x=analyte[0]
			y=analyte[1]

			self.mz_bOff_nOn_plot.plot(title= "Test", x=x, y=y, pen=None, symbolPen=pg.intColor(colour, hues=20, values=5), symbolBrush=pg.intColor(colour,hues=20,values=5),symbol='o', symbolSize=4)
			colour+=1


		rt_array_NOn_BOff = []
		for analyte_id in sorted_rt_df.analyte_id.unique():
			rt_array_NOn_BOff.append([sorted_rt_df[sorted_rt_df["analyte_id"] == analyte_id]["rt"].to_numpy(),
		                     sorted_rt_df[sorted_rt_df["analyte_id"] == analyte_id]["intensity"].to_numpy()])



		self.mz_r1_bOff_nOn_plot.clear()
		colour=5
		for analyte in mz_array_NullOff:


			#symbol_color = random.randint(0, 255)
			x=analyte[0]
			y=analyte[1]

			self.mz_r1_bOff_nOn_plot.plot(title= "Test", x=x, y=y, pen=None, symbolPen=pg.intColor(colour, hues=20, values=5), symbolBrush=pg.intColor(colour,hues=20,values=5),symbol='o', symbolSize=4)
			colour+=1

		
		mz_array_NOn_BOff = []
		for analyte_id in sorted_rt_df.analyte_id.unique():
			mz_array_NOn_BOff.append([sorted_rt_df[sorted_rt_df["analyte_id"] == analyte_id]["rt"].to_numpy(),
		                     sorted_rt_df[sorted_rt_df["analyte_id"] == analyte_id]["intensity"].to_numpy()])
		self.rt_bOff_nOn_plot.clear()
		colour=5
		for analyte in mz_array_NOn_BOff:


			#symbol_color = random.randint(0, 255)
			x=analyte[0]
			y=analyte[1]

			self.rt_bOff_nOn_plot.plot(title= "Test", x=x, y=y, pen=None, symbolPen=pg.intColor(colour, hues=20, values=5), symbolBrush=pg.intColor(colour,hues=20,values=5),symbol='o', symbolSize=4)
			colour+=1
		self.rt_r1_bOff_nOn_plot.clear()
		colour=5
		for analyte in mz_array_NOn_BOff:


			#symbol_color = random.randint(0, 255)
			x=analyte[0]
			y=analyte[1]

			self.rt_r1_bOff_nOn_plot.plot(title= "Test", x=x, y=y, pen=None, symbolPen=pg.intColor(colour, hues=20, values=5), symbolBrush=pg.intColor(colour,hues=20,values=5),symbol='o', symbolSize=4)
			colour+=1
			
####### #####################r2 Data
		total_df = import_dataframe(input_structure, input_type, comboText)





		total_df=total_df[total_df.replicate != 3]
		total_df=total_df[total_df.replicate != 1]
		total_df=total_df[total_df.blank_analyte != True]



		#print(sort)
		sorted_rt_df = total_df.sort_values(by=['rt'])
		sorted_mz_df = total_df.sort_values(by=['mz'])

		mz_array_NOn_BOff = []
		
		self.mz_r2_bOff_nOn_plot.clear()
		colour=5
		for analyte in mz_array_NullOff:


			#symbol_color = random.randint(0, 255)
			x=analyte[0]
			y=analyte[1]

			self.mz_r2_bOff_nOn_plot.plot(title= "Test", x=x, y=y, pen=None, symbolPen=pg.intColor(colour, hues=20, values=5), symbolBrush=pg.intColor(colour,hues=20,values=5),symbol='o', symbolSize=4)
			colour+=1

		
		mz_array_NOn_BOff = []
		for analyte_id in sorted_rt_df.analyte_id.unique():
			mz_array_NOn_BOff.append([sorted_rt_df[sorted_rt_df["analyte_id"] == analyte_id]["rt"].to_numpy(),
		                     sorted_rt_df[sorted_rt_df["analyte_id"] == analyte_id]["intensity"].to_numpy()])
		self.rt_r2_bOff_nOn_plot.clear()
		colour=5
		for analyte in mz_array_NOn_BOff:


			#symbol_color = random.randint(0, 255)
			x=analyte[0]
			y=analyte[1]

			self.rt_r2_bOff_nOn_plot.plot(title= "Test", x=x, y=y, pen=None, symbolPen=pg.intColor(colour, hues=20, values=5), symbolBrush=pg.intColor(colour,hues=20,values=5),symbol='o', symbolSize=4)
			colour+=1

####### #####################r3 Data
		total_df = import_dataframe(input_structure, input_type, comboText)





		total_df=total_df[total_df.replicate != 2]
		total_df=total_df[total_df.replicate != 1]
		total_df=total_df[total_df.blank_analyte != True]



		#print(sort)
		sorted_rt_df = total_df.sort_values(by=['rt'])
		sorted_mz_df = total_df.sort_values(by=['mz'])

		mz_array_NOn_BOff = []
		
		self.mz_r3_bOff_nOn_plot.clear()
		colour=5
		for analyte in mz_array_NullOff:


			#symbol_color = random.randint(0, 255)
			x=analyte[0]
			y=analyte[1]

			self.mz_r3_bOff_nOn_plot.plot(title= "Test", x=x, y=y, pen=None, symbolPen=pg.intColor(colour, hues=20, values=5), symbolBrush=pg.intColor(colour,hues=20,values=5),symbol='o', symbolSize=4)
			colour+=1

		
		mz_array_NOn_BOff = []
		for analyte_id in sorted_rt_df.analyte_id.unique():
			mz_array_NOn_BOff.append([sorted_rt_df[sorted_rt_df["analyte_id"] == analyte_id]["rt"].to_numpy(),
		                     sorted_rt_df[sorted_rt_df["analyte_id"] == analyte_id]["intensity"].to_numpy()])
		self.rt_r3_bOff_nOn_plot.clear()
		colour=5
		for analyte in mz_array_NOn_BOff:


			#symbol_color = random.randint(0, 255)
			x=analyte[0]
			y=analyte[1]

			self.rt_r3_bOff_nOn_plot.plot(title= "Test", x=x, y=y, pen=None, symbolPen=pg.intColor(colour, hues=20, values=5), symbolBrush=pg.intColor(colour,hues=20,values=5),symbol='o', symbolSize=4)
			colour+=1

########### Data frame containing Null Off, Blank Off data

######### mz_r1, rt_r1 Data

		total_df = import_dataframe(input_structure, input_type, comboText)

		total_df = total_df.dropna(subset=['analyte_id'])



		total_df=total_df[total_df.replicate != 3]
		total_df=total_df[total_df.replicate != 2]
		total_df=total_df[total_df.blank_analyte != True]



		#print(sort)
		sorted_rt_df = total_df.sort_values(by=['rt'])
		sorted_mz_df = total_df.sort_values(by=['mz'])

		mz_array_NOff_BOff = []
		




		for analyte_id in sorted_mz_df.analyte_id.unique():
			mz_array_NOff_BOff.append([sorted_mz_df[sorted_mz_df["analyte_id"] == analyte_id]["mz"].to_numpy(),
		                     sorted_mz_df[sorted_mz_df["analyte_id"] == analyte_id]["intensity"].to_numpy()])
		                     
		                 

		self.mz_bOff_nOff_plot.clear()
		colour=5
		for analyte in mz_array_NullOff:


			#symbol_color = random.randint(0, 255)
			x=analyte[0]
			y=analyte[1]

			self.mz_bOff_nOff_plot.plot(title= "Test", x=x, y=y, pen=None, symbolPen=pg.intColor(colour, hues=20, values=5), symbolBrush=pg.intColor(colour,hues=20,values=5),symbol='o', symbolSize=4)
			colour+=1





		self.mz_r1_bOff_nOff_plot.clear()
		colour=5
		for analyte in mz_array_NOff_BOff:


			#symbol_color = random.randint(0, 255)
			x=analyte[0]
			y=analyte[1]

			self.mz_r1_bOff_nOff_plot.plot(title= "Test", x=x, y=y, pen=None, symbolPen=pg.intColor(colour, hues=20, values=5), symbolBrush=pg.intColor(colour,hues=20,values=5),symbol='o', symbolSize=4)
			colour+=1

		mz_array_NOff_BOff = []
		for analyte_id in sorted_rt_df.analyte_id.unique():
			mz_array_NOff_BOff.append([sorted_rt_df[sorted_rt_df["analyte_id"] == analyte_id]["rt"].to_numpy(),
		                     sorted_rt_df[sorted_rt_df["analyte_id"] == analyte_id]["intensity"].to_numpy()])


		self.rt_bOff_nOff_plot.clear()
		colour=5
		for analyte in mz_array_NOff_BOff:


			#symbol_color = random.randint(0, 255)
			x=analyte[0]
			y=analyte[1]

			self.rt_bOff_nOff_plot.plot(title= "Test", x=x, y=y, pen=None, symbolPen=pg.intColor(colour, hues=20, values=5), symbolBrush=pg.intColor(colour,hues=20,values=5),symbol='o', symbolSize=4)
			colour+=1
		for analyte_id in sorted_rt_df.analyte_id.unique():
			mz_array_NOff_BOff.append([sorted_rt_df[sorted_rt_df["analyte_id"] == analyte_id]["rt"].to_numpy(),
		                     sorted_rt_df[sorted_rt_df["analyte_id"] == analyte_id]["intensity"].to_numpy()])


		self.rt_r1_bOff_nOff_plot.clear()
		colour=5
		for analyte in mz_array_NOn_BOff:


			#symbol_color = random.randint(0, 255)
			x=analyte[0]
			y=analyte[1]

			self.rt_r1_bOff_nOff_plot.plot(title= "Test", x=x, y=y, pen=None, symbolPen=pg.intColor(colour, hues=20, values=5), symbolBrush=pg.intColor(colour,hues=20,values=5),symbol='o', symbolSize=4)
			colour+=1
			
####### #####################r2 Data
		total_df = import_dataframe(input_structure, input_type, comboText)

		total_df = total_df.dropna(subset=['analyte_id'])



		total_df=total_df[total_df.replicate != 3]
		total_df=total_df[total_df.replicate != 1]
		total_df=total_df[total_df.blank_analyte != True]



		#print(sort)
		sorted_rt_df = total_df.sort_values(by=['rt'])
		sorted_mz_df = total_df.sort_values(by=['mz'])

		mz_array_NOff_BOff = []
		
		self.mz_r2_bOff_nOff_plot.clear()
		colour=5
		for analyte in mz_array_NullOff:


			#symbol_color = random.randint(0, 255)
			x=analyte[0]
			y=analyte[1]

			self.mz_r2_bOff_nOff_plot.plot(title= "Test", x=x, y=y, pen=None, symbolPen=pg.intColor(colour, hues=20, values=5), symbolBrush=pg.intColor(colour,hues=20,values=5),symbol='o', symbolSize=4)
			colour+=1

		
		mz_array_NOff_BOff = []
		for analyte_id in sorted_rt_df.analyte_id.unique():
			mz_array_NOff_BOff.append([sorted_rt_df[sorted_rt_df["analyte_id"] == analyte_id]["rt"].to_numpy(),
		                     sorted_rt_df[sorted_rt_df["analyte_id"] == analyte_id]["intensity"].to_numpy()])
		self.rt_r2_bOff_nOff_plot.clear()
		colour=5
		for analyte in mz_array_NOff_BOff:


			#symbol_color = random.randint(0, 255)
			x=analyte[0]
			y=analyte[1]

			self.rt_r2_bOff_nOff_plot.plot(title= "Test", x=x, y=y, pen=None, symbolPen=pg.intColor(colour, hues=20, values=5), symbolBrush=pg.intColor(colour,hues=20,values=5),symbol='o', symbolSize=4)
			colour+=1

####### #####################r3 Data
		total_df = import_dataframe(input_structure, input_type, comboText)

		total_df = total_df.dropna(subset=['analyte_id'])



		total_df=total_df[total_df.replicate != 2]
		total_df=total_df[total_df.replicate != 1]
		total_df=total_df[total_df.blank_analyte != True]



		#print(sort)
		sorted_rt_df = total_df.sort_values(by=['rt'])
		sorted_mz_df = total_df.sort_values(by=['mz'])

		mz_array_NOff_BOff = []
		
		self.mz_r3_bOff_nOff_plot.clear()
		colour=5
		for analyte in mz_array_NullOff:


			#symbol_color = random.randint(0, 255)
			x=analyte[0]
			y=analyte[1]

			self.mz_r3_bOff_nOff_plot.plot(title= "Test", x=x, y=y, pen=None, symbolPen=pg.intColor(colour, hues=20, values=5), symbolBrush=pg.intColor(colour,hues=20,values=5),symbol='o', symbolSize=4)
			colour+=1

		
		mz_array_NOff_BOff = []
		for analyte_id in sorted_rt_df.analyte_id.unique():
			mz_array_NOff_BOff.append([sorted_rt_df[sorted_rt_df["analyte_id"] == analyte_id]["rt"].to_numpy(),
		                     sorted_rt_df[sorted_rt_df["analyte_id"] == analyte_id]["intensity"].to_numpy()])
		self.rt_r3_bOff_nOff_plot.clear()
		colour=5
		for analyte in mz_array_NOff_BOff:


			#symbol_color = random.randint(0, 255)
			x=analyte[0]
			y=analyte[1]

			self.rt_r3_bOff_nOff_plot.plot(title= "Test", x=x, y=y, pen=None, symbolPen=pg.intColor(colour, hues=20, values=5), symbolBrush=pg.intColor(colour,hues=20,values=5),symbol='o', symbolSize=4)
			colour+=1



################################################   Experiment Blank On   ##################################################################

		experiment_df = import_experiment_dataframe(input_structure)

		sample_name_df = experiment_df.sample_name
		sample_name_sorted_df = sample_name_df.drop_duplicates()

		samples = sample_name_sorted_df.values
		print(samples)
		print(len(samples))
		self.ex_bOn_plot.clear()
		i=0
		while i < len(samples):
			experiment_sample_df = experiment_df[experiment_df.sample_name != samples[i]]


			experiment_array_BOn = []


			for experiment_analyte_id in experiment_sample_df.experiment_analyte_id.unique():
				experiment_array_BOn.append([experiment_sample_df[experiment_sample_df["experiment_analyte_id"] == experiment_analyte_id]["experiment_analyte_max_mass"].to_numpy(), 
								experiment_sample_df[experiment_sample_df["experiment_analyte_id"] == experiment_analyte_id]["sample_analyte_max_intensity"].to_numpy()])

			

			colour=5
			for analyte in experiment_array_BOn:



				y=[i]*len(analyte[0])

				x=analyte[0]

				max_int = max(analyte[1])

				test = self.ex_bOn_plot.plot(title= "Test", x=x, y=y, pen=None, symbolPen=pg.intColor(colour, hues=20, values=5), symbolBrush=pg.intColor(colour,hues=20,values=5),symbol='o', symbolSize= 10)
				min_int = 50000
				int_x=40
				if max_int < min_int:
					test.setSymbolSize((max_int/100000)*int_x)
				else:
					test.setSymbolSize((max_int/100000)*4)

				colour+=1

			i+=1


		



		ticks = samples
		ticksdict = dict(enumerate(ticks))
		ax = self.ex_bOn_plot.getAxis('left')
		ax.setTickSpacing(1,1)
		ax.setTicks([ticksdict.items()])
		#print(experiment_array_s1_BOn[1])


################################################   Experiment Blank Off   ##################################################################

		experiment_df = import_experiment_dataframe(input_structure)
		experiment_df=experiment_df[experiment_df.experiment_analyte_is_blank != True]
		print(experiment_df)
		#print(experiment_df)
		sample_name_df = experiment_df.sample_name
		sample_name_sorted_df = sample_name_df.drop_duplicates()
		#sample_name_sorted_df = experiment_df
		#print(sample_name_sorted_df)
		samples = sample_name_sorted_df.values
		print(samples)
		self.ex_bOff_plot.clear()
		i=0
		while i < len(samples):
			experiment_sample_df = experiment_df[experiment_df.sample_name != samples[i]]


			experiment_array_BOff = []

			for experiment_analyte_id in experiment_sample_df.experiment_analyte_id.unique():
				experiment_array_BOff.append([experiment_sample_df[experiment_sample_df["experiment_analyte_id"] == experiment_analyte_id]["experiment_analyte_max_mass"].to_numpy(), 
								experiment_sample_df[experiment_sample_df["experiment_analyte_id"] == experiment_analyte_id]["sample_analyte_max_intensity"].to_numpy()])

			

			colour=5
			for analyte in experiment_array_BOff:



				y=[i]*len(analyte[0])

				x=analyte[0]

				max_int = max(analyte[1])

				test = self.ex_bOff_plot.plot(title= "Test", x=x, y=y, pen=None, symbolPen=pg.intColor(colour, hues=20, values=5), symbolBrush=pg.intColor(colour,hues=20,values=5),symbol='o', symbolSize= 10)
				if max_int < min_int:
					test.setSymbolSize((max_int/100000)*int_x)
				else:
					test.setSymbolSize((max_int/100000)*4)

				colour+=1
			i+=1





		ticks = samples
		ticksdict = dict(enumerate(ticks))
		ax = self.ex_bOff_plot.getAxis('left')
		ax.setTickSpacing(1,1)
		ax.setTicks([ticksdict.items()])
		#print(experiment_array_s1_BOn[1])

##################################################################################################################	

		return 
		
		

################### Connecting Region 1 to Region 3 ###########################



	def nullButton(self):
	    # method called by button 

		# if button is checked 
		if self.Nullbutton.isChecked():
			self.update_tab()
			# setting background color to light-blue 
			self.Nullbutton.setStyleSheet("background-color : lightgrey") 
			self.Nullbutton.setText('Off') 

		# if it is unchecked 
		else: 
			self.update_tab()
			# set background color back to light-grey 
			self.Nullbutton.setStyleSheet("background-color : lightgreen") 
			self.Nullbutton.setText('On')


		
		



	def blankButton(self):

	    # method called by button 

	  
	    # if button is checked 
		if self.Blankbutton.isChecked():
			self.update_tab()
	        # setting background color to light-blue 
			self.Blankbutton.setStyleSheet("background-color : lightgrey") 
			self.Blankbutton.setText('Off') 

	    # if it is unchecked 
		else: 
			self.update_tab()
			# set background color back to light-grey 
			self.Blankbutton.setStyleSheet("background-color : lightgreen") 
			self.Blankbutton.setText('On')


#################### function for updating tabs


	def update_tab(self):

		if self.btn2.isEnabled() == False:
			#print(self.btn2.isEnabled())
			self.Nullbutton.clicked.connect(self.hide_replicate)
			self.Nullbutton.clicked.connect(self.hide_experiment)
			self.Nullbutton.clicked.connect(self.hide_diversity)
			self.Nullbutton.clicked.connect(self.show_sample)
			self.Blankbutton.clicked.connect(self.hide_replicate)
			self.Blankbutton.clicked.connect(self.hide_experiment)
			self.Blankbutton.clicked.connect(self.hide_diversity)
			self.Blankbutton.clicked.connect(self.show_sample)

		else:
			pass



		if self.btn3.isEnabled() == False:
			#print(self.btn3.isEnabled())
			self.Nullbutton.clicked.connect(self.hide_sample)
			self.Nullbutton.clicked.connect(self.hide_experiment)
			self.Nullbutton.clicked.connect(self.hide_diversity)
			self.Nullbutton.clicked.connect(self.show_replicate)
			self.Blankbutton.clicked.connect(self.hide_sample)
			self.Blankbutton.clicked.connect(self.hide_experiment)
			self.Blankbutton.clicked.connect(self.hide_diversity)
			self.Blankbutton.clicked.connect(self.show_replicate)


		else:
			pass

		if self.btn4.isEnabled() == False:
			#print(self.btn4.isEnabled())
			self.Nullbutton.clicked.connect(self.hide_replicate)
			self.Nullbutton.clicked.connect(self.hide_sample)
			self.Nullbutton.clicked.connect(self.hide_diversity)
			self.Nullbutton.clicked.connect(self.show_experiment)
			self.Blankbutton.clicked.connect(self.hide_replicate)
			self.Blankbutton.clicked.connect(self.hide_sample)
			self.Blankbutton.clicked.connect(self.hide_diversity)
			self.Blankbutton.clicked.connect(self.show_experiment)
		else:
			pass
			
		if self.btn5.isEnabled() == False:
			#print(self.btn5.isEnabled())
			self.Nullbutton.clicked.connect(self.hide_replicate)
			self.Nullbutton.clicked.connect(self.hide_sample)
			self.Nullbutton.clicked.connect(self.hide_experiment)
			self.Nullbutton.clicked.connect(self.show_diversity)
			self.Blankbutton.clicked.connect(self.hide_replicate)
			self.Blankbutton.clicked.connect(self.hide_experiment)
			self.Blankbutton.clicked.connect(self.hide_sample)
			self.Blankbutton.clicked.connect(self.show_diversity)
		else:
			pass
	def hide_sample(self):

		self.btn2.setEnabled(True)
		self.mz_plot.hide()
		self.rt_plot.hide()
		self.ms1_plot.hide()
		self.ms2_plot.hide()
		self.mz_bOn_nOff_plot.hide()
		self.rt_bOn_nOff_plot.hide()
		self.mz_bOff_nOn_plot.hide()
		self.rt_bOff_nOn_plot.hide()
		self.mz_bOff_nOff_plot.hide()
		self.rt_bOff_nOff_plot.hide()
		
	def show_sample(self):


		self.btn2.setEnabled(False)
		self.btn4.setEnabled(True)
		self.btn5.setEnabled(True)
		self.btn3.setEnabled(True)
		self.Nullbutton.setEnabled(True)
		self.comboBox.setEnabled(True)
		self.ms1_plot.show()
		self.ms2_plot.show()
		if self.Nullbutton.isChecked() == True and self.Blankbutton.isChecked() == False:

			#self.ms1_plot.hide()
			#self.ms2_plot.hide()
			self.mz_bOn_nOff_plot.show()
			self.rt_bOn_nOff_plot.show()

		if self.Nullbutton.isChecked() == False and self.Blankbutton.isChecked() == False:

			self.mz_plot.show()
			self.rt_plot.show()
			#self.ms1_plot.show()
			#self.ms2_plot.show()

		if self.Nullbutton.isChecked() == False and self.Blankbutton.isChecked() == True:

			self.mz_bOff_nOn_plot.show()
			self.rt_bOff_nOn_plot.show()
		if self.Nullbutton.isChecked() == True and self.Blankbutton.isChecked() == True:
			self.mz_bOff_nOff_plot.show()
			self.rt_bOff_nOff_plot.show()
		
		
	def show_replicate(self):

		self.btn3.setEnabled(False)
		self.btn4.setEnabled(True)
		self.btn2.setEnabled(True)
		self.btn5.setEnabled(True)
		self.Nullbutton.setEnabled(True)
		self.comboBox.setEnabled(True)
		if self.Nullbutton.isChecked() == True and self.Blankbutton.isChecked() == False:

			
			self.mz_r1_bOn_nOff_plot.show()
			self.mz_r2_bOn_nOff_plot.show()
			self.mz_r3_bOn_nOff_plot.show()
			self.rt_r1_bOn_nOff_plot.show()
			self.rt_r2_bOn_nOff_plot.show()
			self.rt_r3_bOn_nOff_plot.show()
		if self.Nullbutton.isChecked() == False and self.Blankbutton.isChecked() == False:
			self.mz_r1_plot.show()
			self.mz_r2_plot.show()
			self.mz_r3_plot.show()
			self.rt_r1_plot.show()
			self.rt_r2_plot.show()
			self.rt_r3_plot.show()

		if self.Nullbutton.isChecked() == False and self.Blankbutton.isChecked() == True:

			
			
			self.mz_r1_bOff_nOn_plot.show()
			self.mz_r2_bOff_nOn_plot.show()
			self.mz_r3_bOff_nOn_plot.show()
			self.rt_r1_bOff_nOn_plot.show()
			self.rt_r2_bOff_nOn_plot.show()
			self.rt_r3_bOff_nOn_plot.show()
		if self.Nullbutton.isChecked() == True and self.Blankbutton.isChecked() == True:

			self.mz_r1_bOff_nOff_plot.show()
			self.mz_r2_bOff_nOff_plot.show()
			self.mz_r3_bOff_nOff_plot.show()
			self.rt_r1_bOff_nOff_plot.show()
			self.rt_r2_bOff_nOff_plot.show()
			self.rt_r3_bOff_nOff_plot.show()


	def hide_replicate(self):
		self.mz_r1_plot.hide()
		self.mz_r2_plot.hide()
		self.mz_r3_plot.hide()
		self.rt_r1_plot.hide()
		self.rt_r2_plot.hide()
		self.rt_r3_plot.hide()
		self.mz_r1_bOn_nOff_plot.hide()
		self.mz_r2_bOn_nOff_plot.hide()
		self.mz_r3_bOn_nOff_plot.hide()
		self.rt_r1_bOn_nOff_plot.hide()
		self.rt_r2_bOn_nOff_plot.hide()
		self.rt_r3_bOn_nOff_plot.hide()
		self.mz_r1_bOff_nOn_plot.hide()
		self.mz_r2_bOff_nOn_plot.hide()
		self.mz_r3_bOff_nOn_plot.hide()
		self.rt_r1_bOff_nOn_plot.hide()
		self.rt_r2_bOff_nOn_plot.hide()
		self.rt_r3_bOff_nOn_plot.hide()
		
		self.mz_r1_bOff_nOff_plot.hide()
		self.mz_r2_bOff_nOff_plot.hide()
		self.mz_r3_bOff_nOff_plot.hide()
		self.rt_r1_bOff_nOff_plot.hide()
		self.rt_r2_bOff_nOff_plot.hide()
		self.rt_r3_bOff_nOff_plot.hide()


	def show_experiment(self):

		self.btn4.setEnabled(False)
		self.btn2.setEnabled(True)
		self.btn3.setEnabled(True)
		self.btn5.setEnabled(True)
		self.Nullbutton.setEnabled(False)
		self.comboBox.setEnabled(False)
		self.chooseSample.setEnabled(False)
		self.showNull.setEnabled(False)
		if self.Blankbutton.isChecked() == False:
			self.ex_bOn_plot.show()
			self.ex_bOff_plot.hide()
		if self.Blankbutton.isChecked()  == True:
			self.ex_bOn_plot.hide()
			self.ex_bOff_plot.show()


	def hide_experiment(self):

		self.ex_bOn_plot.hide()
		self.ex_bOff_plot.hide()

	def show_diversity(self):
		self.btn4.setEnabled(True)
		self.btn2.setEnabled(True)
		self.btn3.setEnabled(True)
		self.btn5.setEnabled(False)
		self.Nullbutton.setEnabled(True)
		self.comboBox.setEnabled(True)
	def hide_diversity(self):
		pass



	def close_application(self):
		choice = QMessageBox.question(self, 'Quit',
											"Are you sure you want to quit?",
											QMessageBox.Yes | QMessageBox.No)
		if choice == QMessageBox.Yes:
			print("Closing Application")
			sys.exit()
		else:
			pass
			
		

		
def run():

	app = QApplication(sys.argv)
	GUI = Window()
	sys.exit(app.exec_())
run()
