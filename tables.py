import pandas as pd
from tabulate import tabulate
Register_status= {
    "R0": None,
    "R1": None,
    "R2": None,
    "R3": None,
    "R4": None,
    "R5": None,
    "R6": None,
    "R7": None,
}
Register_values= {
    "R0": 0,
    "R1": 0,
    "R2": 5,
    "R3": 0,
    "R4": 0,
    "R5": 0,
    "R6": 0,
    "R7": 0,
}

class FunctionalUnit:
    def __init__(self, name):
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
        self.df = pd.DataFrame([reservation_station])
        self.name=name
        self.cycles_needed=cycles[name]
    def can_issue(self):
        return (self.df["Busy"]==False).all()
    def issue_instr(self, instruction):
        self.df["Busy"] = True
        self.df["Op"] = instruction.split()[0]
        self.df["Execution Cycles left"] = self.cycles_needed
        # "Load rA, offset(rB)"
        if (self.df["Op"] == "Load").all():
            operands = instruction.split()[1:]
            offset = operands[1].split("(")[0]
            self.df["A"] = offset
            ra=operands[0].split(",")[0]
            Register_status[ra]=self.name
            rB = operands[1].split("(")[1].replace(")", "")
            if Register_status[rB] == None:
                self.df["Vj"] = Register_values[rB]
            else:
                self.df["Qj"] = Register_status[rB]
        #STORE rA, offset(rB)
        if (self.df["Op"] == "Store").all():
            operands = instruction.split()[1:]
            offset = operands[1].split("(")[0]
            self.df["A"] = offset
            ra=operands[0].split(",")[0]
            #Register_status[ra]=self.name
            rB = operands[1].split("(")[1].replace(")", "")
            if Register_status[rB] == None:
                self.df["Vj"] = Register_values[rB]
            else:
                self.df["Qj"] = Register_status[rB]
            if Register_status[ra] == None:
                self.df["Vk"] = Register_values[ra]
            else:
                self.df["Qk"] = Register_status[ra]
        #"ADD rA, rB, rC"
        if (self.df["Op"] == "Add").all() or (self.df["Op"] == "Div").all() or (self.df["Op"] == "Nand").all():
            operands = instruction.split()[1:]
            rA = operands.split(",")[0]
            rB = operands.split(",")[1]
            rC=operands.split(",")[2]
            Register_status[rA]=self.name
            if Register_status[rB] == None:
                self.df["Vj"] = rB
            else:
                self.df["Qj"] = Register_status[rB]
            if Register_status[rC] == None:
                self.df["Vk"] = rC
            else:
                self.df["Qk"] = Register_status[rC]
        #BNE rA, rB, offset
        if (self.df["Op"] == "BNE").all():
            operands = instruction.split()[1:]
            rA = operands.split(",")[0]
            rB = operands.split(",")[1]
            offset=operands.split(",")[2]
            self.df["A"] = offset
            if Register_status[rA] == None:
                self.df["Vj"] = rA
            else:
                self.df["Qj"] = Register_status[rA]
            if Register_status[rB] == None:
                self.df["Vk"] = rB
            else:
                self.df["Qk"] = Register_status[rB]
        #Call label
        if (self.df["Op"] == "Call").all():
            #TODO: implement the logic to issue Call instruction
            pass
        #RET
        if (self.df["Op"] == "Return").all():
            #TODO: implement the logic to issue return instruction
            pass
    def execute(self):
        if(self.df["Execution Cycles left"]!=0).all():
            self.df["Execution Cycles left"]-=1
        return (self.df["Execution Cycles left"]==0).all()
    def write_result(self):
        self.df["Execution Cycles left"]=None
        self.df["Busy"]=False
        self.df["Op"]=None
        self.df["Vj"]=None
        self.df["Vk"]=None
        self.df["Qj"]=None
        self.df["Qk"]=None
        self.df["A"]=None
        #update register status
        for i in Register_status:
            if Register_status[i]==self.name:
                Register_status[i]=None
    def can_write_result(self):
        return (self.df["Execution Cycles left"]==0).all()
    def print_table(self):
        print(tabulate(self.df, headers='keys', tablefmt='pretty'))
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
    def get_instructions(self):
        return self.instructions
    def set_instructions(self, instructions):
        self.instructions=instructions
    def get_instructions_issued(self):
        return self.instructions_issued
    def get_instructions_executed(self):
        return self.instructions_executed
    def get_instructions_written(self):
        return self.instructions_written