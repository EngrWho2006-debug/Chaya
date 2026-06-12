from interpreter import run

with open("program.chaya", "r") as file:
    code = file.read()

run(code)