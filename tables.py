import pandas as pd
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

class FunctionalUnit:
    def __init__(self, name):
        reservation_station = {
            "Execution Cycles left": None,
            "Name": name,
            "Busy": None,
            "Op": None,
            "Vj": None,
            "Vk": None,
            "Qj": None,
            "Qk": None,
            "A": None    
        }
        cycles= {
            "Load": 3,
            "Store": 3,
            "Add": 2,
            "Div": 10,
            "BNE": 1,
            "Nand": 1,
            "Call": 1,
        }
        self.df = pd.DataFrame(reservation_station)
        self.name=name
        self.cycles_needed=cycles[name]
    def can_issue(self):
        return self.df["Busy"]==False
    def issue_instr(self, instruction):
        self.df["Busy"] = True
        self.df["Op"] = instruction.split()[0]
        self.df["Execution Cycles left"] = self.cycles_needed
        
        if self.df["Op"] == "Load":
            operands = instruction.split()[1:]
            offset = operands[1].split("(")[0]
            rB = operands[1].split("(")[1].replace(")", "")
            self.df["A"] = offset
            if Register_status[rB] == None:
                self.df["Vj"] = rB
            else:
                self.df["Qj"] = Register_status[rB]
        if self.dp["Op"] == "Store":
            operands = instruction.split()[1:]
            offset = operands[1].split("(")[0]
            rB = operands[1].split("(")[1].replace(")", "")
            self.df["A"] = offset
            if Register_status[rB] == None:
                self.df["Vj"] = rB
            else:
                self.df["Qj"] = Register_status[rB]
            rA = operands[0]
            if Register_status[rA] == None:
                self.df["Vk"] = rA
            else:
                self.df["Qk"] = Register_status[rA]
            
            
        # TODO: implement the logic to issue other instructions
        
        pass
    def execute(self):
        if(self.df["Execution Cycles left"]!=0):
            self.df["Execution Cycles left"]-=1
        if (self.df["Execution Cycles left"]==0):
            #TODO: update register status
            pass
        return self.df["Execution Cycles left"]==0
    def write_result(self):
        if(self.df["Execution Cycles left"]==0):
            self.df["Execution Cycles left"]=None
            self.df["Busy"]=False
            self.df["Op"]=None
            self.df["Vj"]=None
            self.df["Vk"]=None
            self.df["Qj"]=None
            self.df["Qk"]=None
            self.df["A"]=None
    def can_write_result(self):
        return self.df["Execution Cycles left"]==0
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
        self.df["Issue"][self.issue_index]=True
        self.issue_index+=1
        self.instructions_issued+=1
    def execute(self, index):
        self.df["Execute"][index]=True
        self.instructions_executed+=1
    def write_result(self,index):
        self.df["Write Result"][index]=True
        self.instructions_executed+=1
    def print_table(self):
        print(self.df)
    def get_table(self):
        return self.df
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