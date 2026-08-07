import os
from executor import execute_command


def runtime_error(line_no, message):
    print("Chaya Runtime Error")
    print("Line:", line_no)
    print("Message:", message)


def _value(value, variables):
    """Convert a Chaya condition value into a Python value."""
    value = value.strip()

    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False

    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]

    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]

    if value in variables:
        return variables[value]

    try:
        return int(value)
    except ValueError:
        pass

    try:
        return float(value)
    except ValueError:
        return value


def evaluate_condition(condition, variables):
    """Evaluate one or more Chaya conditions."""
    condition = condition.strip()

    # OR has lower priority than AND.
    if " or " in condition:
        return any(
            evaluate_condition(part, variables)
            for part in condition.split(" or ")
        )

    if " and " in condition:
        return all(
            evaluate_condition(part, variables)
            for part in condition.split(" and ")
        )

    if condition.startswith("not "):
        return not bool(
            _value(condition[4:].strip(), variables)
        )

    operators = [">=", "<=", "==", "!=", ">", "<"]

    for operator in operators:
        if operator in condition:
            left, right = condition.split(operator, 1)

            left = _value(left, variables)
            right = _value(right, variables)

            try:
                if operator == ">=":
                    return left >= right
                if operator == "<=":
                    return left <= right
                if operator == "==":
                    return left == right
                if operator == "!=":
                    return left != right
                if operator == ">":
                    return left > right
                if operator == "<":
                    return left < right
            except TypeError:
                return False

    return bool(_value(condition, variables))


def find_block_end(lines, start, end_token="done"):
    """Find the matching done for a block, including nested blocks."""
    depth = 1
    index = start

    while index < len(lines):
        current = lines[index].strip()

        if current.startswith(("if ", "while ", "for ", "repeat ", "brew ")):
            depth += 1

        elif current == end_token:
            depth -= 1

            if depth == 0:
                return index

        index += 1

    return None


def find_if_parts(lines, start):
    """
    start = first line inside an IF.
    Returns (else_index, done_index).
    Nested IFs are ignored while looking for the outer ELSE.
    """
    depth = 1
    index = start
    else_index = None

    while index < len(lines):
        current = lines[index].strip()

        if current.startswith("if "):
            depth += 1

        elif current == "done":
            depth -= 1

            if depth == 0:
                return else_index, index

        elif current == "else" and depth == 1:
            else_index = index

        index += 1

    return None, None


def execute_keep(line, variables, line_no):
    parts = line.split(" as ", 1)

    if len(parts) != 2:
        runtime_error(line_no, "Invalid keep syntax")
        return

    name = parts[0].replace("keep", "", 1).strip()
    raw = parts[1].strip()

    # List
    if raw.startswith("[") and raw.endswith("]"):
        inside = raw[1:-1].strip()

        if inside == "":
            value = []
        else:
            value = [
                _value(item.strip(), variables)
                for item in inside.split(",")
            ]

    # Boolean
    elif raw.lower() == "true":
        value = True

    elif raw.lower() == "false":
        value = False

    # String
    elif (
        raw.startswith('"') and raw.endswith('"')
    ) or (
        raw.startswith("'") and raw.endswith("'")
    ):
        value = raw[1:-1]

    # Existing variable
    elif raw in variables:
        value = variables[raw]

    # Integer
    else:
        try:
            value = int(raw)

        # Float
        except ValueError:
            try:
                value = float(raw)

            # Arithmetic expression
            except ValueError:
                try:
                    expression = raw

                    for name2, value2 in sorted(
                        variables.items(),
                        key=lambda item: len(item[0]),
                        reverse=True
                    ):
                        if isinstance(value2, (int, float)):
                            expression = expression.replace(
                                name2,
                                str(value2)
                            )

                    value = eval(
                        expression,
                        {"__builtins__": {}},
                        {}
                    )

                except Exception:
                    value = raw

    variables[name] = value
    

