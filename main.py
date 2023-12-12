import pandas as pd
import preprocessing
import components
import sys
#initializing the common data bus
cdb= components.CommonDataBus()

#initializing the register file
register_file= components.RegisterFile(cdb)

#intializing the instruction table
instruction_table=preprocessing.get_instruction_queue("program.txt")
instruction_table=components.InstructionsTable(instruction_table)


#initializing the memory
data_memory= components.DataMemory()

#read data from data file into data memory
preprocessing.read_data("data.txt",data_memory)

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
clock = 1
stall_execution=False
branch_instr_index=None
number_of_instructions=len(instruction_table.df)
skipped_instructions=0
while instruction_table.instructions_written+skipped_instructions<number_of_instructions:
    print("Clock cycle: ", clock)
    recently_removed_reservation_station=None
    branch=False
    #write result if possible
    indices_of_potential_reservation_stations_to_write=[]
    corresponding_instructions_index=[]
    for i in range(len(Reservation_stations)):
        if Reservation_stations[i].can_write_result():
            indices_of_potential_reservation_stations_to_write.append(i)
            corresponding_instructions_index.append(reservation_station_to_instruction_map[Reservation_stations[i]])
    try:
        most_prior_instruction = min(corresponding_instructions_index)
        reservation_station_index=indices_of_potential_reservation_stations_to_write[corresponding_instructions_index.index(most_prior_instruction)]
        branch,ret,call=Reservation_stations[reservation_station_index].write_result(issue_index)
        if call or ret:
            target_index=cdb.get_value()
            #flush instructions after return (from issue_index to the current index)
            #flush= clear corresponding reservation stations and register status and update the instruction table
            #update the PC (issue_index) to the return instruction's PC + 1
            cleared_reservation_stations=[]
            #flush reservation stations
            for station,instruction_no in reservation_station_to_instruction_map.items():
                if instruction_no in range(issue_index,target_index):
                    station.clear()
                    cleared_reservation_stations.append(station)
                    reservation_station_to_instruction_map[station]=None

            for cleared in cleared_reservation_stations:
                print("Cleared reservation station: ", cleared.name)
            #flush instruction table
            for issue_state in instruction_table.df["Issue"][issue_index:issue_index+1]:
                issue_state=False
            #remove references of flushed instructions from reservation_stations
            for reservation_station in Reservation_stations:
                reservation_station.clear_dependency(cleared_reservation_stations)
            #flush register status (flushed after the references problem is solved, because we need the register status to clear the reservation stations dependencies)
            for register,station in register_file.Register_status.items():
                if station in cleared_reservation_stations:
                    register_file.Register_status[register]=None
        if branch:
            print("Branch instruction")
            branch_offset=cdb.get_value()
            bne_station=Reservation_stations[8]
            index_of_branch_instruction=reservation_station_to_instruction_map[bne_station]
            target_index=index_of_branch_instruction+branch_offset+1
            skipped_instructions+=(target_index-issue_index-1)

            cleared_reservation_stations=[]
            #flush instructions after branch (from index_of_branch_instruction+1 to the current index)
            #flush= clear corresponding reservation stations and register status and update the instruction table
            #update the PC (issue_index) to the branch instruction's PC + branch_offset + 1
            
            #flush reservation stations
            for station,instruction_no in reservation_station_to_instruction_map.items():
                if instruction_no in range(index_of_branch_instruction+1,issue_index):
                    station.clear()
                    cleared_reservation_stations.append(station)
                    reservation_station_to_instruction_map[station]=None

            for cleared in cleared_reservation_stations:
                print("Cleared reservation station: ", cleared.name)
            #flush instruction table
            for issue_state in instruction_table.df["Issue"][index_of_branch_instruction:issue_index]:
                issue_state=False
            #remove references of flushed instructions from reservation_stations
            for reservation_station in Reservation_stations:
                reservation_station.clear_dependency(cleared_reservation_stations)
            #flush register status (flushed after the references problem is solved, because we need the register status to clear the reservation stations dependencies)
            for register,station in register_file.Register_status.items():
                if station in cleared_reservation_stations:
                    register_file.Register_status[register]=None

            issue_index=target_index#update the PC
            instruction_table.issue_index=issue_index
            stall_execution=False
            print("End stall execution")
        recently_removed_reservation_station=Reservation_stations[reservation_station_index]
        instruction_table.write_result(most_prior_instruction)#update the instruction table
        #we update the instruction table after the issue so that we don't 
        # empty a reservation_unit and fill it with another function in the same cycle
    except Exception as e:
        # Print the exception details along with the line number
        line_number = sys.exc_info()[-1].tb_lineno
        print(f"An error occurred on line {line_number}: {type(e).__name__} - {str(e)}")
    #execute instruction if possible
    #TODO: if the instruction being executed is a branch, stop executing the rest of the instructions
    if stall_execution==False:
        for i in range(len(Reservation_stations)):
            executed=Reservation_stations[i].execute()
            if(executed):
                instruction_table.execute(reservation_station_to_instruction_map[Reservation_stations[i]])#update the instruction table
    else:
        for station in Reservation_stations:
            #execute instructions before the branch instruction only
            if reservation_station_to_instruction_map[station]!=None:
                if reservation_station_to_instruction_map[station]<=branch_instr_index:
                    executed=station.execute()
                    if(executed):
                        instruction_table.execute(reservation_station_to_instruction_map[station])
        
    #issue instruction if possible
    if issue_index<len(instruction_table.df):#check if there are any instructions left to issue 
        instruction_type=instruction_table.df.loc[issue_index,"Operation"]
        #stall execution of other instructions if the instruction issue is a branch
        if instruction_type=="BNE":
            branch_instr_index=issue_index
            stall_execution=True
            print("Start stall execution")
        suitable_reservation_stations=functional_units[instruction_type]
        the_available_unit_index=None
        for i in range(len(suitable_reservation_stations)):
            if(suitable_reservation_stations[i].can_issue()) and (suitable_reservation_stations[i]!=recently_removed_reservation_station):
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
    # read data from the common data bus (into register file or other reservation stations)
    for i in range(len(Reservation_stations)):
        Reservation_stations[i].check_data_bus()
    register_file.check_data_bus()
    instruction_table.print_table()
    register_file.print_table()
    print("In clock cycle: ", clock, "the stall execution is: ", stall_execution)
    print("The branch instruction index is: ", branch_instr_index)
    print("\n")
    clock+=1
    if(clock==100):
        break
register_file.print_table()
