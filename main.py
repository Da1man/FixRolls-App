from kivy.app import App

from kivy.uix.widget import Widget

from kivymd.theming import ThemeManager
from kivymd.label import MDLabel
from kivymd.button import MDRectangleFlatButton, MDRoundFlatButton, MDFillRoundFlatIconButton, MDTextButton, MDRaisedButton
# from kivymd.cards import MDSeparator

from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition, WipeTransition
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.image import AsyncImage 
from kivy.core.window import Window
# Window.size = (360, 640)


from kivymd.bottomsheet import MDListBottomSheet
from kivymd.toast.kivytoast import toast
from kivymd.snackbars import Snackbar


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import sqlite3

screen_manager = None
total_in_cart = 0

#TODO LIST:
'''
1. Вызов функции звонка по вызову Call to us в тулбар меню
Done. 2. Подключение базы данных проекта
2.1 Подключение удаленной базы проекта
Done. 3. Регистрация пользователя
Done. 4. Авторизация пользователя
5. Сохранение заказа пользователя в БД
Done. 6. Открытие окна каталога при логине
7. Отправка письма заказа на почту
Done. 8. Всплывашка подсказки минимального заказа
9. Личные данные пользователя в боковом меню
Done. 10. Вывод товаров из базы данных
11. Страница с личными данными пользователя
'''

product_list = []
cart_list = []



# Import products start
print('Import products from database...')

print('connecting to database')
connect = sqlite3.connect('fixrolls.db')
cursor = connect.cursor()
print('connected')
sql = "SELECT * FROM products"
cursor.execute(sql)

for product_db in cursor.fetchall():
	product_list.append({'id': product_db[0],
							'title': product_db[1],
							'price': product_db[2],
							'img': 'images/' + product_db[3]})
	print ('Product ', product_db, ' add to list')

#Import products end


class CartListing(GridLayout):
	
	pass
		

class ProductImage(AsyncImage):

	def on_touch_down(self, touch):
		if self.collide_point(*touch.pos):
			print (self.id, self.source, self.title, self.price)
			ProductListing.open_popup(self.title, self.source, self.id, self.price)

class ConfirmButton(MDRaisedButton):
	global total_in_cart
	def on_touch_down(self, touch):
		if self.collide_point(*touch.pos):
			if total_in_cart <= 500:
				MainScreen.show_snackbar(self, "The minimal total price of your order is 500p")
			else:
				screen_manager.current = 'checkout_screen'

