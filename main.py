import pandas as pd
import preprocessing
import components
import sys
import traceback
from tabulate import tabulate

def algorithm(number_of_units,number_of_cycles, program_path, data_path):
    
    #initializing the table for instructions time stamps
    instruction_table_timing=preprocessing.get_instructions_timing_table(program_path)

    #initializing the common data bus
    cdb= components.CommonDataBus()

    #initializing the register file
    register_file= components.RegisterFile(cdb)

    #intializing the instruction table
    instruction_table=preprocessing.get_instruction_queue(program_path)
    instruction_table=components.InstructionsTable(instruction_table)


    #initializing the memory
    data_memory= components.DataMemory()

    #read data from data file into data memory
    preprocessing.read_data(data_path,data_memory)
    #initializing the reservation stations
    reservation_station_to_instruction_map= {
    }
    #maps instruction type to its available reservation units.
    #(ADD and ADDI share the same functional unit) (RET and CALL share the same functional unit)
    functional_units= {
        "LOAD": [],
        "ADD": [],
        "ADDI": [],
        "DIV": [],
        "STORE": [],
        "BNE": [],
        "NAND": [],
        "RET": [],
        "CALL": []
    }
    cycles= {
    }
    Reservation_stations=[]
    for key,value in number_of_units.items():
        if key=="Load":
            for i in range(int(value)):
                station=components.ReservationStation(key+str(i+1), register_file, cdb,data_memory)
                Reservation_stations.append(station)
                functional_units["LOAD"].append(station)
                reservation_station_to_instruction_map[station]=None
                cycles[key+str(i+1)]=number_of_cycles[key]
        elif key=="Store":
            for i in range(int(value)):
                station=components.ReservationStation(key+str(i+1), register_file, cdb,data_memory)
                Reservation_stations.append(station)
                functional_units["STORE"].append(station)
                reservation_station_to_instruction_map[station]=None
                cycles[key+str(i+1)]=number_of_cycles[key]
        elif key=="BNE":
            for i in range(int(value)):
                station=components.ReservationStation(key+str(i+1), register_file, cdb,data_memory)
                Reservation_stations.append(station)
                functional_units["BNE"].append(station)
                reservation_station_to_instruction_map[station]=None
                cycles[key+str(i+1)]=number_of_cycles[key]
        elif key=="Call/Ret":
            for i in range(int(value)):
                station=components.ReservationStation(key+str(i+1), register_file, cdb,data_memory)
                Reservation_stations.append(station)
                functional_units["RET"].append(station)
                functional_units["CALL"].append(station)
                reservation_station_to_instruction_map[station]=None
                cycles[key+str(i+1)]=number_of_cycles[key]
        elif key=="Add":
            for i in range(int(value)):
                station=components.ReservationStation(key+str(i+1), register_file, cdb,data_memory)
                Reservation_stations.append(station)
                functional_units["ADD"].append(station)
                functional_units["ADDI"].append(station)
                reservation_station_to_instruction_map[station]=None
                cycles[key+str(i+1)]=number_of_cycles[key]
        elif key=="Nand":
            for i in range(int(value)):
                station=components.ReservationStation(key+str(i+1), register_file, cdb,data_memory)
                Reservation_stations.append(station)
                functional_units["NAND"].append(station)
                reservation_station_to_instruction_map[station]=None
                cycles[key+str(i+1)]=number_of_cycles[key]
        elif key=="Div":
            for i in range(int(value)):
                station=components.ReservationStation(key+str(i+1), register_file, cdb,data_memory)
                Reservation_stations.append(station)
                functional_units["DIV"].append(station)
                reservation_station_to_instruction_map[station]=None
                cycles[key+str(i+1)]=number_of_cycles[key]

    for station in Reservation_stations:
        station.set_cycles_needed(cycles)
    # load_station_1= components.ReservationStation("Load1", register_file, cdb,data_memory)
    # load_station_2= components.ReservationStation("Load2", register_file,cdb,data_memory)
    # add_station_1= components.ReservationStation("Add1", register_file, cdb,data_memory)
    # add_station_2= components.ReservationStation("Add2", register_file, cdb,data_memory)
    # add_station_3= components.ReservationStation("Add3", register_file, cdb,data_memory)
    # div_station= components.ReservationStation("Div", register_file, cdb,data_memory)
    # store_station_1= components.ReservationStation("Store1", register_file, cdb,data_memory)
    # store_station_2= components.ReservationStation("Store2", register_file, cdb,data_memory)
    # bne_station= components.ReservationStation("BNE", register_file, cdb,data_memory)
    # nand_station= components.ReservationStation("Nand", register_file, cdb,data_memory)
    # call_return_station= components.ReservationStation("Call/Ret", register_file, cdb,data_memory)
    # Reservation_stations= [load_station_1,load_station_2,add_station_1,add_station_2,add_station_3,div_station,store_station_1,store_station_2,bne_station,nand_station,call_return_station]


    #maps instruction type to its available reservation units.
    #(ADD and ADDI share the same functional unit) (RET and CALL share the same functional unit)
    # functional_units= {
    #     "LOAD": [load_station_1,load_station_2],
    #     "ADD": [add_station_1,add_station_2,add_station_3],
    #     "ADDI": [add_station_1,add_station_2,add_station_3],
    #     "DIV": [div_station],
    #     "STORE": [store_station_1,store_station_2],
    #     "BNE": [bne_station],
    #     "NAND": [nand_station],
    #     "RET": [call_return_station],
    #     "CALL": [call_return_station]
    # }
    # reservation_station_to_instruction_map= {
    #     load_station_1: None,
    #     load_station_2: None,
    #     add_station_1: None,
    #     add_station_2: None,
    #     add_station_3: None,
    #     div_station: None,
    #     store_station_1: None,
    #     store_station_2: None,
    #     bne_station: None,
    #     nand_station: None,
    #     call_return_station: None
    # }

    issue_index = 0
    clock = 1
    stall_execution=False
    stall_execution_for_call_or_ret=False
    branch_instr_index=None
    call_or_ret_instr_index=None
    number_of_instructions=len(instruction_table.df)
    skipped_instructions=0
    register_status_at_branch=None
    register_status_at_call_or_ret=None
    no_branch_instructions=0
    taken_branches=0
    while instruction_table.instructions_written+skipped_instructions<number_of_instructions:
        register_file.save_register_status_state_now()
        # print("Clock cycle: ", clock)
        recently_removed_reservation_station=None
        branch=False
        call=False
        ret=False
        #write result if possible
        branch_backwards=False
        indices_of_potential_reservation_stations_to_write=[]
        corresponding_instructions_index=[]
        cleared_reservation_stations=[]
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
                try:
                    for station,instruction_no in reservation_station_to_instruction_map.items():
                        if instruction_no in range(call_or_ret_instr_index+1,target_index):
                            station.clear()
                            cleared_reservation_stations.append(station)
                            reservation_station_to_instruction_map[station]=None
                except Exception as e:
                    # print(f"An error occurred: {type(e).__name__} - {str(e)}")
                    # traceback.print_exc()\
                    pass
                # for cleared in cleared_reservation_stations:
                    # print("Cleared reservation station: ", cleared.name)
                
                #flush instruction table
                try:
                    for i in range(call_or_ret_instr_index+1,issue_index):
                        instruction_table.df.loc[i,"Issue"]=False
                except Exception as e:
                    # print(f"An error occurred: {type(e).__name__} - {str(e)}")
                    # traceback.print_exc()
                    pass
                #remove references of flushed instructions from reservation_stations
                for reservation_station in Reservation_stations:
                    reservation_station.clear_dependency(cleared_reservation_stations)
                cleared_reservation_stations_names_callOrRet=[]
                for station in cleared_reservation_stations_names_callOrRet:
                    cleared_reservation_stations_names_callOrRet.append(station.df["Name"][0])
                #restore register status before branch
                issue_index=target_index#update the PC
                instruction_table.issue_index=issue_index
                stall_execution_for_call_or_ret=False
                skipped_instructions+=(target_index-call_or_ret_instr_index-1)
                # print("End stall execution")
                register_file.restore_register_status_state(register_status_at_call_or_ret, cleared_reservation_stations)
            if branch:
                taken_branches+=1
                no_branch_instructions+=1
                all_before_branch_finished=instruction_table.check_all_before_branch_finished(branch_instr_index)
                if all_before_branch_finished==False:
                    print("Waiting for instructions before branch to finish")
                    continue
                branch_offset=cdb.get_value()
                target_index=branch_instr_index+branch_offset+1
                if target_index<branch_instr_index:
                    branch_backwards=True
                    instruction_table.clear_some_instructions(target_index,branch_instr_index)
                skipped_instructions+=(target_index-branch_instr_index-1)
                
                cleared_reservation_stations=[]
                #flush instructions after branch (from branch_instr_index+1 to the current index)
                #flush= clear corresponding reservation stations and register status and update the instruction table
                #update the PC (issue_index) to the branch instruction's PC + branch_offset + 1
                
                #flush reservation stations
                for station,instruction_no in reservation_station_to_instruction_map.items():
                    if instruction_no in range(branch_instr_index+1,issue_index):
                        station.clear()
                        cleared_reservation_stations.append(station)
                        reservation_station_to_instruction_map[station]=None

                # for cleared in cleared_reservation_stations:
                    # print("Cleared reservation station: ", cleared.name)
                    # print("Our target index is: ", target_index)
                #flush instruction table
                for i in range(branch_instr_index+1,issue_index):
                    instruction_table.df.loc[i,"Issue"]=False
                #remove references of flushed instructions from reservation_stations
                for reservation_station in Reservation_stations:
                    # print("Clearing dependencies of reservation station: ", reservation_station.name)
                    reservation_station.clear_dependency(cleared_reservation_stations)
                #restore register status before branch
                register_file.restore_register_status_state(register_status_at_branch, cleared_reservation_stations)
                
                
                issue_index=target_index#update the PC
                instruction_table.issue_index=issue_index
                stall_execution=False
                # print("End stall execution")
            recently_removed_reservation_station=Reservation_stations[reservation_station_index]
            if branch_backwards==False:
                instruction_table.write_result(most_prior_instruction)#update the instruction table
                instruction_table_timing.loc[most_prior_instruction,"Write"]=int(clock)
            #we update the instruction table after the issue so that we don't 
            # empty a reservation_unit and fill it with another function in the same cycle
        except Exception as e:
            # A generic exception handler (catches any other exception)
            # print(f"An error occurred: {type(e).__name__} - {str(e)}")
            #traceback.print_exc()
            pass
        #execute instruction if possible
        # print("At clock cycle: ", clock, "the stall execution is: ", stall_execution)
        if stall_execution==False and stall_execution_for_call_or_ret==False:
            for i in range(len(Reservation_stations)):
                executed,began_execution=Reservation_stations[i].execute()
                if(executed):
                    instruction_table_timing.loc[reservation_station_to_instruction_map[Reservation_stations[i]],"End Execute"]=int(clock)
                    if Reservation_stations[i].name=="BNE":
                        no_branch_instructions+=1
                    instruction_table.execute(reservation_station_to_instruction_map[Reservation_stations[i]])#update the instruction table
                if(began_execution):
                    instruction_table_timing.loc[reservation_station_to_instruction_map[Reservation_stations[i]],"Begin Execute"]=int(clock)
        else:
            if stall_execution_for_call_or_ret==True:
                ind=call_or_ret_instr_index
            else:
                ind=branch_instr_index
            for station in Reservation_stations:
                #execute instructions before the branch instruction only
                if reservation_station_to_instruction_map[station]!=None:
                    if reservation_station_to_instruction_map[station]<=ind:
                        try:
                            executed=station.execute()
                            if(executed):
                                instruction_table.execute(reservation_station_to_instruction_map[station])
                        except ZeroDivisionError as e:
                            print(f"Error: {type(e).__name__} - {str(e)}")
            
        #issue instruction if possible
        if issue_index<len(instruction_table.df):#check if there are any instructions left to issue 
            instruction_type=instruction_table.df.loc[issue_index,"Operation"]
            #stall execution of other instructions if the instruction issue is a branch
            if instruction_type=="BNE":
                register_status_at_branch=register_file.get_register_saved_state()
                branch_instr_index=issue_index
                stall_execution=True
                # print("Start stall execution for branch")
            if instruction_type=="CALL" or instruction_type=="RET":
                register_status_at_call_or_ret=register_file.get_register_saved_state()
                call_or_ret_instr_index=issue_index
                stall_execution_for_call_or_ret=True
                # print("Start stall execution for call or ret")
            suitable_reservation_stations=functional_units[instruction_type]
            the_available_unit_index=None
            for i in range(len(suitable_reservation_stations)):
                if(suitable_reservation_stations[i].can_issue()) and (suitable_reservation_stations[i]!=recently_removed_reservation_station):
                    the_available_unit_index=i
                    break
            if the_available_unit_index!=None:
                the_available_unit=suitable_reservation_stations[the_available_unit_index]
                instruction_to_issue=instruction_table.get_instruction(issue_index)#get the instruction to issue
                the_available_unit.issue_instr(instruction_to_issue)#update reservation station
                instruction_table.issue() #update instruction table (instruction table keeps track of issue_index)
                instruction_table_timing.loc[issue_index,"Issue"]=int(clock)
                #register status is updated in the issue_instr function 
                reservation_station_to_instruction_map[the_available_unit]=issue_index#keep track of which instruction is issued to which reservation station
                issue_index+=1
        #remove references of flushed instructions from reservation_stations for newly issued instructions
        for reservation_station in Reservation_stations:
            # print("Clearing dependencies of reservation station: ", reservation_station.name)
            reservation_station.clear_dependency(cleared_reservation_stations)
        # read data from the common data bus (into register file or other reservation stations)
        for i in range(len(Reservation_stations)):
            Reservation_stations[i].check_data_bus()
        register_file.check_data_bus()
        # instruction_table.print_table()
        # print("\n")
        # register_file.print_table()
        # register_file.print_register_status()
        # print("In clock cycle: ", clock, "the stall execution is: ", stall_execution)
        # print("The branch instruction index is: ", branch_instr_index)
        # print("\n")
        # for i in range(len(Reservation_stations)):
        #     Reservation_stations[i].print_table()
        clock+=1
        if(clock==100):
            break
    register_file.print_table()
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(tabulate(instruction_table_timing, headers='keys', tablefmt='pretty'))
    print("The number of clock cycles is: ", clock-1)
    print("The number of no branch instructions is: ", no_branch_instructions)
    print("The number of taken branches is: ", taken_branches)
    if no_branch_instructions==0:
        print("The branch misprediction rate is: 0%")
    else:   
        print("The branch misprediction rate is: ", (taken_branches/no_branch_instructions)*100, "%")
    print("The IPC is ", (number_of_instructions-skipped_instructions)/(clock-1))