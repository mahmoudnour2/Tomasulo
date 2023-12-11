import pandas as pd
from tabulate import tabulate
import sys

class DataMemory:
    def __init__(self):
        self.memory = [0] * 65536

    def get_value(self, address):
        return self.memory[address]

    def set_value(self, address, value):
        try:
            self.memory[address] = value
        except Exception as e:
            line_number = sys.exc_info()[-1].tb_lineno
            print(f"An error occurred on line {line_number}: {type(e).__name__} - {str(e)}")

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
    # def __init__(self):
    #     for i in self.Register_values:
    #         self.Register_values[i]=0
    def get_value(self, register):
        return self.Register_values[register]
    def set_value(self, register, value):
        self.Register_values[register]=value
    def check_data_bus(self):
        for key,value in self.Register_status.items():
            if value==self.cdb.get_reservation_station() and self.cdb.get_reservation_station()!=None:
                self.Register_values[key]=self.cdb.get_value()
                self.Register_status[key]=None
    def print_table(self):
        print(tabulate(self.Register_values.items(), headers=['Register', 'Value'], tablefmt='pretty'))

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
            self.register_file.Register_status[rA]=self.name
            if self.register_file.Register_status[rB] == None:
                self.df["Vj"] = self.register_file.Register_values[rB]
            else:
                self.df["Qj"] = self.register_file.Register_status[rB]
            if self.register_file.Register_status[rC] == None:
                self.df["Vk"] = self.register_file.Register_values[rC]
            else:
                self.df["Qk"] = self.register_file.Register_status[rC]
        #"ADDI rA, rB, immediate"
        if (self.df["Op"] == "ADDI").all():
            operands = instruction.split()[1:]
            rA = operands[0].split(",")[0]
            rB = operands[0].split(",")[1]
            immediate=operands[0].split(",")[2]
            self.register_file.Register_status[rA]=self.name
            if self.register_file.Register_status[rB] == None:
                self.df["Vj"] = self.register_file.Register_values[rB]
            else:
                self.df["Qj"] = self.register_file.Register_status[rB]
            self.df["Vk"] = int(immediate) 
        #BNE rA, rB, offset
        if (self.df["Op"] == "BNE").all():
            operands = instruction.split()[1:]
            rA = operands.split(",")[0]
            rB = operands.split(",")[1]
            offset=operands.split(",")[2]
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
            #TODO: implement the logic to issue Call instruction
            label = instruction.split(" ")[1]
            pass
        #RET
        if (self.df["Op"] == "RET").all():
            #TODO: implement the logic to issue return instruction
            pass
    def execute(self):
        #TODO:don't execute if the operands are not ready
        if(self.df["Execution Cycles left"]!=0).all() and (self.df["Qk"][0]==None) and (self.df["Qj"][0]==None):
            if (self.df["Op"] == "ADD").all():
                print("ADD")
            self.df["Execution Cycles left"]-=1
        if(self.df["Execution Cycles left"]==0).all():
            if (self.df["Op"] == "LOAD").all():
                address=int(self.df["A"][0])
                self.result=self.memory.get_value(address)
            if (self.df["Op"] == "STORE").all():
                self.result=self.df["Vk"]
            if (self.df["Op"] == "ADD").all():
                self.result=self.df["Vj"][0]+self.df["Vk"][0]
            if (self.df["Op"] == "ADDI").all():
                self.result=self.df["Vj"][0]+self.df["Vk"][0]
            if (self.df["Op"] == "DIV").all():
                self.result=self.df["Vj"][0]//self.df["Vk"][0]
            if (self.df["Op"] == "NAND").all():
                self.result=~(self.df["Vj"][0]&self.df["Vk"])[0]
            if (self.df["Op"] == "BNE").all():
                self.result=self.df["Vj"][0]-self.df["Vk"][0]
            if (self.df["Op"] == "CALL").all():
                #TODO: implement the logic to execute Call instruction
                pass
            if (self.df["Op"] == "RET").all():
                #TODO: implement the logic to execute return instruction
                pass
        if((self.df["Op"]=="LOAD").all() or (self.df["Op"]=="STORE").all()) and self.df["Execution Cycles left"][0]==self.cycles_needed-1:
            self.df["A"]=int(self.df["A"][0]+self.df["Vj"][0])
        return (self.df["Execution Cycles left"]==0).all()
    def write_result(self):
        try:
            print("Writing result of ", self.name)
            if (self.df["Op"]=="STORE").all():
                #write to data memory
                address=self.df["A"]
                self.memory.set_value(address,self.result)
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
        except Exception as e:
            # Print the exception details along with the line number
            line_number = sys.exc_info()[-1].tb_lineno
            print(f"An error occurred on line {line_number}: {type(e).__name__} - {str(e)}")
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
class InstructionsTable:
    # instructions_queue= {
    # "Operation": ["ADD", "ADD", "ADD"],
    # "Instruction": ["ADD r1, r2, r3)", "ADD r2, r3, r4", "ADD r5, r6, r7"],
    # "Issue": [False, False, False],
    # "Execute": [False, False, False],
    # "Write Result": [False, False, False],
    # }
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
        print(self.df.head())
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