import socket, os

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096
host = '127.0.0.1'
port = 6969


while True:
	print('> ',end='')
	user_input = input()
	if user_input.lower() == "exit":
		exit()
	elif user_input.lower() == "help":
		print("""
		EXIT  :  exit the program
		HELP  :  bring up this menu
		SHARE {PATH and FILE NAME}  : share filename with set host
		SET {OPTION} {INPUT}  : options are PORT and HOST
		SERVER  :  set client to server mode (must use ctrl + c to end)
		""")
	elif "share" in user_input.lower():
		args = user_input.split()
		if os.path.exists(args[1]):
			s = socket.socket()
			try:
				s.connect((host,port))
			except ConnectionRefusedError:
				print("Target IP / PORT were not listening")
				continue
			filesize = os.path.getsize(args[1])
			s.send(f'{args[1]}{SEPARATOR}{filesize}'.encode())
			with open(args[1], "rb") as f:
				while True:
					bytes_read = f.read(BUFFER_SIZE)
					if not bytes_read:
						break
					s.sendall(bytes_read)
			s.close()
		else:
			print(f'{args[1]} does not exist.')
	elif "set" in user_input.lower():
		trigger = False
		args = user_input.split()
		if args[1].lower() == "host" and args[2]:
			trigger = True
			host = args[2]
		elif args[1].lower() == "port" and args[2]:
			if args[2].isnumeric():
				port = int(args[2])
				trigger = True
			else:
				print("That is not a valid port number.")
		else:
			print("Syntax Error, refer to HELP.")
		if trigger:
			print(f'{args[1].title()} was set to {args[2]}.')
	elif user_input.lower() == 'server':
		s = socket.socket()
		while True:
			s.bind((host, port))
			print(f"Entering server mode.\nListening on {host}:{port}.")
			s.listen()
			conn, addr = s.accept()
			print(f"{addr} is connected.")
			received = conn.recv(BUFFER_SIZE).decode('latin-1')
			filename, filesize = received.split(SEPARATOR)
			filename = os.path.basename(filename)
			with open(filename, "wb") as f:
				while True:
					bytes_read = conn.recv(BUFFER_SIZE)
					if not bytes_read:
						break
					f.write(bytes_read)
			conn.close()
			s.close()
	else:
		print(f"{user_input} is not a command. Maybe reference the HELP command?")
