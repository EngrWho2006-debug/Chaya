from pydoc import text


def run(code):
    variables = {}
    shadow_variables = {}
    shadow_count = 0
    functions = {}
    imports = {}

    current_scope = "main"
    last_scope = "main"


    lines = code.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        if line == "":
            i += 1
            continue

        # Comments
        if line.startswith("#"):
            i += 1
            continue


        # -------------------
        # import
        # -------------------

        if line.startswith("import"):

            statement = line.replace("import", "").strip()

            alias = None

            if " as " in statement:

                filename, alias = statement.split(" as ")

                filename = filename.strip()
                alias = alias.strip()

            else:

                filename = statement.strip()

            try:

                with open(filename, "r") as file:

                    imported_code = file.read()

                if alias:
                    imports[alias] = filename

                for imported_line in imported_code.split("\n"):
                    lines.insert(i + 1, imported_line)

            except FileNotFoundError:

                print("Chaya Import Error:")
                print("File not found:", filename)



        # -------------------
        # keep
        # -------------------
        if line.startswith("keep"):
            parts = line.split(" as ")

            if len(parts) != 2:
                print("Chaya Error: Invalid keep syntax")
                i += 1
                continue

            var_name = parts[0].replace("keep", "").strip()
            value = parts[1].strip()

            if value.startswith("[") and value.endswith("]"):
                items = value[1:-1].split(",")

                value = []

                for item in items:
                    value.append(item.strip())

            elif value.isdigit():
                value = int(value)

            else:
                value = str(value)

            variables[var_name] = value


        # -------------------
        # shadow
        # -------------------

        elif line.startswith("shadow"):

            parts = line.split(" as ")

            if len(parts) != 2:
                print("Chaya Reflection Error:")
                print("Invalid shadow syntax")

                i += 1
                continue

            var_name = parts[0].replace("shadow", "").strip()

            value = parts[1].strip()

            if value.isdigit():
                value = int(value)

            shadow_variables[var_name] = value

            shadow_count += 1
      

        # -------------------
        # ask
        # -------------------
        elif line.startswith("ask"):
            var_name = line[4:].strip()

            user_input = input("> ")

            if user_input.isdigit():
                user_input = int(user_input)

            variables[var_name] = user_input

        # -------------------
        # if else done
        # -------------------
        elif line.startswith("if"):
            condition = line[3:].strip()

            result = False

            if ">=" in condition:
                left, right = condition.split(">=")
                result = variables[left.strip()] >= int(right.strip())

            elif "<=" in condition:
                left, right = condition.split("<=")
                result = variables[left.strip()] <= int(right.strip())

            elif "==" in condition:
                left, right = condition.split("==")
                result = variables[left.strip()] == int(right.strip())

            elif "!=" in condition:
                left, right = condition.split("!=")
                result = variables[left.strip()] != int(right.strip())

            elif ">" in condition:
                left, right = condition.split(">")
                result = variables[left.strip()] > int(right.strip())

            elif "<" in condition:
                left, right = condition.split("<")
                result = variables[left.strip()] < int(right.strip())

            if result:
                i += 1

                while i < len(lines):
                    current = lines[i].strip()

                    if current == "else":
                        while i < len(lines):
                            if lines[i].strip() == "done":
                                break
                            i += 1
                        break

                    elif current == "done":
                        break

                    elif current.startswith("say"):
                        text = current[4:].strip()

                        if text in variables:
                            print(variables[text])
                        else:
                            print(text)

                    i += 1

            else:
                while i < len(lines):
                    current = lines[i].strip()

                    if current == "else":
                        i += 1

                        while i < len(lines):
                            current = lines[i].strip()

                            if current == "done":
                                break

                            elif current.startswith("say"):
                                text = current[4:].strip()

                                if text in variables:
                                    print(variables[text])
                                else:
                                    print(text)

                            i += 1

                        break

                    elif current == "done":
                        break

                    i += 1


        # -------------------
        # repeat
        # -------------------
        elif line.startswith("repeat"):
            count = int(line.replace("repeat", "").strip())

            loop_lines = []

            i += 1

            while i < len(lines) and lines[i].strip() != "done":
                loop_lines.append(lines[i].strip())
                i += 1

            for _ in range(count):
                for loop_line in loop_lines:
                    if loop_line.startswith("say"):
                        text = loop_line[4:].strip()

                        if text in variables:
                            print(variables[text])
                        else:
                            print(text)

        # -------------------
        # brew
        # -------------------
        elif line.startswith("brew"):
            func_name = line.replace("brew", "").strip()
            last_scope = current_scope
            current_scope = func_name

            function_lines = []

            i += 1

            while i < len(lines):
                current = lines[i].strip()

                if current == "done":
                    break

                function_lines.append(current)
                i += 1

            functions[func_name] = function_lines

            last_scope = func_name
            current_scope = "main"


        # -------------------
        # serve
        # ------------------- 

        elif line.startswith("serve"):
            func_name = line.replace("serve", "").strip()

            if func_name in functions:

                for func_line in functions[func_name]:

                    if func_line.startswith("say"):
                        text = func_line[4:].strip()

                        if "+" in text:
                            left, right = text.split("+", 1)

                            left = left.strip()
                            right = right.strip()

                            if left.startswith('"') and left.endswith('"'):
                                left = left[1:-1]
                            elif left in variables:
                                left = variables[left]

                            if right.startswith('"') and right.endswith('"'):
                                right = right[1:-1]
                            elif right in variables:
                                right = variables[right]

                            print(str(left) + str(right))

                        elif text.startswith('"') and text.endswith('"'):
                            print(text[1:-1])

                        elif text in variables:
                            print(variables[text])

                        else:
                            print(text)


        # -------------------
        # add
        # -------------------
        
        elif line.startswith("add"):

            parts = line.split(" to ")

            item = parts[0].replace("add", "").strip()
            list_name = parts[1].strip()

            if list_name in variables:
                variables[list_name].append(item) 

        # -------------------
        # remove
        # -------------------

        elif line.startswith("remove"):

            parts = line.split(" from ")

            item = parts[0].replace("remove", "").strip()
            list_name = parts[1].strip()

            if list_name in variables:
                if item in variables[list_name]:
                    variables[list_name].remove(item)


        # -------------------
        # size
        # -------------------

        elif line.startswith("size"):
            list_name = line.replace("size", "").strip()

            if list_name in variables:
                print(len(variables[list_name]))


        # -------------------
        # reflect
        # -------------------

        elif line.startswith("reflect"):

            var_name = line.replace("reflect", "").strip()

            if var_name in variables:

                value = variables[var_name]

                print("Reflection")
                print("name =", var_name)
                print("value =", value)
                print("type =", type(value).__name__)

            else:
                print("Chaya Reflection Error:")
                print("Variable not found")  


        # -------------------
        # echo
        # -------------------

        elif line == "echo":

            print("Chaya Echo")
            print("last_scope =", last_scope)        


        # -------------------
        # presence
        # -------------------

        elif line == "presence":

            print("Chaya Presence")
            print("scope =", current_scope)
            print("variables =", len(variables))
            print("shadow =", shadow_count)
            print("functions =", len(functions))      


        # -------------------
        # help
        # -------------------

        elif line.startswith("help"):

            command = line.replace("help", "").strip()

            help_text = {
                "keep": "store values",
                "say": "print values",
                "ask": "take input",
                "reflect": "inspect variable details",
                "presence": "show current state",
                "echo": "show previous scope",
                "brew": "create function",
                "serve": "run function",
                "import": "load another .chaya file"
            }

            if command in help_text:
                print(help_text[command])

            else:
                print("Chaya Help Error:")
                print("Command not found")






        # -------------------
        # say
        # -------------------
        elif line.startswith("say"):
            text = line[4:].strip()

            try:

                # Power
                if "**" in text:
                    left, right = text.split("**")

                    left = variables.get(left.strip(), left.strip())
                    right = variables.get(right.strip(), right.strip())

                    print(int(left) ** int(right))

                # Modulus
                elif "%" in text:
                    left, right = text.split("%")

                    left = variables.get(left.strip(), left.strip())
                    right = variables.get(right.strip(), right.strip())

                    print(int(left) % int(right))

                # Addition
                elif "+" in text:
                    left, right = text.split("+", 1)

                    left = left.strip()
                    right = right.strip()

                    # Remove quotes if present
                    if left.startswith('"') and left.endswith('"'):
                        left = left[1:-1]
                    elif left in variables:
                        left = variables[left]

                    if right.startswith('"') and right.endswith('"'):
                        right = right[1:-1]
                    elif right in variables:
                        right = variables[right]

                    # String concatenation if either side is text
                    if isinstance(left, str) or isinstance(right, str):
                        print(str(left) + str(right))
                    else:
                        print(int(left) + int(right))


                # Subtraction
                elif "-" in text:
                    left, right = text.split("-")

                    left = variables.get(left.strip(), left.strip())
                    right = variables.get(right.strip(), right.strip())

                    print(int(left) - int(right))

                # Multiplication
                elif "*" in text:
                    left, right = text.split("*")

                    left = variables.get(left.strip(), left.strip())
                    right = variables.get(right.strip(), right.strip())

                    print(int(left) * int(right))

                # Division
                elif "/" in text:
                    left, right = text.split("/")

                    left = variables.get(left.strip(), left.strip())
                    right = variables.get(right.strip(), right.strip())

                    if int(right) == 0:
                        print("Chaya Error")
                        print("line =", i + 1)
                        print("message = Division by zero")
                    else:
                        print(int(left) / int(right))

                # String Literal
                elif text.startswith('"') and text.endswith('"'):
                    print(text[1:-1])

                # List Indexing
                elif "[" in text and "]" in text:

                    list_name = text.split("[")[0].strip()

                    index = int(
                        text.split("[")[1]
                        .replace("]", "")
                    )

                    if list_name in variables:
                        print(variables[list_name][index])


                # Variable
                elif text in shadow_variables:
                    print(shadow_variables[text])

                elif text in variables:
                    print(variables[text])


                # Plain Text
                else:
                    print(text)
            

            except Exception as e:
                print("Chaya Error")
                print("line =", i + 1)
                print("message =", e)

        i += 1