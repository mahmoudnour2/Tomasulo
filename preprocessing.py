import pandas as pd
def read_program(file_path):
    lines = []
    with open(file_path, 'r') as file:
        for line in file:
            lines.append(line.strip())
    return lines
def read_data():
    # TODO: Implement the logic to read the data
    pass
def get_instruction_queue():
    instructions = read_program("program.txt")
    operations = []
    for instruction in instructions:
        words = instruction.split()
        first_word = words[0]
        operations.append(first_word)

    instructions_queue = {
        "Operation": operations,
        "Instruction": instructions,
        "Issue": [None for i in range(len(instructions))],
        "Execute": [None for i in range(len(instructions))],
        "Write Result": [None for i in range(len(instructions))]
    }
    instructions_queue = pd.DataFrame(instructions_queue)
    return instructions_queue