def run(code):
    variables = {}

    lines = code.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        if line == "":
            i += 1
            continue

        # -------------------
        # keep
        # -------------------
        if line.startswith("keep"):
            parts = line.split(" as ")

            if len(parts) != 2:
                print("TeaLang Error: Invalid keep syntax")
                i += 1
                continue

            var_name = parts[0].replace("keep", "").strip()
            value = parts[1].strip()

            if value.isdigit():
                value = int(value)

            variables[var_name] = value

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
        # say
        # -------------------
        elif line.startswith("say"):
            text = line[4:].strip()

            try:

                if "**" in text:
                    left, right = text.split("**")

                    left = variables.get(left.strip(), left.strip())
                    right = variables.get(right.strip(), right.strip())

                    print(int(left) ** int(right))

                elif "%" in text:
                    left, right = text.split("%")

                    left = variables.get(left.strip(), left.strip())
                    right = variables.get(right.strip(), right.strip())

                    print(int(left) % int(right))

                elif "+" in text:
                    left, right = text.split("+")

                    left = variables.get(left.strip(), left.strip())
                    right = variables.get(right.strip(), right.strip())

                    print(int(left) + int(right))

                elif "-" in text:
                    left, right = text.split("-")

                    left = variables.get(left.strip(), left.strip())
                    right = variables.get(right.strip(), right.strip())

                    print(int(left) - int(right))

                elif "*" in text:
                    left, right = text.split("*")

                    left = variables.get(left.strip(), left.strip())
                    right = variables.get(right.strip(), right.strip())

                    print(int(left) * int(right))

                elif "/" in text:
                    left, right = text.split("/")

                    left = variables.get(left.strip(), left.strip())
                    right = variables.get(right.strip(), right.strip())

                    if int(right) == 0:
                        print("TeaLang Error: Division by zero")
                    else:
                        print(int(left) / int(right))

                elif text in variables:
                    print(variables[text])

                else:
                    print(text)

            except Exception as e:
                print("TeaLang Error:", e)

        i += 1