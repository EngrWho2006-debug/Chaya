import re

def evaluate_expression(expression, variables):

    # Replace variable names with their values
    for name, value in variables.items():

        expression = re.sub(
            r"\b" + re.escape(name) + r"\b",
            str(value),
            expression
        )

    return eval(expression)

def execute_command(line, variables, shadow_variables,
                    functions, imports):

    line = line.strip()

    if line == "":
        return

    # -------------------
    # say
    # -------------------

    if line.startswith("say"):

        text = line[4:].strip()

        try:

            # -------------------
            # Power
            # -------------------

            if "**" in text:

                left, right = text.split("**", 1)

                left = variables.get(left.strip(), left.strip())
                right = variables.get(right.strip(), right.strip())

                print(int(left) ** int(right))


            # -------------------
            # Modulus
            # -------------------

            elif "%" in text:

                left, right = text.split("%", 1)

                left = variables.get(left.strip(), left.strip())
                right = variables.get(right.strip(), right.strip())

                print(int(left) % int(right))


            # -------------------
            # Expression
            # -------------------

            elif any(op in text for op in [
                "+",
                "-",
                "*",
                "/",
                "%",
                "**",
                "(",
                ")"
            ]):

                print(
                    evaluate_expression(
                        text,
                        variables
                    )
                )

            # -------------------
            # String
            # -------------------

            elif text.startswith('"') and text.endswith('"'):

                print(text[1:-1])


            # -------------------
            # Subtraction
            # -------------------

            elif "-" in text:

                left, right = text.split("-", 1)

                left = variables.get(left.strip(), left.strip())
                right = variables.get(right.strip(), right.strip())

                print(int(left) - int(right))


            # -------------------
            # Multiplication
            # -------------------

            elif "*" in text:

                parts = text.split("*")

                result = 1

                for value in parts:

                    value = value.strip()

                    if value in variables:
                        value = variables[value]

                    result *= int(value)

                print(result)


            # -------------------
            # Division
            # -------------------

            elif "/" in text:

                left, right = text.split("/", 1)

                left = variables.get(left.strip(), left.strip())
                right = variables.get(right.strip(), right.strip())

                if int(right) == 0:

                    print("Chaya Error")
                    print("message = Division by zero")
                else:
                    print(int(left) / int(right))


            # -------------------
            # List Indexing
            # -------------------

            elif "[" in text and "]" in text:

                list_name = text.split("[")[0].strip()

                index = int(
                    text.split("[")[1]
                    .replace("]", "")
                )

                if list_name in variables:

                    print(variables[list_name][index])

                else:

                    print("Chaya Error")
                    print("List not found")


            # -------------------
            # Shadow variable
            # -------------------

            elif text in shadow_variables:

                print(shadow_variables[text])


            # -------------------
            # Variable
            # -------------------

            elif text in variables:

                print(variables[text])


            # -------------------
            # Plain text
            # -------------------

            else:

                print(text)


        except Exception as e:

            print("Chaya Error")
            print("Message:", e)


    # -------------------
    # keep
    # -------------------

    elif line.startswith("keep"):

        parts = line.split(" as ", 1)

        if len(parts) != 2:
            print("Chaya Error: Invalid keep syntax")
            return

        name = parts[0].replace("keep", "", 1).strip()
        value = parts[1].strip()

        if value.lower() == "true":
            value = True

        elif value.lower() == "false":
            value = False

        elif value.isdigit():
            value = int(value)

        elif value in variables:
            value = variables[value]

        else:
            value = value.strip('"')

        variables[name] = value

    # -------------------
    # delete
    # -------------------

    elif line.startswith("delete"):

        name = line.replace("delete", "", 1).strip()

        if name in variables:
            del variables[name]
            print("Deleted:", name)

        else:
            print("Chaya Delete Error:")
            print("Variable not found")

    # -------------------
    # exists
    # -------------------

    elif line.startswith("exists"):

        name = line.replace("exists", "", 1).strip()

        print(name in variables)

    # -------------------
    # type
    # -------------------

    elif line.startswith("type"):

        name = line.replace("type", "", 1).strip()

        if name in variables:
            print(type(variables[name]).__name__)

        elif name in shadow_variables:
            print(type(shadow_variables[name]).__name__)

        else:
            print("Chaya Type Error:")
            print("Variable not found")