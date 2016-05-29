from typing import Tuple, List

from app.data.crucipixel_instance import CrucipixelInstance
from app.data.crucipixel_scheme import CrucipixelScheme
from app.data.guides_instance import GuidesInstance


class CrucipixelCompleteModel:

    def __init__(self, scheme: CrucipixelScheme,
                 instances: List[Tuple[CrucipixelInstance, GuidesInstance]]):
        self.scheme = scheme
        if instances:
            self.instances = instances
        else:
            self.instances = [
                (CrucipixelInstance(len(scheme.rows), len(scheme.cols)),
                 GuidesInstance())
            ]

        self.file_name_complete = None

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
        try:
            instances = [
                (CrucipixelInstance.from_json_object(cruci),
                 GuidesInstance.from_json_object(guide))
                for cruci, guide in json_object['instances']
            ]
        except KeyError:
            instances = None

        return CrucipixelCompleteModel(scheme, instances)

