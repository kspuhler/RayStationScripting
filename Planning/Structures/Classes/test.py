from connect import *

case=get_current('Case')
exam=get_current("Examination")


case.PatientModel.RegionsOfInterest['Rectum'].CreateAlgebraGeometry(Examination=exam, Algorithm="Auto", ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["Rectum"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                                                    ExpressionB={ 'Operation': "Union", 'SourceRoiNames': ["PTV_CK"], 'MarginSettings': { 'Type': "Expand", 'Superior': 5, 'Inferior': 2, 'Anterior': 5, 'Posterior': 5, 'Right': 5, 'Left': 5 } }, ResultOperation="Intersection", 
                                                                    ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })