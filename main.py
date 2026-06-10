from interpreter import run

with open("program.tea", "r") as file:
    code = file.read()

run(code)