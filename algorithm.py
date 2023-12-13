import main
load_units = input("Enter number of load units: ")
load_cycles= input("Enter number of load cycles: ")
store_units = input("Enter number of store units: ")
store_cycles = input("Enter number of store cycles: ")
bne_units= input("Enter number of branch units: ")
bne_cycles = input("Enter number of branch cycles: ")
call_ret_units = input("Enter number of call/return units: ")
call_ret_cycles = input("Enter number of call/return cycles: ")
add_units = input("Enter number of add units: ")
add_cycles = input("Enter number of add cycles: ")
nand_units = input("Enter number of nand units: ")
nand_cycles = input("Enter number of nand cycles: ")
div_units = input("Enter number of div units: ")
div_cycles = input("Enter number of div cycles: ")
# load_units=2
# store_units=2
# bne_units=1
# call_ret_units=1
# add_units=3
# nand_units=1
# div_units=1
# load_cycles=3
# store_cycles=3
# bne_cycles=1
# call_ret_cycles=1
# add_cycles=2
# nand_cycles=1
# div_cycles=10

program_path= "program.txt"
data_path= "data.txt"
number_of_units= {
    "Load": load_units,
    "Store": store_units,
    "BNE": bne_units,
    "Call/Ret": call_ret_units,
    "Add": add_units,
    "Nand": nand_units,
    "Div": div_units,
    }

number_of_cycles= {
    "Load": load_cycles,
    "Store": store_cycles,
    "BNE": bne_cycles,
    "Call/Ret": call_ret_cycles,
    "Add": add_cycles,
    "Nand": nand_cycles,
    "Div": div_cycles,
    }

main.algorithm(number_of_units, number_of_cycles, program_path, data_path)