class ProductListing(GridLayout):
	global product_list
	global cart_list
	the_popup = None

	def search_index_by_id(self, id):
		global product_list
		index = 0
		#print('Input ID = ' + str(id))
		for product in product_list:
			if product['id'] == id:
				#print('Output Index = ' + str(index))
				return index
			else:
				index += 1
		
		


	def show_products(self):

		for product in product_list:
			one_product = BoxLayout(
				orientation='vertical', 
				size_hint_y= 1)

			image_section = BoxLayout(
				orientation='vertical',
				size_hint_y=.65)
			image = ProductImage (
				id = str(product['id']),
				source=product['img'],)
			image.price = product['price']
			
				# on_touch_down=lambda x,y: print(x,y))
			image.title = product['title']

			image_section.add_widget(image)

			label_section = BoxLayout (
				orientation='vertical', 
				size_hint_y=.10)
			label_section.add_widget(MDLabel(
				font_style='Caption',
				font_size='20dp',
				theme_text_color='Primary', 
				text=product['title'].upper(),
				halign='center'))

			button_section = BoxLayout (
				orientation='vertical', 
				size_hint_y=.20)
			button_cart = MDRaisedButton(
				id = str(product['id']),
				text='ADD TO CART',
				pos_hint={'center_x': .5},
				elevation = 9,
				#on_release = lambda x:self.open_popup(product_list[self.search_index_by_id(int(x.id))]['title'], product_list[int(x.id)]['img'], product_list[int(x.id)]['id'])
				#on_press = lambda x: print(product_list[int(x.id)]['title'], product_list[int(x.id)]['img'])
				#on_release = lambda x: self.search_index_by_id(int(x.id))
				#on_release = lambda x: print(product_list[self.search_index_by_id(int(x.id))]['title'], product_list[self.search_index_by_id(int(x.id))]['img'], product_list[self.search_index_by_id(int(x.id))]['id'])
				# on_release = lambda x: ProductListing.open_popup(product_list[self.search_index_by_id(int(x.id))]['title'],
				# 	product_list[self.search_index_by_id(int(x.id))]['img'],
				# 	product_list[self.search_index_by_id(int(x.id))]['id'],
				# 	product_list[self.search_index_by_id(int(x.id))]['price'])
				on_release = lambda x: ProductListing.add_to_cart(product_list[self.search_index_by_id(int(x.id))]['id'],
														product_list[self.search_index_by_id(int(x.id))]['img'],
														product_list[self.search_index_by_id(int(x.id))]['title'],
														product_list[self.search_index_by_id(int(x.id))]['price'])
				)
			button_section.add_widget(button_cart)

			one_product.add_widget(image_section)
			one_product.add_widget(label_section)
			one_product.add_widget(button_section)

			self.add_widget(one_product)
	
	@staticmethod
	def open_popup(product_title, image_source, id, price):
		ProductListing.the_popup = Popup(
			id = 'product_popup',
			size_hint=(1, .8),
			auto_dismiss=True,
			background='',
			background_color=(.5, .5, .5, .8),
			title_color=(0, 0, 0, 1),
			title=product_title)

		popup_box = BoxLayout(
			orientation = 'vertical',
			size_hint_y = 1)
		popup_box.add_widget(AsyncImage(source=image_source))
		popup_box.add_widget(MDLabel(
			size_hint_y = .15,
			text = product_title,
			halign = 'center',
			font_style = 'H5',
			font_size = '20dp'
			))
		popup_box.add_widget(MDLabel(
			size_hint_y = .25,
			text = str(price) + 'p',
			halign = 'center',
			font_style = 'H6',
			font_size = '30dp',
			color = [1, 0, 0, 1]
			))

		button_section = BoxLayout(
			size_hint_y = .15,
			orientation = 'horizontal',
			padding = '10dp',
			spacing = '10dp',
			# size_hint = (None, None),
			# size = self.minimum_size,
			pos_hint = {'center_x': .5},
			)
		button1_section = AnchorLayout (
			# size = self.parent.size,
			anchor_x ='center',
			anchor_y = 'center')

		button2_section = AnchorLayout (
			# size = self.parent.size,
			anchor_x ='center',
			anchor_y = 'center')

		button1_section.add_widget(MDRectangleFlatButton(
			text = 'Close',
			pos_hint = {'center_x': .5},
			# size = self.minimum_size,
			size_hint_x = .5,
			on_release=lambda a:ProductListing.the_popup.dismiss(),
			))
		button2_section.add_widget(MDRaisedButton(
			text = 'Add to cart',
			# icon = 'cart',
			pos_hint = {'center_x': .5},
			size_hint_x = .5,
			elevation = 9,
			on_release=lambda x:ProductListing.add_to_cart(id, image_source, product_title, price)
			))

		


		button_section.add_widget(button1_section)
		button_section.add_widget(button2_section)
		popup_box.add_widget(button_section)
		ProductListing.the_popup.add_widget(popup_box)
		ProductListing.the_popup.open()

	def add_to_cart(id, image_source, product_title, price):
		cart_list.append({'id': id, 'img': image_source, 'title': product_title, 'price': price})
		ProductListing.toast_message(product_title + ' was addet to your cart')
		MainScreen.item_incart_count()
		if str(type(ProductListing.the_popup)) != "<class 'NoneType'>":
		 	ProductListing.the_popup.dismiss()
		#MainScreen.update_confirm_button()

	def toast_message(text):
		toast(text)

	

class StartScreen(Screen):
	pass

class CheckOutScreen(Screen):
	pass

class LoginFormPage(Screen):
	pass

class RegistrationFormPage(Screen):
	pass



