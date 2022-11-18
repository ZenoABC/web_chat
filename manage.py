import click
import json

with open("storage.json", "r") as f:
	data = json.load(f)

def save():
	with open("storage.json", "w") as f:
		json.dump(data, f, indent = 4)

@click.group(invoke_without_command = True)
def main():
	pass

@main.command()
@click.option("--ip", prompt = "Enter user's ip address")
@click.option("--name", prompt = "Enter user's name")
@click.option("--color", default = "#555555")
def add_user(ip: str, name: str, color: str):
	user = {"name": name, "last_color": color}
	data["users"][ip] = user
	save()
	print("Added.")

main()