import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import psycopg2
from psycopg2 import Error
import csv
import os, platform
import datetime
import threading
import serial
import serial.tools.list_ports
import threading 
from threading import Thread, Lock
#from PIL import Image, ImageTk
import time
import tkinter.font as tkFont
import sys
import socket
from ftplib import FTP
gpio_flag = True
try:
   import OPi.GPIO as GPIO   
except(Exception, Error) as error:
         print("Ошибка при попытки работы с GPIO портом:", error)
         gpio_flag = False

   
   

prog_name="Проверка штрих-кодов v.1.2"

#Postgres
userPG="postgres"
passwordPG="postgres"
hostPG="127.0.0.1"
portPG="5432"
databasePG="vm"

#FTP подключение
ftpserver="ftp_vologda.iceberry.local"
ftpuser="BarCode"
ftppass="BarCodePass"
timer_ftp_log_down=3600  #1час

#Настройки программы
collect_base="base1"
timer_collect_down=60.0
timer_log_down=300.0
comp_name=""

#COM порт
#comport="" #значение поумолчанию, СОМ порт отключен
#comraute=9600
#MySerial = None 
port_com_list = []          # Список номеров портов
port_com_raute = []         # Список скоростей портов
port_com_place = []         # Список имен портов
MySerial = {}
codecount = {}
codecount_name = {}
codecount_error = {}
codecount_povtor = {}
com_lb = {}

gpiostop_list = [] # Список портов GPIO для управления отключением
gpiodefect_list = [] # Список портов GPIO для отбраковки
gpiocounter_list = [] # Список портов GPIO получения информации по скорости подачи штрих-кодов для сканирования
defect_time_list = [] # Список времени до фиксации ошибки и отключения линии


# Объявление массива продуктов
#product_name, product_massa, product_barcode, product_stm, product_temperature
array_product = [] 

# Объявление массива сбора
#collect_date, collect_barcode, collect_barcode_one, collect_product_name, collect_base
array_collect = [] 


# Объявление массива лога
#log_date, log_text, log_base, log_place, log_type
array_log = [] 


#if platform.system() == "Windows":
#    name_pk=platform.uname().node
#    ostype="windows"
#else:
#    name_pk=os.uname()[1]   # doesnt work on windows
#    ostype="linux"
fileprogram = os.path.basename(__file__)
filepath = os.path.abspath(__file__).replace(fileprogram, '')    
filenameconfig = filepath+"config.ini"
filenameproduct = filepath+"product.txt"
comp_name = socket.gethostname()

#print(filepath)
#if (ostype=="windows"):
#   filenameconfig = filepath+"config.ini"
#   filenameproduct = filepath+"product.txt"
#else:
#   filenameconfig = "/home/vm/vm/config.ini"
#   filenameproduct = "/home/vm/vm/product.txt"

#Управление потоками
a_lock = Lock()
b_lock = Lock()

#Выход из программы
def exit_programm():
   #if SERIAL_IS_ACTIVE==True:
   #   ser.close()
   #quit()
   sys.exit(1)


#Клонирование списка
def Cloning(li1):
    li_copy = li1[:]
    return li_copy


