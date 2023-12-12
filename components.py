import pandas as pd
from tabulate import tabulate

class DataMemory:
    def __init__(self):
        self.memory = [0] * 65536

    def get_value(self, address):
        return self.memory[address]

    def set_value(self, address, value):
        self.memory[address] = value

    def print_table(self):
        print(tabulate(self.memory.items(), headers=['Address', 'Value'], tablefmt='pretty'))

    def load_from_data_bus(self,cdb):
        address=cdb.get_value()
        self.memory[address]=cdb.get_value()

class RegisterFile:
    def __init__(self,cdb):
        self.cdb=cdb
    Register_status= {
    "r0": None,
    "r1": None,
    "r2": None,
    "r3": None,
    "r4": None,
    "r5": None,
    "r6": None,
    "r7": None,
    
    }
    Register_values= {
        "r0": 0,
        "r1": 0,
        "r2": 0,
        "r3": 0,
        "r4": 0,
        "r5": 0,
        "r6": 0,
        "r7": 0,
    }
    state_of_register_status= {#this is used to store the state of the register status at a given time
    "r0": None,
    "r1": None,
    "r2": None,
    "r3": None,
    "r4": None,
    "r5": None,
    "r6": None,
    "r7": None,
    }
    # def __init__(self):
    #     for i in self.Register_values:
    #         self.Register_values[i]=0
    def get_value(self, register):
        return self.Register_values[register]
    def set_value(self, register, value):
        self.Register_values[register]=value
    def check_data_bus(self):
        for register,reserve_station in self.Register_status.items():
            if reserve_station==self.cdb.get_reservation_station() and self.cdb.get_reservation_station()!=None:
                if register!="r0":
                    self.Register_values[register]=self.cdb.get_value()
                self.Register_status[register]=None

        self.cdb.clear_bus()
    def print_table(self):
        print(tabulate(self.Register_values.items(), headers=['Register', 'Value'], tablefmt='pretty'))
    def print_register_status(self):
        print(tabulate(self.Register_status.items(), headers=['Register', 'Status'], tablefmt='pretty'))
    def save_register_status_state_now(self):
        self.state_of_register_status=self.Register_status.copy()
    def get_register_saved_state(self):
        return self.state_of_register_status.copy()
    def restore_register_status_state(self,state,cleared_reservation_stations):
        cleared_reservation_stations_names_branch=[]
        for station in cleared_reservation_stations:
            cleared_reservation_stations_names_branch.append(station.df["Name"][0])
        for register,station in self.Register_status.items():
            if station in cleared_reservation_stations_names_branch:
                # self.Register_status[register]=state[register]
                self.Register_status[register]=None
    

class CommonDataBus:
    def __init__(self):
        self.value=None
        self.reservation_station=None
    def write_value(self, value, reservation_station):
        self.value=value
        self.reservation_station=reservation_station
    def get_value(self):
        return self.value
    def get_reservation_station(self):
        return self.reservation_station
    def print_table(self):
        print(tabulate([{"Value": self.value, "Reservation Station": self.reservation_station}], headers='keys', tablefmt='pretty'))
    def clear_bus(self):
        self.value=None
        self.reservation_station=None

