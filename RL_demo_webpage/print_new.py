from pyscript import document, window

javi_buffer = ""
found_key = False 

def print_custom_terminal(output_type, string):
    if output_type == 'color':
        document.getElementById('colorOutput').innerHTML += string + " <br>"
    elif output_type == 'action':
        document.getElementById('actionOutput').innerHTML += string + " <br>"
    elif output_type == 'reward':
        document.getElementById('rewardOutput').innerHTML += string + " <br>"
    window.setTimeout(window.scrollTerminalToBottom, 0)

def find_print_statements(buffer):
    statements = []
    start_index = 0
    while start_index < len(buffer):
        end_new_line_index = buffer.find("\n", start_index)
        if end_new_line_index == -1:
            break
        statement = buffer[start_index:end_new_line_index]
        statements.append(statement)
        start_index = end_new_line_index + 1
    return statements

def process_chunks(chunk):
    global javi_buffer
    global found_key
    javi_buffer += chunk
    if not found_key:
        key_index = javi_buffer.find("#**END-CODE**#")
        if key_index == -1:
            last_newline_pos = javi_buffer.rfind("\n")
            if last_newline_pos != -1:
                javi_buffer = javi_buffer[last_newline_pos + 1:]
        else:
            print("FOUND)")
            found_key = True
            start_point = javi_buffer.find("\n", key_index)
            javi_buffer = javi_buffer[start_point + 1:]
    if found_key:
        print_statements = find_print_statements(javi_buffer)
        if print_statements:
            for statement in print_statements:
                print_statement = statement.strip()
                print("***", print_statement)
                if "Color:" in print_statement:
                    print_custom_terminal('color', print_statement)
                elif "Action:" in print_statement:
                    print_custom_terminal('action', print_statement)
                elif "Reward:" in print_statement:
                    print_custom_terminal('reward', print_statement)
    return javi_buffer

def on_data_jav(chunk):
    global javi_buffer
    javi_buffer = process_chunks(chunk)