#Выгрузка таблицы сбора
def collect_down(flagrepeat = ""):
 if len(array_collect)>0:
   try:
      # Подключение к существующей базе данных
      connection = psycopg2.connect(user=userPG,
                                  # пароль, который указали при установке PostgreSQL
                                  password=passwordPG,
                                  host=hostPG,
                                  port=portPG,
                                  database=databasePG)
      array_copy = Cloning(array_collect)
      i = 0
      for row in array_copy:
         cursor = connection.cursor()
         #print(f'{row[0]} {row[1]} {row[2]} {row[3]} {row[4]}')
         #print (f""" INSERT INTO collect (collect_date, collect_barcode, collect_barcode_one, collect_product_name, collect_base) VALUES ('{row[0]}', '{row[1]}', '{row[2]}', '{row[3]}', '{row[4]}') SELECT collect_barcode, collect_date WHERE NOT EXISTS (SELECT 1 FROM COLLECT WHERE collect_barcode='{row[1]}' AND collect_date='{row[0]}');""")
         insert_query = f""" INSERT INTO collect (collect_date, collect_barcode, collect_barcode_one, collect_product_name, collect_base, collect_place) SELECT '{row[0]}', '{row[1]}', '{row[2]}', '{row[3]}', '{row[4]}', '{row[5]}' WHERE NOT EXISTS (SELECT 1 FROM COLLECT WHERE collect_barcode='{row[1]}' AND collect_date='{row[0]}');"""
         cursor.execute(insert_query)
         connection.commit()
         i += 1
      #print('Таблица сканированных кодов загружена. Количество строк:'+str(i))
      now = datetime.datetime.now() 
      collect_date = now.strftime("%Y-%m-%d %H:%M:%S")
      status1_1_lb.config(text ="СБОР:"+collect_date)


   except (Exception, Error) as error:
       print("collect_down: ошибка при работе с PostgreSQL:", error)
       #sys.exit(1)
   finally:
      if connection:
        cursor.close()
        connection.close()
        #print("Соединение с PostgreSQL закрыто")   
 if flagrepeat != "once":
   t1 = threading.Timer(timer_collect_down, collect_down) # after 30 seconds
   t1.daemon = True
   t1.start()

#Выгрузка таблицы лога
def log_down(flagrepeat = ""):
 flagOK = False
 if len(array_log)>0:
   try:
      # Подключение к существующей базе данных
      connection_log = psycopg2.connect(user=userPG,
                                  # пароль, который указали при установке PostgreSQL
                                  password=passwordPG,
                                  host=hostPG,
                                  port=portPG,
                                  database=databasePG)
      array_copy_log = Cloning(array_log)
      i_log = 0
      for row in array_copy_log:
         cursor_log = connection_log.cursor()
         #print(f'{row[0]} {row[1]} {row[2]} {row[3]} {row[4]}')
         #print (f""" INSERT INTO collect (collect_date, collect_barcode, collect_barcode_one, collect_product_name, collect_base) VALUES ('{row[0]}', '{row[1]}', '{row[2]}', '{row[3]}', '{row[4]}') SELECT collect_barcode, collect_date WHERE NOT EXISTS (SELECT 1 FROM COLLECT WHERE collect_barcode='{row[1]}' AND collect_date='{row[0]}');""")
         insert_query_log = f""" INSERT INTO log (log_date, log_text, log_base, log_place, log_type) SELECT '{row[0]}', '{row[1]}', '{row[2]}', '{row[3]}', '{row[4]}' WHERE NOT EXISTS (SELECT 1 FROM log WHERE log_text='{row[1]}' AND log_date='{row[0]}');"""      
         cursor_log.execute(insert_query_log)
         connection_log.commit()
         i_log += 1
      now = datetime.datetime.now() 
      log_date = now.strftime("%Y-%m-%d %H:%M:%S")
      status3_lb.config(text ="ЛОГ:"+log_date)
      #print('Таблица сканированных кодов загружена. Количество строк:'+str(i))


   except (Exception, Error) as error_log:
       print("log_down: ошибка при работе с PostgreSQL:", error_log)
       #sys.exit(1)
   finally:
      if connection_log:
        cursor_log.close()
        connection_log.close()
        #print("Соединение с PostgreSQL закрыто")   
 else:
   flagOK = True
 if flagrepeat!="once":
   t2 = threading.Timer(timer_log_down, log_down) # after 30 seconds
   t2.daemon = True
   t2.start()
 


