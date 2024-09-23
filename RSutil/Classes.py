from connect import *

class PlanReader(object):
    
    '''Anything can inherit this object in order to automatically populate
    self.plan/pm/beamset/exam etc
    '''
    
    def __init__(self):
        try:
            self.patient = get_current('Patient')
        except:
            pass
        try:
            self.mrn = self.patient.PatientID
        except:
            pass
        try:
           self.case = get_current('Case')
        except:
           pass
        try:
           self.plan = get_current('Plan')
        except:
           pass
        try:
           self.exam = get_current('Examination')
        except:
           pass
        try:
           self.pm = self.pm.PatientModel
        except:
           pass
        try:
          self.ss = self.pm.StructureSets[self.exam.Name]
        except:
           pass
        try:
            self.plan = get_current('Plan')
        except:
            pass
        try:
            self.bs = get_current("BeamSet")
        except:
            pass

    def getMachine(self):
        if hasattr(self, 'bs'):
            self.txMachine = self.bs.MachineReference.MachineName
        else:
            raise Exception("Cannot get machine name!")


if __name__ == "__main__":
    a = PlanReader()