def execute_import(line, lines, index, imports, line_no):
    statement = line[len("import "):].strip()

    if " as " in statement:
        filename, alias = statement.split(" as ", 1)
        filename = filename.strip()
        alias = alias.strip()
    else:
        filename = statement
        alias = None

    try:
        with open(filename, "r", encoding="utf-8") as file:
            imported_code = file.read()

        imports[alias or filename] = filename

        imported_lines = imported_code.splitlines()

        for imported_line in reversed(imported_lines):
            lines.insert(index + 1, imported_line)

        return True

    except FileNotFoundError:
        print("Chaya Import Error:")
        print("File not found:", filename)
        return True

    except Exception as exc:
        print("Chaya Import Error:")
        print(exc)
        return True


def execute_command_line(
    line,
    variables,
    shadow_variables,
    shadow_count,
    functions,
    imports,
    current_scope,
    last_scope,
    line_no,
):
    """
    Execute one non-block command.
    Returns updated (shadow_count, current_scope, last_scope).
    """
    if line.startswith("keep "):
        execute_keep(line, variables, line_no)
        return shadow_count, current_scope, last_scope

    if line.startswith("shadow "):
        parts = line.split(" as ", 1)

        if len(parts) != 2:
            runtime_error(line_no, "Invalid shadow syntax")
            return shadow_count, current_scope, last_scope

        name = parts[0].replace("shadow", "", 1).strip()
        value = _value(parts[1], variables)

        shadow_variables[name] = value
        shadow_count += 1

        return shadow_count, current_scope, last_scope

    if line.startswith("ask ") or line.startswith("input "):
        if line.startswith("ask "):
            name = line[4:].strip()
        else:
            name = line[6:].strip()

        user_input = input("> ")

        if user_input.lower() == "true":
            user_input = True
        elif user_input.lower() == "false":
            user_input = False
        else:
            try:
                user_input = int(user_input)
            except ValueError:
                pass

        variables[name] = user_input
        return shadow_count, current_scope, last_scope

    if line.startswith("delete "):
        name = line[7:].strip()

        if name in variables:
            del variables[name]
            print("Deleted:", name)
        else:
            runtime_error(line_no, "Variable not found")

        return shadow_count, current_scope, last_scope

    if line.startswith("exists "):
        name = line[7:].strip()
        print(name in variables)
        return shadow_count, current_scope, last_scope

    if line.startswith("type "):
        name = line[5:].strip()

        if name in variables:
            print(type(variables[name]).__name__)
        elif name in shadow_variables:
            print(type(shadow_variables[name]).__name__)
        else:
            runtime_error(line_no, "Variable not found")

        return shadow_count, current_scope, last_scope

    if line.startswith("length "):
        name = line[7:].strip()

        if name not in variables:
            runtime_error(line_no, "Variable not found")
        else:
            value = variables[name]

            if isinstance(value, (str, list)):
                print(len(value))
            else:
                print("Chaya Length Error:")
                print("Variable has no length")

        return shadow_count, current_scope, last_scope

    if line.startswith("add ") and " to " in line:
        item, list_name = line[4:].split(" to ", 1)
        list_name = list_name.strip()
        item = _value(item.strip(), variables)

        if list_name in variables and isinstance(variables[list_name], list):
            variables[list_name].append(item)

        return shadow_count, current_scope, last_scope

    if line.startswith("remove ") and " from " in line:
        item, list_name = line[7:].split(" from ", 1)
        list_name = list_name.strip()
        item = _value(item.strip(), variables)

        if list_name in variables and isinstance(variables[list_name], list):
            if item in variables[list_name]:
                variables[list_name].remove(item)

        return shadow_count, current_scope, last_scope

    if line.startswith("size "):
        name = line[5:].strip()

        if name in variables and isinstance(variables[name], list):
            print(len(variables[name]))
        else:
            runtime_error(line_no, "List not found")

        return shadow_count, current_scope, last_scope

    if line.startswith("reflect "):
        name = line[8:].strip()

        if name in variables:
            value = variables[name]
            print("Reflection")
            print("name =", name)
            print("value =", value)
            print("type =", type(value).__name__)
        else:
            runtime_error(line_no, "Variable not found")

        return shadow_count, current_scope, last_scope

    if line == "show":
        print("Variables")

        if not variables:
            print("No variables")
        else:
            for name, value in variables.items():
                print(name, "=", value)

        return shadow_count, current_scope, last_scope

    if line.startswith("write "):
        try:
            statement = line[6:].strip()

            if " to " not in statement:
                print("Chaya Write Error:")
                print("Invalid syntax")
                return shadow_count, current_scope, last_scope

            text, filename = statement.split(" to ", 1)
            text = text.strip()
            filename = filename.strip()

            text = _value(text, variables)

            with open(filename, "w", encoding="utf-8") as file:
                file.write(str(text))

            print("Written to", filename)

        except Exception as exc:
            print("Chaya Write Error:")
            print(exc)

        return shadow_count, current_scope, last_scope

    if line.startswith("read "):
        filename = line[5:].strip()

        try:
            with open(filename, "r", encoding="utf-8") as file:
                print(file.read())
        except FileNotFoundError:
            print("Chaya Read Error:")
            print("File not found")
        except Exception as exc:
            print("Chaya Read Error:")
            print(exc)

        return shadow_count, current_scope, last_scope

    if line == "echo":
        print("Chaya Echo")
        print("last_scope =", last_scope)
        return shadow_count, current_scope, last_scope

    if line == "presence":
        print("Chaya Presence")
        print("scope =", current_scope)
        print("variables =", len(variables))
        print("shadow =", shadow_count)
        print("functions =", len(functions))
        return shadow_count, current_scope, last_scope

    if line == "version":
        print("Chaya v1.6")
        return shadow_count, current_scope, last_scope

    if line == "about":
        print("Chaya Programming Language")
        print("Shadow • Presence • Reflection • Night")
        print("Version v1.6")
        return shadow_count, current_scope, last_scope

    if line == "clear":
        os.system("cls" if os.name == "nt" else "clear")
        return shadow_count, current_scope, last_scope

    if line == "imports":
        print("Loaded Imports")

        if not imports:
            print("No imports loaded")
        else:
            for file in imports.values():
                print(file)

        return shadow_count, current_scope, last_scope

    if line.startswith("help"):
        command = line[4:].strip()

        help_text = {
            "keep": "store values",
            "say": "print values",
            "ask": "take input",
            "reflect": "inspect variable details",
            "presence": "show current state",
            "echo": "show previous scope",
            "brew": "create function",
            "serve": "run function",
            "import": "load another .chaya file",
            "write": "write data to a file",
            "read": "read a file",
        }

        if command in help_text:
            print(help_text[command])
        else:
            runtime_error(line_no, "Command not found")

        return shadow_count, current_scope, last_scope

    # Everything else goes through executor.py.
    try:
        execute_command(
            line,
            variables,
            shadow_variables,
            functions,
            imports
        )
    except Exception as exc:
        runtime_error(line_no, str(exc))

    return shadow_count, current_scope, last_scope