#Выгрузка лога фтп
def update_log_ftp():
   if len(array_log)>0:      
      #Выгрузка лога
      log_down("once")  
      now = datetime.datetime.now() 
      log_date = now.strftime("%d-%m-%Y")
      ftp_name = log_date+'-'+comp_name+'.csv'
      ftp_full_name = filepath + ftp_name   
      array_copy_log = Cloning(array_log)   
      array_log.clear()
      with open(ftp_full_name, 'w', newline='') as f:
         writer = csv.writer(f,delimiter=";")
         writer.writerows(array_copy_log)
      #Отправка фтп файла
      try:
         ftp = FTP(ftpserver)
         ftp.login(ftpuser,ftppass)
         with open(ftp_full_name, 'rb') as file:
            ftp.storbinary('STOR '+ftp_name, file)
         ftp.quit()   
      finally:
         print("update_log_ftp: выгружен файл фтп: "+ftp_full_name)
   if len(array_collect)>0:       
      #Выгрузка сбора    
      collect_down("once")
      now = datetime.datetime.now() 
      collect_date = now.strftime("%d-%m-%Y")
      ftp_name = collect_date+'-collect-'+comp_name+'.csv'
      ftp_full_name = filepath + ftp_name   
      array_copy_collect = Cloning(array_collect)   
      array_collect.clear()
      with open(ftp_full_name, 'w', newline='') as f:
         writer = csv.writer(f,delimiter=";")
         writer.writerows(array_copy_collect)
      #Отправка фтп файла
      try:
         ftp = FTP(ftpserver)
         ftp.login(ftpuser,ftppass)
         with open(ftp_full_name, 'rb') as file:
            ftp.storbinary('STOR '+ftp_name, file)
         ftp.quit()
      finally:
         print("update_log_ftp: выгружен файл фтп: "+ftp_full_name)   
      #print("Выгружен фтп")

#Таймер выгрузки лога фтп
def ftp_log_down():   
   now = datetime.datetime.now()
   today8am = now.replace(hour=8, minute=0, second=0, microsecond=0)
   today9am = now.replace(hour=9, minute=0, second=0, microsecond=0)
   if now >= today8am and now < today9am:       
      update_log_ftp()
   t3 = threading.Timer(timer_ftp_log_down, ftp_log_down) # after 3600 seconds
   t3.daemon = True
   t3.start()

#Загрудка таблицы товаров
def product_up():
   # Подключение базы данных и заполнение таблиц продуктов
   try:
      # Подключение к существующей базе данных
      connection = psycopg2.connect(user=userPG,
                                  # пароль, который указали при установке PostgreSQL
                                  password=passwordPG,
                                  host=hostPG,
                                  port=portPG,
                                  database=databasePG)
      # Курсор для выполнения операций с базой данных
      cursor = connection.cursor()   
      # Заполнение массива продуктов
      # Выполнение SQL-запроса
      cursor.execute("SELECT product_name, product_massa, product_barcode, product_stm, product_temperature from product;")
      # Получить результат
      for row in cursor:
            array_product.append([row[0],row[1],row[2],row[3],row[4]])
            #print(row[1])
    #print(array_product[0] [0])

    #record = cursor.fetchone()
      now = datetime.datetime.now()     
      bd_date = now.strftime("%Y-%m-%d %H:%M:%S")
      status1_lb.config(text ="БД:"+bd_date)
      #print("Данные таблицы - ", record, "\n")
   except (Exception, Error) as error:
    print("main: не заполнена таблица товаров, ошибка при работе с PostgreSQL", error)
    sys.exit(1)
   finally:
    if connection:
        cursor.close()
        connection.close()
        print("main: таблица товаров заполнена, соединение с PostgreSQL закрыто")


#Загрузка таблицы сбора
def collect_up():
# Подключение базы данных и загрузка таблицы сбора
   try:
    # Подключение к существующей базе данных
    connection = psycopg2.connect(user=userPG,
                                  # пароль, который указали при установке PostgreSQL
                                  password=passwordPG,
                                  host=hostPG,
                                  port=portPG,
                                  database=databasePG)
    # Курсор для выполнения операций с базой данных
    cursor = connection.cursor()   
    # Заполнение массива продуктов
    # Выполнение SQL-запроса
    cursor.execute("SELECT collect_date, collect_barcode, collect_barcode_one, collect_product_name, collect_base, collect_place from collect;")
    # Получить результат
    for row in cursor:
            array_collect.append([row[0],row[1],row[2],row[3],row[4],row[5]])
            #print(row[1])
    #print(array_product[0] [0])

    #record = cursor.fetchone()
    #print("Данные таблицы - ", record, "\n")
    
   except (Exception, Error) as error:
      print("collect_up: таблица сбора не загружена, ошибка при работе с PostgreSQL", error)
      #sys.exit(1)
   finally:
      if connection:
         cursor.close()
         connection.close()
         print("collect_up: таблица сбора обновлена, соединение с PostgreSQL закрыто")

