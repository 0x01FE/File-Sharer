from zipfile import ZipFile
import socket, os, configparser


BUFFER_SIZE = 4096
config = configparser.ConfigParser()
config.read('config.ini')
host = config['SETTINGS']['HOST']
port = int(config['SETTINGS']['PORT'])

def get_all_file_paths(directory):
	file_paths = []

	for root, directories, files in os.walk(directory):
		for filename in files:
			filepath = os.path.join(root, filename)
			file_paths.append(filepath)

	return file_paths        


while True:
	print('> ',end='')
	user_input = input().lower()
	if user_input == "exit":
		exit()
	elif user_input == "help":
		print("""
		EXIT  :  exit the program
		HELP  :  bring up this menu
		SHARE {-z} {PATH and FILE NAME}  : share filename with set host
			-z : zip the file
		SET {OPTION} {INPUT}  : options are PORT and HOST
		SERVER  :  set client to server mode (must use ctrl + c to end)
		PRINT {OPTION}  :  options are PORT and HOST
		""")
	elif "share" in user_input:
		args = user_input.split()
		if not len(args) > 1:
			print("Error: no file path")
		else:
			file_path = args[1]
			if os.path.exists(file_path):
				if "-z" in user_input:
					if os.path.isdir(file_path):
						with ZipFile('message.zip','w') as z:
							for item in get_all_file_paths(file_path):
								z.write(item)
					else:
						with ZipFile('message.zip','w') as z:
							z.write(file_path)
					file_path = 'message.zip'
				s = socket.socket()
				try:
					s.connect((host,port))
				except ConnectionRefusedError:
					print("Target IP / PORT were not listening")
					continue
				s.send(f'{file_path}'.encode())
				with open(file_path, "rb") as f:
					while True:
						bytes_read = f.read(BUFFER_SIZE)
						if not bytes_read:
							break
						s.sendall(bytes_read)
				s.close()
			else:
				print(f'{args[1]} does not exist or is not a valid file path.')
	elif "set" in user_input:
		trigger = False
		args = user_input.split()
		if len(args) == 1:
			print('Not enough arguments, check HELP')
		else:
			if args[1] == "host" and args[2]:
				trigger = True
				host = args[2]
				config_write = configparser.ConfigParser()
				config_write['SETTINGS'] = {'HOST' : args[2], "PORT" : port}
				with open('config.ini', 'w') as config_file:
					config_write.write(config_file)
			elif args[1] == "port" and args[2]:
				if args[2].isnumeric():
					port = int(args[2])
					trigger = True
					config_write = configparser.ConfigParser()
					config_write['SETTINGS'] = {'HOST' : host, "PORT" : args[2]}
					with open('config.ini', 'w') as config_file:
						config_write.write(config_file)
				else:
					print("That is not a valid port number.")
			else:
				print("Syntax Error, refer to HELP.")
			if trigger:
				print(f'{args[1].title()} was set to {args[2]}.')
	elif user_input == 'server':
		s = socket.socket()
		s.bind((host, port))
		print("Entering server mode.")
		while True:
			print(f"[*] Listening on {host}:{port}.")
			s.listen()
			conn, addr = s.accept()
			print(f"{addr} is connected.")
			received = conn.recv(BUFFER_SIZE).decode('latin-1')
			filename = received
			filename = os.path.basename(filename)
			with open(filename, "wb") as f:
				while True:
					bytes_read = conn.recv(BUFFER_SIZE)
					if not bytes_read:
						break
					f.write(bytes_read)
			conn.close()
			print(f"File \"{filename}\" recieved from {addr}.")
	elif "print" in user_input:
		args = user_input.split()
		if len(args) == 1:
			print('Not enough arguments, check HELP')
		else:
			if args[1] == 'host':
				print(host)
			elif args[1] == 'port':
				print(port)
			else:
				print("That is not a valid option, please refer to HELP.")
	else:
		print(f"{user_input} is not a command. Maybe reference the HELP command?")
		
		
