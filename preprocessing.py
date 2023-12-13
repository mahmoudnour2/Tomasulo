import pandas as pd
def read_program(file_path):
    lines = []
    with open(file_path, 'r') as file:
        for line in file:
            lines.append(line.strip())
    return lines
def read_data(file_path, data_memory):
    with open(file_path, 'r') as file:
        for line in file:
            address= int(line.split(",")[0])
            value= int(line.split(",")[1])
            data_memory.set_value(address,value)
def get_instruction_queue(file_path):
    instructions = read_program(file_path)
    operations = []
    for instruction in instructions:
        words = instruction.split()
        first_word = words[0]
        operations.append(first_word)

    instructions_queue = {
        "Operation": operations,
        "Instruction": instructions,
        "Issue": [False for i in range(len(instructions))],
        "Execute": [False for i in range(len(instructions))],
        "Write Result": [False for i in range(len(instructions))]
    }
    instructions_queue = pd.DataFrame(instructions_queue)
    return instructions_queue
def get_instructions_timing_table(file_path):
    
    instructions = read_program(file_path)
    my_range = len(instructions)
    instructions_timing_table = {
        "Instruction": instructions,
        "Issue": [0 for i in range(my_range)],
        "Begin Execute": [0 for i in range(my_range)],
        "End Execute": [0 for i in range(my_range)],
        "Write": [0 for i in range(my_range)]
    }
    instructions_timing_table = pd.DataFrame(instructions_timing_table)
    return instructions_timing_table