#Поиск в списке
def chk_for_val(lst, key, val):
    i = 0
    for d in lst:
      if d[key]==val:
            return i
      i = i +1
    return -1

#Проверка штрих-кода
def test_barcode(code="", log_place="OS", log_place_name="Ручной"):
      ai1 = "01"
      ai2 = "21"
      ai3 = "93"
      gs1 = ""
      strana = "5"
      sernom = ""
      proverka = ""
      errors = ""
      fai1 = ""
      fai2 = ""
      fai3 = ""
      fstrana = ""
      flag_error = "false"
      n = 0
      secun = 0
      pos = 0

      
      #print(code)
      if (len(code) >= 30):
         #Проверка префикса ai1
         #0104607067932082215BgmZD93ui9+
         fai1 = code[0:2] #(0, 2);
         if (ai1 != fai1):
            errors = "Разделитель №1 " + ai1 + "[" + fai1 + "]; " 
            flag_error = "true"    
         fai2 = code[16:18] #(16, 2);
         if (ai2 != fai2):
            errors = errors +"Разделитель №2 " + ai2 + "[" + fai2 + "]; "              
            flag_error = "true"
         fai3 = code[24:26] #(24, 2);
         if (ai3 != fai3):
            errors = errors + "Разделитель №3 " + ai3 + "[" + fai3 + "]; "
            flag_error = "true"
         fstrana = code[18:19] #(18, 1);
         if (strana != fstrana):
            errors = errors + "Страна " + strana + "[" + fstrana + "]; "  
            flag_error = "true"
         gs1 = code[2:16] #(2, 14);  
         if (gs1[0:1] == "0"):
            gs1 = gs1[1:14]
         #print(gs1)     
         if (errors == ""):
            d = []
            for c in array_product :
               d.extend(c)
            if gs1 not in d:
               errors = "2"+log_place_name+":Марка мороженого не найдена!"
               flag_error = "true"
            else:
               product_name = d[0]
               massa = d[1]
               srokhran = d[4]
               komment = d[3]                                                     
               komment = "Ед.ШК:" + gs1 + " " + komment
               errors = "0"+code+"\n"+log_place_name+":"+komment + "\n" + product_name + "\nМасса:" + str(massa)+" Срок:"+ srokhran
            #pos = array_product.index(gs1)  # Array.IndexOf(scodes, gs1);
            #if (pos != -1):
            #   print(pos)
            #Проверка есть ли ШК в уже отсканированных
            #print (array_collect)     
            now = datetime.datetime.now() 
            collect_date = now.strftime("%Y-%m-%d %H:%M:%S")
            i = 0                     
            i = chk_for_val(array_collect, 1, code)  
            if (i == -1):
               #print("ШК не найден в отсканированных.")
               flag_error = "false" 
               #Запись ШК в отсканированные    
               #print (collect_base)
               a_lock.acquire()  
               array_collect.append([collect_date, code, gs1, product_name, collect_base, log_place_name])
               #log_date, log_text, log_base, log_place, log_type
               array_log.append([collect_date,errors,collect_base,log_place_name,"add"])
               if (log_place=="OS"):
                  i=0
               else:                  
                  i=port_com_list.index(log_place)+1
               global codecount
               codecount[i] = codecount[i]+1
               a_lock.release()
            else:              
               collect_date = array_collect [i] [0]
               collect_product_name = array_collect [i] [3]
               collect_base_alt = array_collect [i] [4]
               errors ="1"+code+"\n"+log_place_name+":Повтор штрих-кода! Место:"+collect_base_alt+" Дата: " + str(collect_date) + "\n" + komment + "\n" + product_name + "\nМасса:" + str(massa) + " Срок:" + srokhran
               flag_error = "true"
               a_lock.acquire()              
               array_log.append([collect_date,errors,collect_base,log_place_name,"repeat"])
               if (log_place=="OS"):
                  i=0
               else:                  
                  i=port_com_list.index(log_place)+1
               global codecount_povtor
               codecount_povtor[i] = codecount_povtor[i]+1
               a_lock.release()

      else:
         if (len(code) != 0):
            errors = code+"\n"+log_place_name+":Длина штрих-кода меньше 30 знаков [" + str(len(code)) + "]"
         errors = "2"+errors
         flag_error = "true"
         now = datetime.datetime.now() 
         collect_date = now.strftime("%Y-%m-%d %H:%M:%S") 
         a_lock.acquire()  
         array_log.append([collect_date,errors,collect_base,log_place_name,"error"])
         if (log_place=="OS"):
            i=0
         else:                  
            i=port_com_list.index(log_place)+1
         global codecount_error
         codecount_error[i] = codecount_error[i]+1
         a_lock.release()
      return errors
      

