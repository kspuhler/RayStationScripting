'''
breast_sib/BreastPlanOptimizer.py

Simple class dedicated for optimization in the main_breast_sib.py

'''

from __future__ import annotations

# === Raystation import ===
try:
    from connect import set_progress, await_user_input
except Exception:
    pass

class BreastPlanOptimizer:
    def __init__(self, plan, db, optimization_index=0, iterations=2, max_num_segments=8):
        """
        Initialize and automatically optimize the plan.

        :param plan: The RayStation plan object containing optimization parameters.
        :param db: The RayStation database object (used to load templates).
        :param jaws: A list of jaw settings, where each sublist contains [Left, Right, Top, Bottom] for a beam.
        :param template_name: The name of the optimization function template to load (default is "Breast_SIB_Opt").
        :param optimization_index: The index of the plan optimization (default is 1).
        :param iterations: Number of optimization runs (default is 2).
        """
        self.plan = plan
        self.db = db
        self.optimization_index = optimization_index
        self.iterations = iterations 
        self.optimization = plan.PlanOptimizations[self.optimization_index]
        self.max_num_segments = max_num_segments
              
        # Automatically perform all optimization steps
        try:
            set_progress('Optimizing...', percentage = -1)
            self.optimize()
        except Exception:
            set_progress("Waiting on manual optimization...", percentage = -1)
            await_user_input(message="Automated optimization failed.  Please manually optimize.")
            

    def reset_optimization(self):
        """Resets the optimization process."""
        self.optimization.ResetOptimization()

    def set_optimization_parameters(self):
        """Configures optimization and segmentation settings."""
        algorithm = self.optimization.OptimizationParameters.Algorithm
        dose_calc = self.optimization.OptimizationParameters.DoseCalculation
        segment_conversion = self.optimization.OptimizationParameters.TreatmentSetupSettings[0].SegmentConversion

        algorithm.MaxNumberOfIterations = 40
        algorithm.OptimalityTolerance = 0
        dose_calc.ComputeFinalDose = True
        dose_calc.IterationsInPreparationsPhase = 20

        segment_conversion.MaxNumberOfSegments = self.max_num_segments
        segment_conversion.MinNumberOfOpenLeafPairs = 4
        segment_conversion.MinSegmentArea = 5
        segment_conversion.MinSegmentMUPerFraction = 5
        segment_conversion.MinLeafEndSeparation = 2

    def run_optimization(self):
        """Runs the optimization process."""
        for _ in range(self.iterations):
            self.optimization.RunOptimization(ScalingOfSoftMachineConstraints=None)

    def optimize(self):
        """Executes all optimization steps automatically in the correct sequence."""
        self.reset_optimization()
        self.set_optimization_parameters()
        self.run_optimization()
        print("Optimization process completed successfully!")


# Example Usage :
# optimizer = PlanOptimizer(plan, db)
