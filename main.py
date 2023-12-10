import pandas as pd
import preprocessing
import tables

#initializing the reservation stations
load_unit_1= tables.FunctionalUnit("Load1")
load_unit_2= tables.FunctionalUnit("Load2")
add_unit_1= tables.FunctionalUnit("Add1")
add_unit_2= tables.FunctionalUnit("Add2")
add_unit_3= tables.FunctionalUnit("Add3")
div_unit= tables.FunctionalUnit("Div")
store_unit_1= tables.FunctionalUnit("Store1")
store_unit_2= tables.FunctionalUnit("Store2")
bne_unit= tables.FunctionalUnit("BNE")
nand_unit= tables.FunctionalUnit("Nand")
call_return_unit= tables.FunctionalUnit("Call/Ret")
functional_units= [load_unit_1,load_unit_2,add_unit_1,add_unit_2,add_unit_3,div_unit,store_unit_1,store_unit_2,bne_unit,nand_unit,call_return_unit]
#maps instruction type to functional units. Each key resembles a reservation station
Reservation_stations= {
    "LOAD": [load_unit_1,load_unit_2],
    "ADD": [add_unit_1,add_unit_2,add_unit_3],
    "ADDI": [add_unit_1,add_unit_2,add_unit_3],
    "DIV": [div_unit],
    "STORE": [store_unit_1,store_unit_2],
    "BNE": [bne_unit],
    "NAND": [nand_unit],
    "RET": [call_return_unit],
    "CALL": [call_return_unit]
}
functional_unit_to_instruction_map= {
    load_unit_1: None,
    load_unit_2: None,
    add_unit_1: None,
    add_unit_2: None,
    add_unit_3: None,
    div_unit: None,
    store_unit_1: None,
    store_unit_2: None,
    bne_unit: None,
    nand_unit: None,
    call_return_unit: None
}
#intializing the instruction table
instruction_table=preprocessing.get_instruction_queue("program.txt")
instruction_table=tables.InstructionsTable(instruction_table)

issue_index=0
clock=0
while not instruction_table.df["Write Result"].all():
    print("Clock cycle: ", clock)
    #write result if possible
    for i in range(len(functional_units)):
        if functional_units[i].can_write_result():
            functional_units[i].write_result()
            instruction_table.write_result(functional_unit_to_instruction_map[functional_units[i]])#update the instruction table

    #execute instruction if possible
    for i in range(len(functional_units)):
        executed=functional_units[i].execute()
        if(executed):
            instruction_table.execute(functional_unit_to_instruction_map[functional_units[i]])#update the instruction table

    #issue instruction if possible
    if issue_index<len(instruction_table.df):#check if there are any instructions left to issue 
        print("Issue index: ", issue_index)
        instruction_type=instruction_table.df.loc[issue_index,"Operation"]
        suitable_functional_units=Reservation_stations[instruction_type]
        the_available_unit_index=None
        for i in range(len(suitable_functional_units)):
            if(suitable_functional_units[i].can_issue()):
                the_available_unit_index=i
                print("The available unit index: ", the_available_unit_index)
                break
        if the_available_unit_index!=None:
            the_available_unit=suitable_functional_units[the_available_unit_index]
            instruction_to_issue=instruction_table.get_instruction(issue_index)#get the instruction to issue
            the_available_unit.issue_instr(instruction_to_issue)#update reservation station
            instruction_table.issue() #update instruction table (instruction table keeps track of issue_index)
            #register status is updated in the issue_instr function 
            functional_unit_to_instruction_map[the_available_unit]=issue_index
            issue_index+=1

    instruction_table.print_table()
    # for i in range(len(functional_units)):
    #     functional_units[i].print_table()
    clock+=1
    if(clock==10):
        break
print("Instructions issued: ", instruction_table.get_instructions_issued())