#Заполнение данных таблицы Product из файла
def product_add():
   # Подключение базы данных и заполнение таблицы product
   try:
      # Подключение к существующей базе данных
      connection = psycopg2.connect(user=userPG,
                                  # пароль, который указали при установке PostgreSQL
                                  password=passwordPG,
                                  host=hostPG,
                                  port=portPG,
                                  database=databasePG)
      
      with open(filenameproduct) as file:
         csvfilereader = csv.reader(file, delimiter="\t")
         # Очистка таблицы
         cursor = connection.cursor()
         insert_query = """ truncate table product"""
         cursor.execute(insert_query)
         connection.commit()
         
         # Счетчик
         i = 0
         for r in csvfilereader:
            #if i == 0:
               #print(f'Файл содержит столбцы: {";".join(r)}')
            #else:
            if i != 0: 
               # Курсор для выполнения операций с базой данных
               if (f'{r[0]}'!=""):
                  cursor = connection.cursor()
                  insert_query = f""" INSERT INTO product (product_name, product_massa, product_barcode, product_temperature, product_stm) VALUES ('{r[0]}', {r[1]}, '{r[2]}', '{r[3]}', '{r[4]}') ON CONFLICT DO NOTHING"""
                  cursor.execute(insert_query)
                  connection.commit()
               #     print(f'{r[0]} {r[1]} {r[2]} - {r[3]}'+f'родился в городе {r[4]}.')
            i += 1
         #print('Таблица загружена. Количество строк:'+str(i))


   except (Exception, Error) as error:
       print("product_add: не заполнена таблица товаров, ошибка при работе с PostgreSQL", error)
       sys.exit(1)
   finally:
      if connection:
        cursor.close()
        connection.close()
        print("product_add: таблица товаров заполнена, cоединение с PostgreSQL закрыто") 


#def  comport_read(str,log_place):
#        str=str.rstrip()
        #Убираю символы GS "\u001d"
#        str = str.replace("\u001d", "")
#        print("--- Читать данные ---:", str)
#        barcode_tf.insert(0, str)
#        test_barcode(str,log_place)
#       return str

#========================================================================

   
#def  comport_read(ser):    
#    if ser.in_waiting:        
#        code="utf-8"
#        str = ser.read(ser.in_waiting).decode(code)
#        str=str.rstrip()
        #Убираю символы GS "\u001d"
#        str = str.replace("\u001d", "")
#        print("--- Читать данные ---:", str)
        #barcode_tf.insert(0, str)
#        log_place = ser.port
#        komment = test_barcode(str, log_place)
#        view_komment(komment)
#        return str
#    else:
#        return None          

def  comport_read(str,log_place,log_place_name):    
        log = test_barcode(str, log_place,log_place_name)
        b_lock.acquire()  
        view_log(log,log_place,log_place_name)
        b_lock.release()

