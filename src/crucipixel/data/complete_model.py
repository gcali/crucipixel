from time import sleep
from typing import Tuple, List

from crucipixel.data.crucipixel_instance import CrucipixelInstance
from crucipixel.data.crucipixel_scheme import CrucipixelScheme
from crucipixel.data.guides_instance import GuidesInstance


class CrucipixelCompleteModel:

    def __init__(self, scheme: CrucipixelScheme,
                 instances: List[Tuple[CrucipixelInstance, GuidesInstance]]):
        self.scheme = scheme
        if instances:
            print("Instances!")
            print(instances)
            self.instances = instances
        else:
            self.instances = [
                (CrucipixelInstance(len(scheme.rows), len(scheme.cols)),
                GuidesInstance())
            ]

    def to_json_object(self) -> object:
        return {
            'scheme': self.scheme.to_json_object(),
            'instances': [
                (cruci.to_json_object(), guide.to_json_object())
                for cruci, guide in self.instances
            ]
        }

    @staticmethod
    def from_json_object(json_object: object) -> "CrucipixelCompleteModel":
        scheme = CrucipixelScheme.from_json_object(json_object['scheme'])
        instances = [
            (CrucipixelInstance.from_json_object(cruci),
             GuidesInstance.from_json_object(guide))
            for cruci, guide in json_object['instances']
        ]

        return CrucipixelCompleteModel(scheme, instances)