class ReservationStation:
    def __init__(self, name, register_file,common_data_bus,memory):
        self.register_file=register_file
        self.common_data_bus=common_data_bus
        self.memory=memory
        self.result=None
        reservation_station = {
            "Execution Cycles left": None,
            "Name": name,
            "Busy": False,
            "Op": None,
            "Vj": None,
            "Vk": None,
            "Qj": None,
            "Qk": None,
            "A": None    
        }
        cycles= {
            "Load1": 3,
            "Load2": 3,
            "Store1": 3,
            "Store2": 3,
            "Add1": 2,
            "Add2": 2,
            "Add3": 2,
            "Div": 10,
            "BNE": 1,
            "Nand": 1,
            "Call/Ret": 1,
        }
        # cycles= {
        #     "Load1": 2,
        #     "Load2": 2,
        #     "Store1": 3,
        #     "Store2": 3,
        #     "Add1": 2,
        #     "Add2": 2,
        #     "Add3": 2,
        #     "Div": 12,
        #     "BNE": 1,
        #     "Nand": 6,
        #     "Call/Ret": 1,
        # }
        self.df = pd.DataFrame([reservation_station])
        self.name=name
        self.cycles_needed=cycles[name]
    def can_issue(self):
        return (self.df["Busy"]==False).all()
    def issue_instr(self, instruction):
        self.df["Busy"] = True
        self.df["Op"] = instruction.split()[0]
        self.df["Execution Cycles left"] = self.cycles_needed
        self.df["Qj"] = None
        self.df["Qk"] = None
        # "Load rA, offset(rB)"
        if (self.df["Op"] == "LOAD").all():
            operands = instruction.split()[1:]
            offset = operands[1].split("(")[0]
            self.df["A"] = int(offset)
            ra=operands[0].split(",")[0]
            self.register_file.Register_status[ra]=self.name
            rB = operands[1].split("(")[1].replace(")", "")
            if self.register_file.Register_status[rB] == None:
                self.df["Vj"] = self.register_file.Register_values[rB]
            else:
                self.df["Qj"] = self.register_file.Register_status[rB]
        #STORE rA, offset(rB)
        if (self.df["Op"] == "STORE").all():
            operands = instruction.split()[1:]
            offset = operands[1].split("(")[0]
            self.df["A"] = int(offset)
            ra=operands[0].split(",")[0]
            #self.register_file.Register_status[ra]=self.name
            rB = operands[1].split("(")[1].replace(")", "")
            if self.register_file.Register_status[rB] == None:
                self.df["Vj"] = self.register_file.Register_values[rB]
            else:
                self.df["Qj"] = self.register_file.Register_status[rB]
            if self.register_file.Register_status[ra] == None:
                self.df["Vk"] = self.register_file.Register_values[ra]
            else:
                self.df["Qk"] = self.register_file.Register_status[ra]
        #"ADD rA, rB, rC"
        if (self.df["Op"] == "ADD").all() or (self.df["Op"] == "DIV").all() or (self.df["Op"] == "NAND").all():
            operands = instruction.split()[1:]
            rA = operands[0].split(",")[0]
            rB = operands[0].split(",")[1]
            rC=operands[0].split(",")[2]
            if self.register_file.Register_status[rB] == None:
                self.df["Vj"] = self.register_file.Register_values[rB]
            else:
                self.df["Qj"] = self.register_file.Register_status[rB]
            if self.register_file.Register_status[rC] == None:
                self.df["Vk"] = self.register_file.Register_values[rC]
            else:
                self.df["Qk"] = self.register_file.Register_status[rC]
            self.register_file.Register_status[rA]=self.name
        #"ADDI rA, rB, immediate"
        if (self.df["Op"] == "ADDI").all():
            operands = instruction.split()[1:]
            rA = operands[0].split(",")[0]
            rB = operands[0].split(",")[1]
            immediate=operands[0].split(",")[2]
            if self.register_file.Register_status[rB] == None:
                self.df["Vj"] = self.register_file.Register_values[rB]
            else:
                self.df["Qj"] = self.register_file.Register_status[rB]
            self.register_file.Register_status[rA]=self.name
            self.df["Vk"] = int(immediate) 
        #BNE rA,rB,offset
        if (self.df["Op"] == "BNE").all():
            operands = instruction.split()[1:]
            rA = operands[0].split(",")[0]
            rB = operands[0].split(",")[1]
            offset=operands[0].split(",")[2]
            self.df["A"] = int(offset)
            if self.register_file.Register_status[rA] == None:
                self.df["Vj"] = rA
            else:
                self.df["Qj"] = self.register_file.Register_status[rA]
            if self.register_file.Register_status[rB] == None:
                self.df["Vk"] = rB
            else:
                self.df["Qk"] = self.register_file.Register_status[rB]
        #Call label
        if (self.df["Op"] == "CALL").all():
            self.df["A"]=instruction.split(" ")[1]
            self.df["Op"]="CALL"
        #RET
        if (self.df["Op"] == "RET").all():
            self.df["Op"]="RET"
            self.df["A"]=self.register_file.Register_values["r1"]
    def execute(self):
        if(self.df["Execution Cycles left"]!=0).all() and (self.df["Qk"][0]==None) and (self.df["Qj"][0]==None):
            # if (self.df["Execution Cycles left"][0]!=None):
                # print("Executing instruction: ", self.df["Op"][0])
            self.df["Execution Cycles left"]-=1
        if(self.df["Execution Cycles left"]==0).all():
            if (self.df["Op"] == "LOAD").all():
                address=int(self.df["A"][0])
                self.result=self.memory.get_value(address)
            if (self.df["Op"] == "STORE").all():
                self.result=self.df["Vk"][0]
            if (self.df["Op"] == "ADD").all():
                self.result=self.df["Vj"][0]+self.df["Vk"][0]
            if (self.df["Op"] == "ADDI").all():
                self.result=self.df["Vj"][0]+self.df["Vk"][0]
            if (self.df["Op"] == "DIV").all():
                if self.df["Vk"][0]==0:
                    raise ZeroDivisionError("Divide by zero error")
                self.result=self.df["Vj"][0]//self.df["Vk"][0]
            if (self.df["Op"] == "NAND").all():
                self.result=~(self.df["Vj"][0]&self.df["Vk"])[0]
            if (self.df["Op"] == "BNE").all():
                self.result=self.df["A"][0]
            if (self.df["Op"] == "CALL").all():
                self.result=self.df["A"][0]
            if (self.df["Op"] == "RET").all():
                self.result=self.df["A"][0]
        if((self.df["Op"]=="LOAD").all() or (self.df["Op"]=="STORE").all()) and self.df["Execution Cycles left"][0]==self.cycles_needed-1:
            self.df["A"]=int(self.df["A"][0]+self.df["Vj"][0])
        return (self.df["Execution Cycles left"]==0).all()
    
    def write_result(self, issue_index):
        branch=False
        ret=False
        call=False
        if (self.df["Op"]=="STORE").all():
            #write to data memory
            address=self.df["A"][0]
            self.memory.set_value(address,self.result)
        if (self.df["Op"]=="BNE").all():
            # print("WE ARE A BNE INSTRUCTION!!!")
            if (self.df["Vj"]!=self.df["Vk"]).all():
                #update common data bus with the branch offset
                self.common_data_bus.write_value(self.result,self.df["Name"][0])
                branch=True #return true to indicate that we need to branch
        if (self.df["Op"]=="CALL").all():
            #update common data bus with the jump offset
            self.common_data_bus.write_value(self.result,self.df["Name"][0])
            self.register_file.Register_values["r1"]=issue_index+1
            call=True
        if  (self.df["Op"]=="RET").all():
            self.common_data_bus.write_value(self.result,self.df["Name"][0])
            ret=True
        if (self.df["Op"][0]=="DIV"):
            # print ("At div result is ",self.result)
            self.common_data_bus.write_value(self.result,self.df["Name"][0])
        else:
            #update common data bus
            self.common_data_bus.write_value(self.result,self.df["Name"][0])
        #TODO: handle the case of BNE, CALL, and RET
        #Clear reservation station values for the functional unit
        self.df["Execution Cycles left"]=None
        self.df["Busy"]=False
        self.df["Op"]=None
        self.df["Vj"]=None
        self.df["Vk"]=None
        self.df["Qj"]=None
        self.df["Qk"]=None
        self.df["A"]=None
        return branch,ret,call
        #update of register status is done after reading the data in the register file from the common data bus
    def can_write_result(self):
        return (self.df["Execution Cycles left"]==0).all()
    def print_table(self):
        print(tabulate(self.df, headers='keys', tablefmt='pretty'))
    def check_data_bus(self):
        if (self.df["Qj"]==self.common_data_bus.get_reservation_station()).all():
            self.df["Vj"]=self.common_data_bus.get_value()
            self.df["Qj"]=None
        if (self.df["Qk"]==self.common_data_bus.get_reservation_station()).all():
            self.df["Vk"]=self.common_data_bus.get_value()
            self.df["Qk"]=None
    def clear(self):
        self.df["Execution Cycles left"]=None
        self.df["Busy"]=False
        self.df["Op"]=None
        self.df["Vj"]=None
        self.df["Vk"]=None
        self.df["Qj"]=None
        self.df["Qk"]=None
        self.df["A"]=None
    def clear_dependency(self, cleared_reservation_stations):
        ReservationStations_names=[]
        if cleared_reservation_stations==None:
            return
        for station in cleared_reservation_stations:
            ReservationStations_names.append(station.name)
        # print("At","Reservation ",self.name," ReservationStations_names: ",ReservationStations_names)
        # print("At Reservation station", self.name, "Qj is ",self.df["Qj"], "and Qk is ",self.df["Qk"])
        if self.df["Qj"][0]!=None:
            if self.df["Qj"][0] in ReservationStations_names:
                self.df["Qj"]=None
                for register,station in self.register_file.Register_status.items():
                    if station==self.name:
                        self.df["Vj"]=self.register_file.Register_values[register]
        if self.df["Qk"][0]!=None:
            if self.df["Qk"][0] in ReservationStations_names:
                self.df["Qk"]=None
                for register,station in self.register_file.Register_status.items():
                    if station==self.name:
                        self.df["Vk"]=self.register_file.Register_values[register]
            
class InstructionsTable:
    def __init__(self, instructions):
        self.df = pd.DataFrame(instructions)
        self.issue_index=0
        self.instructions_issued=0
        self.instructions_executed=0
        self.instructions_written=0
    def issue(self):
        self.df.loc[self.issue_index, "Issue"]=True
        self.issue_index+=1
        self.instructions_issued+=1
    def execute(self, index):
        self.df.loc[index,"Execute" ]=True
        self.instructions_executed+=1
    def write_result(self,index):
        self.df.loc[index,"Write Result"]=True
        self.instructions_written+=1
    def print_table(self):
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            print(self.df)
    def get_table(self):
        print(tabulate(self.df, headers='keys', tablefmt='pretty'))
    def get_instruction(self,index):
        return self.df.loc[index,"Instruction"]
    def set_instructions(self, instructions):
        self.instructions=instructions
    def get_instructions_issued(self):
        return self.instructions_issued
    def get_instructions_executed(self):
        return self.instructions_executed
    def get_instructions_written(self):
        return self.instructions_written
    def check_all_before_branch_finished(self,index):
        return (self.df["Write Result"][0:index]==True).all()