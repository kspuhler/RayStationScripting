#Handling for opt structures like rings and intersections etc



class OptStructure(object):
    pass




class RingStructure(object):
    ##creates a ring of radius "radius" around the structure "structure"
    def __init__(self, radius, structure) -> None:
        self.radius = radius
        self.structure = structure



class IntersectionSturcture(object):

    def __init__(self) -> None:
        pass
