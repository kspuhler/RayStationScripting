

from connect import *

import tkinter as tk
import sys
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from Planning.Structures.Classes.MakePTV import MakePTV
from Planning.Structures.Functions.checkForContour import checkForContour
from FrontEnd.GenericPopup import GenericPopup
from FrontEnd.CheckWithUserWindow import CheckWithUserWindowBoolean
from FrontEnd.DropdownMenuWindow import DropdownMenuWindow


class MakePTVTangents(MakePTV):
    '''
    This script will make PTV Tangents, and if appropriate, PTV TB Eval (if there is a contour named Tumor Bed or similar).
    
    PTV tangents will be the result of cropping the 50% IDL into the External contour, reducing 6mm, and cropping out of Lung/Liver/Heart.
    
    To run:
        
        1. Set prescription.
        2. Make a norm point at the lung/tissue boundary.
        3. Make sure to close window that pops up if you did not place your own norm point. 
        4. Verify your PTVs.
        
    '''
    
    TUMOR_STRINGS = ['tumor_bed', 'tumorbed', 'tumor bed'] #list of potential structures indiciating the need for TB EVAL

    def __init__(self, RoiName = 'PTV Tangents',  Idl = None):
            
        super().__init__()
        
        
    def getCurrent(self):
        super().getCurrent()
        self.dose = self.plan.TreatmentCourse.TotalDose
        
    def preChecks(self):
        
        try:
            self.idl #if we passed it as a param
        except:
            try:
                self.idl = self.bs.Prescription.PrescriptionDoseReferences[0].DoseValue #rx dose to make idl contours off of
            except:
                self.idl=100.0

        super().preChecks()
        self.hasNormPoint()
        self.checkForDoseCalc()
        
    def makePtv(self):

        if not checkForContour('ptv tangents'):
            self.pm.CreateRoi(Name="PTV Tangents", Color="Red", Type="ptv", TissueName="", RbeCellTypeName=None, RoiMaterial=None)
        
        ptvTanGeometry = self.pm.StructureSets[self.exam.Name].RoiGeometries['PTV Tangents'].OfRoi
        ptvTanGeometry.CreateRoiGeometryFromDose(DoseDistribution=self.dose, ThresholdLevel=self.idl/2.0)
        crop = [x.Name for x in self.pm.RegionsOfInterest if any(y in x.Name.lower() for y in ['lung', 'heart', 'liver'])]

        #Crop into External
        self.pm.RegionsOfInterest['PTV Tangents'].CreateAlgebraGeometry(Examination=self.exam, Algorithm="Auto", ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["PTV Tangents"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                                                        ExpressionB={ 'Operation': "Union", 'SourceRoiNames': ["External"], 'MarginSettings': { 'Type': "Contract", 'Superior': 0, 'Inferior': 0.0, 'Anterior': 0.0, 'Posterior': 0.0, 'Right': 0.0, 'Left': 0.0 } }, 
                                                                        ResultOperation="Intersection", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

        #Crop 0.6cm 
        self.pm.RegionsOfInterest['PTV Tangents'].CreateAlgebraGeometry(Examination=self.exam, Algorithm="Auto", ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["PTV Tangents"], 'MarginSettings': { 'Type': "Contract", 'Superior': 0.6, 'Inferior': 0.6, 'Anterior': 0.6, 'Posterior': 0.6, 'Right': 0.6, 'Left': 0.6} },
                                                                        ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="None", 
                                                                        ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

        
        #Crop out lungs/liver/heart
        self.pm.RegionsOfInterest['PTV Tangents'].CreateAlgebraGeometry(Examination=self.exam, Algorithm="Auto", ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["PTV Tangents"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                                                        ExpressionB={ 'Operation': "Union", 'SourceRoiNames': crop, 'MarginSettings': { 'Type': "Expand", 'Superior': 0.2, 'Inferior': 0.2, 'Anterior': 0.2, 'Posterior': 0.2, 'Right': 0.2, 'Left': 0.2 } }, ResultOperation="Subtraction", 
                                                                        ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

        tb = None  

        for x in self.pm.RegionsOfInterest:
            if x.Name.lower() in self.TUMOR_STRINGS:
                tb = x.Name
                break  

        if tb is not None:
            # Match found and stored in `match`
            self.pm.CreateRoi(Name="PTV_TB_Eval", Color="Pink", Type="ptv", TissueName="", RbeCellTypeName=None, RoiMaterial=None)
            self.pm.RegionsOfInterest['PTV_TB_Eval'].CreateAlgebraGeometry(Examination=self.exam, Algorithm="Auto", ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [tb], 'MarginSettings': { 'Type': "Expand", 'Superior': 1.0, 'Inferior': 1.0, 'Anterior': 1.0, 'Posterior': 1.0, 'Right': 1.0, 'Left': 1.0 } },
                                                                            ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="None", 
                                                                            ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
            
            self.pm.RegionsOfInterest['PTV_TB_Eval'].CreateAlgebraGeometry(Examination=self.exam, Algorithm="Auto", ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["PTV_TB_Eval2"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                                                            ExpressionB={ 'Operation': "Union", 'SourceRoiNames': ["External"], 'MarginSettings': { 'Type': "Contract", 'Superior': 0.5, 'Inferior': 0.5, 'Anterior': 0.5, 'Posterior': 0.5, 'Right': 0.5, 'Left': 0.5 } }, 
                                                                            ResultOperation="Intersection", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
            self.pm.RegionsOfInterest['PTV_TB_Eval'].CreateAlgebraGeometry(Examination=self.exam, Algorithm="Auto", ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["PTV_TB_Eval2"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                                                            ExpressionB={ 'Operation': "Union", 'SourceRoiNames': crop, 'MarginSettings': { 'Type': "Expand", 'Superior': 0.2, 'Inferior': 0.2, 'Anterior': 0.2, 'Posterior': 0.2, 'Right': 0.2, 'Left': 0.2 } }, ResultOperation="Subtraction", 
                                                                            ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
            

        
    #Precheck functions
    def hasNormPoint(self): #Check for norm point, if it does not exist, warn user with a window and place it into plan, user needs to move point sadly
        if not 'norm' in [x.Name.lower() for x in self.pm.PointsOfInterest]:
            self.pm.CreatePoi(Examination=self.exam, Point={ 'x': 0.0, 'y': 0.0, 'z': 0.0 }, Name="norm", Color="Yellow", VisualizationDiameter=1, Type="Undefined")

            w = GenericPopup(title='NO NORM POINT!', message='You need to set a norm point before running the script!\nThe script has made an empty one for you\nplease set location re-run the script!')
            w.showPopup()
            sys.exit()
            

    def checkForDoseCalc(self):
        
        if self.plan.TreatmentCourse.TotalDose.GetDoseStatistic(RoiName="External", DoseType="Max") > 0:
            return 
        else:

            self.bs.SetDefaultDoseGrid(VoxelSize={ 'x': 0.25, 'y': 0.25, 'z': 0.25 })
            self.bs.FractionDose.UpdateDoseGridStructures()
            tmp = self.bs.TreatAndProtect(ShowProgress=True)
            tmp.SetMUAndComputeDose(ForceRecompute=False)
            tmp.ScaleToDoseGoal(DspName=None, RoiName="norm", DoseValue=self.idl, DoseVolume=0, PrescriptionType="DoseAtPoint", LockedBeamNames=None, EvaluateOptimizationFunctionsAfterScaling=False, IncludeBackgroundDose=False)
        self.dose = self.plan.TreatmentCourse.TotalDose
        
    def __repr__(self):
        return  '''This script makes PTV Tangents by calculating plan to give rx dose to norm point and then taking 50%idl and cropping it from anything with "lung" "heart" or "liver" in the name \n
                will also make ptv tb eval if there is a structure matching anything in self.TUMOR_STRINGS'''
                
if __name__ == '__main__':
    tmp = MakePTVTangents()