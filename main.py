import pandas as pd
import preprocessing
import components

#initializing the register file
register_file= components.RegisterFile()

#intializing the instruction table
instruction_table=preprocessing.get_instruction_queue("program.txt")
instruction_table=components.InstructionsTable(instruction_table)

#initializing the common data bus
cdb= components.CommonDataBus()

#initializing the memory

data_memory= components.DataMemory()

#initializing the reservation stations
load_station_1= components.ReservationStation("Load1", register_file, cdb,data_memory)
load_station_2= components.ReservationStation("Load2", register_file,cdb,data_memory)
add_station_1= components.ReservationStation("Add1", register_file, cdb,data_memory)
add_station_2= components.ReservationStation("Add2", register_file, cdb,data_memory)
add_station_3= components.ReservationStation("Add3", register_file, cdb,data_memory)
div_station= components.ReservationStation("Div", register_file, cdb,data_memory)
store_station_1= components.ReservationStation("Store1", register_file, cdb,data_memory)
store_station_2= components.ReservationStation("Store2", register_file, cdb,data_memory)
bne_station= components.ReservationStation("BNE", register_file, cdb,data_memory)
nand_station= components.ReservationStation("Nand", register_file, cdb,data_memory)
call_return_station= components.ReservationStation("Call/Ret", register_file, cdb,data_memory)
Reservation_stations= [load_station_1,load_station_2,add_station_1,add_station_2,add_station_3,div_station,store_station_1,store_station_2,bne_station,nand_station,call_return_station]

#maps instruction type to its available reservation units.
#(ADD and ADDI share the same functional unit) (RET and CALL share the same functional unit)
functional_units= {
    "LOAD": [load_station_1,load_station_2],
    "ADD": [add_station_1,add_station_2,add_station_3],
    "ADDI": [add_station_1,add_station_2,add_station_3],
    "DIV": [div_station],
    "STORE": [store_station_1,store_station_2],
    "BNE": [bne_station],
    "NAND": [nand_station],
    "RET": [call_return_station],
    "CALL": [call_return_station]
}
reservation_station_to_instruction_map= {
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

issue_index = 0
clock = 0
while not instruction_table.df["Write Result"].all():
    print("Clock cycle: ", clock)
    #write result if possible
    for i in range(len(Reservation_stations)):
        if Reservation_stations[i].can_write_result():
            Reservation_stations[i].write_result()
            instruction_table.write_result(reservation_station_to_instruction_map[Reservation_stations[i]])#update the instruction table

    #execute instruction if possible
    for i in range(len(Reservation_stations)):
        executed=Reservation_stations[i].execute()
        if(executed):
            instruction_table.execute(reservation_station_to_instruction_map[Reservation_stations[i]])#update the instruction table

    #issue instruction if possible
    if issue_index<len(instruction_table.df):#check if there are any instructions left to issue 
        print("Issue index: ", issue_index)
        instruction_type=instruction_table.df.loc[issue_index,"Operation"]
        suitable_reservation_stations=functional_units[instruction_type]
        the_available_unit_index=None
        for i in range(len(suitable_reservation_stations)):
            if(suitable_reservation_stations[i].can_issue()):
                the_available_unit_index=i
                print("The available unit index: ", the_available_unit_index)
                break
        if the_available_unit_index!=None:
            the_available_unit=suitable_reservation_stations[the_available_unit_index]
            instruction_to_issue=instruction_table.get_instruction(issue_index)#get the instruction to issue
            the_available_unit.issue_instr(instruction_to_issue)#update reservation station
            instruction_table.issue() #update instruction table (instruction table keeps track of issue_index)
            #register status is updated in the issue_instr function 
            reservation_station_to_instruction_map[the_available_unit]=issue_index#keep track of which instruction is issued to which reservation station
            issue_index+=1

    instruction_table.print_table()
    # for i in range(len(Reservation_stations)):
    #     Reservation_stations[i].print_table()
    clock+=1
    if(clock==10):
        break
print("Instructions issued: ", instruction_table.get_instructions_issued())
register_file.print_table()