class MainScreen(Screen):
	id = 'mainnn'
	global cart_list
	global product_list

	toolbar = ObjectProperty()
	product_popup_title = ObjectProperty()
	toolbar_menu = ObjectProperty()
	toolbar_menu = MDListBottomSheet()

	def show_snackbar(self, text):
		Snackbar(text= text).show()


	def change_toolbar_title(self, toolbar_name):
		self.toolbar.title = toolbar_name

	def toolbar_callback_menu(self):
	 	self.toolbar_menu.open()

	def toast_message(text):
		toast(text)

	toolbar_menu.add_item(
			"Call to us",
			lambda x: MainScreen.toast_message('Start calling ...'),
			icon='phone-outgoing')

	toolbar_menu.add_item(
 			"Request a call",
 			# lambda x: MainScreen.toast_message('You sent a request for a call back'),
 			# icon='phone-incoming')
 			lambda x: Fixrolls2App.callback_request_email('Da1man', '+7 (999) 888-44-22'),
 			icon='phone-incoming')

	def show_cart(self):
		global cart_list
		self.ids.cart_listing.clear_widgets()
		#print('Cart:')
		for product in cart_list:
			#print(product)
			cart_product = BoxLayout(
				orientation = 'vertical')

			cart_item = BoxLayout(
				orientation = 'horizontal')

			cart_image = AsyncImage(
				source = product['img'],
				size_hint_x = .3)

			cart_name = MDLabel(
				text = product['title'],
				size_hint_x = .3)

			cart_price = MDLabel(
				text = str(product['price']) + 'p',
				size_hint_x = .1)

			cart_cancel_button = MDTextButton(
				id = str(product['id']),
				text = 'X',
				size_hint_x = .1,
				pos_hint = {'center_x': 1, 'center_y': .5},
				font_size = '25dp',
				on_release = lambda x: self.remove_from_cart(int(x.id))
				)

			cart_empty_space = Widget(
				size_hint_x = .025)

			cart_item.add_widget(cart_image)
			cart_item.add_widget(cart_name)
			cart_item.add_widget(cart_price)
			cart_item.add_widget(cart_cancel_button)
			cart_item.add_widget(cart_empty_space)
			cart_product.add_widget(cart_item)
			self.ids.cart_listing.add_widget(cart_product)

	def remove_from_cart(self, id):
		#print('Product ID=' + str(id))
		#print('Index in cart=' + str(self.search_index_by_id_in_cart(id)) + ' removed from cart')
		cart_list.pop(self.search_index_by_id_in_cart(id))
		self.show_cart()
		removed_item=product_list[self.search_index_by_id(id)]['title']
		MainScreen.toast_message(removed_item + 'was removed from cart')
		self.update_total()
		MainScreen.item_incart_count()
		self.update_confirm_button()

	def update_confirm_button(self):
		if self.update_total() >= 500:
			self.ids.confirm_button.disabled = False
			print ('Confirm button is enabled')
		elif self.update_total() < 500:
			self.ids.confirm_button.disabled = True
			print ('Confirm button is disabled')



	def update_total(self):
		global total_in_cart
		total_label = ObjectProperty()
		total = 0
		for product in cart_list:
			total += product['price']
		self.total_label.text = 'Total: ' + str(total)
		#print('Total=' + str(total))
		total_in_cart = total
		return total

	def search_index_by_id_in_cart(self, id):
		index = 0
		for product in cart_list:
			if product['id'] == id:
				return index
			else:
				index += 1

	def search_index_by_id(self, id):
		global product_list
		index = 0
		#print('Input ID = ' + str(id))
		for product in product_list:
			if product['id'] == id:
				#print('Output Index = ' + str(index))
				return index
			else:
				index += 1

	def item_incart_count():
		count = len(cart_list)
		print ('item in cart = ' + str(count))
		return count

class Container (BoxLayout):
	toolbar = ObjectProperty()
	product_popup_title = ObjectProperty()
	toolbar_menu = ObjectProperty()


	def change_toolbar_title(self, toolbar_name):

		self.toolbar.title = toolbar_name

	def toast_message(self, text):
		toast(text)


	



