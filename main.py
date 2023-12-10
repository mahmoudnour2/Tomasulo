import pandas as pd
import preprocessing
import tables

register_status= {
    "Qi": []
}
#initializing the reservation stations
load_station_1= tables.FunctionalUnit("Load")
load_station_2= tables.FunctionalUnit("Load")
add_station_1= tables.FunctionalUnit("Add")
add_station_2= tables.FunctionalUnit("Add")
add_station_3= tables.FunctionalUnit("Add")
div_station= tables.FunctionalUnit("Div")
store_station_1= tables.FunctionalUnit("Store")
store_station_2= tables.FunctionalUnit("Store")
bne_station= tables.FunctionalUnit("BNE")
nand_station= tables.FunctionalUnit("Nand")
call_return_station= tables.FunctionalUnit("Call")
functional_units= [load_station_1,load_station_2,add_station_1,add_station_2,add_station_3,div_station,store_station_1,store_station_2,bne_station,nand_station,call_return_station]
#maps instruction type to functional units. Each key resembles a reservation station
Reservation_stations= {
    "Load": [load_station_1,load_station_2],
    "Add": [add_station_1,add_station_2,add_station_3],
    "Div": div_station,
    "Store": [store_station_1,store_station_2],
    "BNE": bne_station,
    "NAND": nand_station,
    "Call/Return": call_return_station
}
functional_unit_to_instruction_map= {
    load_station_1: None,
    load_station_2: None,
    add_station_1: None,
    add_station_2: None,
    add_station_3: None,
    div_station: None,
    store_station_1: None,
    store_station_2: None,
    bne_station: None,
    nand_station: None,
    call_return_station: None
}
#intializing the instruction table
instruction_table=preprocessing.read_program()
instruction_table=tables.InstructionsTable(instruction_table)

issue_index=0
clock=0
while not instruction_table.df["Write Result"].all():
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
    instruction_type=instruction_table.df["Operation"][issue_index]
    suitable_functional_units=Reservation_stations[instruction_type]
    if(suitable_functional_units[i].can_issue() for i in range(len(suitable_functional_units))):#check if any functional unit is available
        for i in range(len(suitable_functional_units)):
            if(suitable_functional_units[i].can_issue()):
                the_available_unit=suitable_functional_units[i]
                break
        the_available_unit.issue_instr(instruction_table["Instruction"].iloc[issue_index])#update reservation station
        instruction_table.issue() #update instruction table (instruction table keeps track of issue_index)
        #register status is updated in the issue_instr function 
        functional_unit_to_instruction_map[the_available_unit]=issue_index
        issue_index+=1
    instruction_table.print_table()
    clock+=1
    