# Класс для работы с СОМ портом
class MSerialPort:
    def __init__(self):
        self.ser = None
        self.serialThread = None
        self.master = None


    
    def serial_thread(self,ser,idport,comport_name):  
                   #   while True: 
                   #    print("222")
                   #    time.sleep(2.5)
        while True: 
            if (ser.is_open):            
               if ser.in_waiting:  
                  try:
                     code="utf-8"
                     str = ""
                     str = ser.read(ser.in_waiting).decode(code)
                     #str = self.ser.readline().decode(code)
                     str = str.rstrip()
                     #Убираю символы GS "\u001d"
                     str = str.replace("\u001d", "")
                     print("--- Читать данные ---:",comport_name,"|",idport,":", str)
                     #barcode_tf.insert(0, str)
                     log_place_id = idport          
                     log_place_name = comport_name             
                  except serial.SerialException as se:
                     print("Ошибка чтения СОМ порта:",comport_name,"|", idport,":",str(se))
                  finally:
                     #comport_read(self.ser)   
                     comport_read(str,log_place_id,log_place_name)
            time.sleep(0.1)

                       
       

                     
   
    #@classmethod
    #def init(cls, master):      
      #cls.master = master
      #cls.serialThread = 
      #threading.Thread(target=cls.serial_thread,
      #                                     args=(cls, master), daemon=False).start()
      #cls.serialThread.start()
      #return cls.serialThread    
    
    @classmethod
    def port_open(self, port, bps):
      try:
        # Откройте последовательный порт
        self.ser = serial.Serial(port, bps, 5)

        if self.ser.is_open:
            print("--- Последовательный порт открыт ---"+str(self.ser.port))
            return self.ser

      except Exception as e:
        print("--- Открытое исключение ---:", e)
        return None   
 
    def port_close(self):
       if self.is_open:
        try:
            self.ser.close()
            print("--- Последовательный порт закрыт ---")
            return 0
        except Exception as e:
            print("--- Закрыть исключение ---:", e)
            return -1
       else:
        print("--- Ошибка ---: последовательный порт не открыт!")
        return -1  
  
 


#================================================================
#Работа с QR кодом
def qrcode_gen(i):
   #img = qrcode.make('01046200326515282151N(rM93M6nW')
   #type(img)
   #img.save(f'c:/222/img.png')
   qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
   qr.add_data('01046200326515282151N(rM93M6nW'+str(i))
   qr.make(fit=True)
   qr_image = qr.make_image(fill_color="black", back_color="white")
   return qr_image


#===================================================================
#Начало программы
# Загрузка файла настроек
try:

   with open(filenameconfig) as fconfig:
      for item in fconfig:
        ch = "="
        #print(item)
        indexOfChar = item.find(ch)
        #print(indexOfChar)
        item = item.strip()
        if ((indexOfChar!=-1) & (item[0]!="#")):
            parname = item[0: indexOfChar]
            #print(parname)
            paramznach = item[indexOfChar + 1: len(item)]
            #print(paramznach)
            if (parname=="ftpserver"):
               ftpserver = paramznach
            if (parname == "ftpuser"):                    
               ftpuser = paramznach
            if (parname == "ftppass"):
               ftppass = paramznach
            if (parname == "com"):
               com = paramznach
               port_com_list = com.split(",")
            if (parname == "comraute"):                    
               comraute = paramznach
               port_com_raute = comraute.split(",")
            if (parname == "complace"):                    
               complace = paramznach
               port_com_place = complace.split(",")             
            if (parname == "userPG"):                    
               userPG = paramznach
            if (parname == "passwordPG"):                    
               passwordPG = paramznach
            if (parname == "hostPG"):                    
               hostPG = paramznach
            if (parname == "portPG"):                    
               portPG = paramznach
            if (parname == "databasePG"):                    
               databasePG = paramznach        
            if (parname == "ftpserver"):                    
               ftpserver = paramznach    
            if (parname == "ftpuser"):                    
               ftpuser = paramznach    
            if (parname == "ftppass"):                    
               ftppass = paramznach 
            if (parname == "collect_base"):                    
               collect_base = paramznach  
            if (parname == "timer_collect_down"):                    
               timer_collect_down = float(paramznach)     
            if (parname == "timer_log_down"):                    
               timer_log_down = float(paramznach)        
            if (parname == "timer_ftp_log_down"):                    
               timer_ftp_log_down = float(paramznach)    
            if (parname == "gpiostop"):                    
               gpiostop = paramznach    
               gpiostop_list = gpiostop.split(",")
            if (parname == "gpiodefect"):                    
               gpiodefect = paramznach    
               gpiodefect_list = gpiodefect.split(",")               
            if (parname == "gpiocounter"):                    
               gpiocounter = paramznach    
               gpiocounter_list = gpiocounter.split(",")
                                                                                                                                                                 
            #print(item)
except (Exception, Error) as error:
    print("Ошибка при попытки чтения файла настроек ("+filenameconfig+"):", error)
    sys.exit(1)





window = Tk()
window.title(prog_name)
window.geometry('1024x530')
#window.attributes("-fullscreen", True)


