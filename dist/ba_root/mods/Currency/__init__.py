from .Commands import chat_commands
from .Handlers.ba_get_player_data import client_to_account



def main(msg, client_id):
	command = msg.split(" ")[0]
	
	if command.startswith("."):
		command = command.split(".")[1]
		arguments = msg.split(" ")[1:]
		accountid = client_to_account(client_id)
		
		chat_commands.on_command(command, arguments, accountid, client_id)