class Fixrolls2App(App):
	global screen_manager
	current_user_id = None

	theme_cls = ThemeManager()
	theme_cls.primary_palette = 'Teal'
	title = "Fixrolls"

	#------EMAIL SETTINGS------
	addr_from = "dl@rocketstation.ru"
	addr_to = "dl@rocketstation.ru"
	host = 'smtp.yandex.ru'
	port = 465
	login = "dl@rocketstation.ru"
	password = "WSFklvhwlgkwq"
	#------------

	def login_user(self, email, password):
		# print('input data: ', + login + ', ' + password)
		print('connecting to database')
		connect = sqlite3.connect('fixrolls.db')
		cursor = connect.cursor()
		print('connected')
		sql = "SELECT * FROM users WHERE email=?"
		founded_user = cursor.execute(sql, [email]).fetchone()
		if founded_user == None:
			MainScreen.toast_message('ERROR! User ' + email + ' not registred')
		else:
			if (email == founded_user[1]) and (password == founded_user[2]):
				MainScreen.toast_message('SUCCES! User ' + email + ' log in')
				screen_manager.current = 'main_screen'
				Fixrolls2App.current_user_id = founded_user[0]
				print('Now user id is: ' + str(Fixrolls2App.current_user_id))
			else:
				MainScreen.toast_message('ERROR! Wrong password')



	def reg_user(self, email, password, name, phone):
		if email=='' or password=='' or name=='' or phone=='':
			MainScreen.toast_message('ERROR! Please, input all fields')
		else:
			print('connecting to database')
			connect = sqlite3.connect('fixrolls.db')
			cursor = connect.cursor()
			print('connected')
			user = (email, password, name, phone)
			sql = "SELECT * FROM users WHERE email=?"
			founded_user = cursor.execute(sql, [email]).fetchone()
			if founded_user != None:
				MainScreen.toast_message('ERROR! Username is already taken')
			else:
				sql = """ INSERT INTO users (email, password, name, phone)
				VALUES (?, ?, ?, ?)
				"""
				cursor.execute(sql, user)
				connect.commit()
				print('User created')
				MainScreen.toast_message('SUCCESS! User '  + email + ' was created')
				sql = "SELECT * FROM users WHERE email=?"
				founded_user = cursor.execute(sql, [email]).fetchone()
				Fixrolls2App.current_user_id = founded_user[0]
				print('Now user id is: ' + str(Fixrolls2App.current_user_id))
				screen_manager.current = 'main_screen'

		# sql = """

		# """
		# cursor.execute(sql)
		# print('saving data...')
		# connect.commit()


	def callback_request_email(user, tel):
		subject = 'Callback Request'
		body = 'User ' + user + ' ordered a call back him to ' + tel
		body += '\n\n------------\n'
		body += 'this mail from FixRolls Application'
		Fixrolls2App.send_email(subject, body)
		


	def send_email(subject, email_text):

		msg = MIMEMultipart()
		msg['From']    = Fixrolls2App.addr_from
		msg['To']      = Fixrolls2App.addr_to
		msg['Subject'] = subject

		body = email_text
		msg.attach(MIMEText(body, 'plain'))

		try:
			print('connecting to server')
			smtpObj = smtplib.SMTP_SSL(Fixrolls2App.host, Fixrolls2App.port)
			print('connected')
		except Exception:
			MainScreen.toast_message(subject + ' - connecting to server ERROR')
		else:
			try:
				print('login to server')
				smtpObj.login(Fixrolls2App.login,Fixrolls2App.password)
				print('loged in - OK')
				print('sending email')
				smtpObj.sendmail(Fixrolls2App.addr_from,Fixrolls2App.addr_to,msg.as_string())
				print('email sended - OK')
				MainScreen.toast_message(subject + ' - sending OK')
				
			except Exception:
				MainScreen.toast_message(subject + ' - sending ERROR')
			finally:
				smtpObj.quit()
				

	def toast_message(self, text):
		toast(text)

	def build(self):
		global screen_manager
		screen_manager = ScreenManager(id='screenmanager', transition=WipeTransition())
		screen_manager.add_widget(StartScreen(name="start_screen"))
		screen_manager.add_widget(MainScreen(name="main_screen"))
		screen_manager.add_widget(CheckOutScreen(name="checkout_screen"))
		screen_manager.add_widget(LoginFormPage(name="login_screen"))
		screen_manager.add_widget(RegistrationFormPage(name="registration_screen"))

		return screen_manager


if __name__ == '__main__':
	Fixrolls2App().run()