#Вывод окна статуса приемки данных с экрана и настройка начальный значений
codecount_name[0]="Ручной"
codecount[0]=0
codecount_error[0]=0
codecount_povtor[0]=0
com_lb[0] = Label(
      text=codecount_name[0]
         )         
com_lb[0].place(x=10, y=90, width=120, height=100)
com_lb[0]["bg"] = "#90ee90"

#GPIO инициализация
if (gpio_flag):
   try:
      GPIO.setwarnings(False)
      GPIO.setmode(GPIO.BOARD)   # Код доски
   except(Exception, Error) as error:
            print("Ошибка при попытки работы с GPIO портом:", error)
            gpio_flag = False




#Проверка и открытие СОМ портов
for i in range(len(port_com_list)):   
   
   MySerial[i]=MSerialPort()
   port_status=MySerial[i].port_open(port_com_list[i],port_com_raute[i])
   
   #Заполнение начальный значений сбора
   codecount_name[i+1]=port_com_place[i]
   codecount[i+1]=0
   codecount_error[i+1]=0
   codecount_povtor[i+1]=0
   
   #Настройка времени отключения
   defect_time_list.append('')
   
   #Отображение окон статуса
   com_lb[i+1] = Label(
      text=codecount_name[i+1]
         )         
   com_lb[i+1].place(x=10+((i+1)*130), y=90, width=120, height=100)
   
   #Порт не подключен
   com_lb[i+1]["bg"] = "#C1CDCD"

   if (port_status is not None):

      if (gpio_flag==True):
         #GPIO настройка номеров портов
         try:
            if (gpiodefect_list[i]!=''):
               GPIO.setup(int(gpiodefect_list[i]), GPIO.OUT)
               GPIO.output(int(gpiodefect_list[i]),0)
            if (gpiostop_list[i]!=''):
               GPIO.setup(int(gpiostop_list[i]), GPIO.OUT)
               GPIO.output(int(gpiostop_list[i]),0)
            if (gpiocounter_list[i]!=''):   
               GPIO.setup(int(gpiocounter_list[i]), GPIO.IN)
         except(Exception, Error) as error:
            print("Ошибка при попытки работы c GPIO портом №"+str(i)+":", error)
            gpio_flag=False
         


      #MySerial[i].init(window)
      MySerial[i].serialThread=threading.Thread(target=MySerial[i].serial_thread,
                                           args=(port_status,port_status.port,codecount_name[i+1]), daemon=True)
      MySerial[i].serialThread.setDaemon(True)
      MySerial[i].serialThread.start()
      #Порт подключен
      com_lb[i+1]["bg"] = "#90ee90"




log_lb = Label(
         text=""
         )         
log_lb.place(x=10,y=200, width=1000, height=250)

barcode_lb = Label(
   text="ШК: "
)
barcode_lb.place(x=10, y=10)

 
barcode_tf = Entry(
   
)
barcode_tf.place(x=40, y=10, width=970)


def clear():
    barcode_tf.delete(0, END)

def check_barcode():
    #print("You hit return.")
    code = barcode_tf.get()
    log = test_barcode(code,"OS","Ручной")
    view_log(log,"OS","Ручной")

def view_log(log,log_place,log_place_name):
    if (log_place=="OS"):
      i=0
      igpio=0
    else:
      igpio=port_com_list.index(log_place)
      i=igpio+1
      
    
    status_code=log[0]
    if (status_code=="0"):  #Принят
       log_lb["bg"] = "#90ee90"
       com_lb[i]["bg"]  = "#90ee90"
    if (status_code=="1"): #Повтор
       log_lb["bg"] = "#fad400"
       com_lb[i]["bg"]  = "#fad400"
       #GPIO отбраковать товар
       if (gpio_flag):
          GPIO.output(gpiodefect_list[igpio],1)       
    if (status_code=="2"): #Ошибка
       log_lb["bg"] = "#ff0000"              
       com_lb[i]["bg"]  = "#ff0000"
       #Проверка критичного интервала ошибок, запись текущего времени
       now = datetime.datetime.now()        
       try:
         defect_time_last=defect_time_list[igpio]
       except: 
         defect_time_last='' 
       if (defect_time_last!=''):
         difference = now - datetime.datetime.strptime(defect_time_last,"%Y-%m-%d %H:%M:%S")
         #print(str(difference))
         if (difference.seconds < 3):
            print('Повторяющиеся ошибки в критичном интервале ['+str(difference)+'] на линии:'+port_com_place[igpio])
            #GPIO отбраковать товар
            if (gpio_flag):                           
               GPIO.output(gpiodefect_list[igpio],1)
       defect_time_now = now.strftime("%Y-%m-%d %H:%M:%S")
       defect_time_list[igpio] = defect_time_now        
    log=log[2:len(log)]
    log_lb.config()
    #log_lb.config(text = log)
    now = datetime.datetime.now() 
    log_date = now.strftime("%H:%M:%S")
    global codecount_error
    global codecount_povtor
    global codecount
    com_lb[i].config(text = str(log_place_name)+"\nПринято:"+str(codecount[i])+"\nПовторы:"+str(codecount_povtor[i])+"\nОшибки:"+str(codecount_error[i])+"\n"+log_date)
    clear()