def run(code):
    variables = {}
    shadow_variables = {}
    shadow_count = 0
    functions = {}
    imports = {}

    current_scope = "main"
    last_scope = "main"

    lines = code.splitlines()

    def execute_range(start, end, lines):
        nonlocal shadow_count, current_scope, last_scope

        i = start

        while i < end:
            line = lines[i].strip()

            if not line or line.startswith("#"):
                i += 1
                continue

            # -------------------
            # import
            # -------------------
            if line.startswith("import "):
                execute_import(
                    line,
                    lines,
                    i,
                    imports,
                    i + 1
                )
                i += 1
                continue

            # -------------------
            # if / else / done
            # -------------------
            if line.startswith("if "):
                else_index, done_index = find_if_parts(lines, i + 1)

                if done_index is None or done_index >= end:
                    runtime_error(i + 1, "Missing done for if block")
                    return

                condition = line[3:].strip()
                result = evaluate_condition(condition, variables)

                if result:
                    block_end = (
                        else_index
                        if else_index is not None
                        else done_index
                    )
                    execute_range(i + 1, block_end, lines)

                elif else_index is not None:
                    execute_range(else_index + 1, done_index, lines)

                i = done_index + 1
                continue

            # -------------------
            # while
            # -------------------
            if line.startswith("while "):
                done_index = find_block_end(lines, i + 1)

                if done_index is None or done_index >= end:
                    runtime_error(i + 1, "Missing done for while loop")
                    return

                condition = line[6:].strip()

                while evaluate_condition(condition, variables):
                    execute_range(i + 1, done_index, lines)

                i = done_index + 1
                continue

            # -------------------
            # for
            # -------------------
            if line.startswith("for "):
                done_index = find_block_end(lines, i + 1)

                if done_index is None or done_index >= end:
                    runtime_error(i + 1, "Missing done for for loop")
                    return

                statement = line[4:].strip()

                try:
                    var_name, remaining = statement.split(" from ", 1)
                    start_value, end_value = remaining.split(" to ", 1)

                    var_name = var_name.strip()
                    start_value = int(start_value.strip())
                    end_value = int(end_value.strip())

                    for value in range(start_value, end_value + 1):
                        variables[var_name] = value
                        execute_range(i + 1, done_index, lines)

                except Exception as exc:
                    print("Chaya For Error:")
                    print(exc)

                i = done_index + 1
                continue

            # -------------------
            # repeat
            # -------------------
            if line.startswith("repeat "):
                done_index = find_block_end(lines, i + 1)

                if done_index is None or done_index >= end:
                    runtime_error(i + 1, "Missing done for repeat")
                    return

                try:
                    count = int(line[7:].strip())

                    for _ in range(count):
                        execute_range(i + 1, done_index, lines)

                except Exception as exc:
                    print("Chaya Repeat Error:")
                    print(exc)

                i = done_index + 1
                continue

            # -------------------
            # brew
            # -------------------
            if line.startswith("brew "):
                done_index = find_block_end(lines, i + 1)

                if done_index is None or done_index >= end:
                    runtime_error(i + 1, "Missing done for brew")
                    return

                func_name = line[5:].strip()

                functions[func_name] = [
                    item.strip()
                    for item in lines[i + 1:done_index]
                    if item.strip()
                ]

                last_scope = current_scope
                current_scope = func_name
                last_scope = func_name
                current_scope = "main"

                i = done_index + 1
                continue

            # -------------------
            # serve
            # -------------------
            if line.startswith("serve "):
                func_name = line[6:].strip()

                if func_name not in functions:
                    runtime_error(i + 1, "Function not found")
                else:
                    previous_scope = current_scope
                    current_scope = func_name

                    function_lines = functions[func_name]

                    for function_line in function_lines:
                        stripped = function_line.strip()

                        if not stripped:
                            continue

                        if stripped.startswith("say "):
                            execute_command(
                                stripped,
                                variables,
                                shadow_variables,
                                functions,
                                imports
                            )
                        else:
                            (
                                shadow_count,
                                current_scope,
                                last_scope
                            ) = execute_command_line(
                                stripped,
                                variables,
                                shadow_variables,
                                shadow_count,
                                functions,
                                imports,
                                current_scope,
                                last_scope,
                                i + 1,
                            )

                    last_scope = func_name
                    current_scope = previous_scope

                i += 1
                continue

            # -------------------
            # done / else outside block
            # -------------------
            if line in ("done", "else"):
                runtime_error(
                    i + 1,
                    f"Unexpected '{line}'"
                )
                i += 1
                continue

            # -------------------
            # normal command
            # -------------------
            (
                shadow_count,
                current_scope,
                last_scope,
            ) = execute_command_line(
                line,
                variables,
                shadow_variables,
                shadow_count,
                functions,
                imports,
                current_scope,
                last_scope,
                i + 1,
            )

            i += 1

    # Start execution
    execute_range(0, len(lines), lines)