def check_barcode_event(event):
    check_barcode()    


barcode_tf.bind('<Return>', check_barcode_event)

cal_btn_tb = Button(
   text='ПРОВЕРИТЬ',
   command=check_barcode
)
cal_btn_tb.place(x=10, y=40, width=1002, height=45)

cal_btn = Button(
   text='Заполнить товары (csv)',
   command=product_add
)
cal_btn.place(x=720, y=470, width=150, height=30)

cal_btn_col_up = Button(
   text='Загрузить собранные',
   command=collect_up
)
cal_btn_col_up.place(x=565, y=470, width=150,  height=30)

cal_btn_ftp_log_down = Button(
   text='Выгрузка фтп',
   command=update_log_ftp
)
cal_btn_ftp_log_down.place(x=460, y=470, width=100,  height=30)

cal_btn_exit = Button(
   text='Выход',
   command=exit_programm
)
cal_btn_exit.place(x=350, y=470, width=100,  height=30)



komment_lb = Label(
         text="Комментарий:"
         )         
komment_lb.place(x=10, y=450, width=1000, height=25)

status1_lb = Label(
         text="БД:"
         )         
status1_lb.place(x=10, y=507, width=190, height=25)

status1_1_lb = Label(
         text="СБОР:"
         )         
status1_1_lb.place(x=210, y=507, width=190, height=25)

status2_lb = Label(
         text=comp_name
         )         
status2_lb.place(x=410, y=507, width=250, height=25)

status3_lb = Label(
         text="ЛОГ:"
         )         
status3_lb.place(x=760, y=507, width=250, height=25)


SetAdvBox = tk.BooleanVar()

def SetAdvBox_command():
    if SetAdvBox.get() == True:
        cal_btn_ftp_log_down.place(x=460, y=470, width=100,  height=30)
        cal_btn_col_up.place(x=565, y=470, width=150,  height=30)
        cal_btn.place(x=720, y=470, width=150, height=30)
    else:
        cal_btn_ftp_log_down.place_forget()
        cal_btn_col_up.place_forget()
        cal_btn.place_forget()

cal_btn_ftp_log_down.place_forget()
cal_btn_col_up.place_forget()
cal_btn.place_forget()

LogAdvBox=tk.Checkbutton(window)
ft = tkFont.Font(family='Times',size=10)
LogAdvBox["font"] = ft
LogAdvBox["justify"] = "center"
LogAdvBox["text"] = "Расш. лог"
LogAdvBox.place(x=10,y=470,width=70,height=25)
LogAdvBox["offvalue"] = "0"
LogAdvBox["onvalue"] = "1"
#LogAdvBox["command"] = self.LogAdvBox_command


CKSetAdvBox=ttk.Checkbutton(window, text="Доп. функции", variable=SetAdvBox, command=SetAdvBox_command, width=120)
CKSetAdvBox.place(x=900, y=470)



#Загрузка таблицы товаров
product_up()

#Загрузка таблицы сканированных ШК
collect_up()

#Таймер выгрузки отсканированных ШК
collect_down()

#Таймер выгрузки лога
log_down()

#Таймер выгрузки лога фтп
ftp_log_down()




window.mainloop()
