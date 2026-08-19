import base64
import copy
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, ClassVar, Mapping, Optional


class Predicate:
    """
    An class representing a Proofpoint ITM Predicate
    """

    def __init__(self, json_data={}):
        data = copy.deepcopy(json_data)

        try:
            self.id = data.get("id")
            self.definition = data.get("definition", {})
            self.patterns = data.get("patterns", [])
            self.predicates = data.get("predicates", [])
            self.purposes = data.get("purposes", [])
            self.lists = data.get("lists", [])
            self.tags = data.get("tags", [])
            self.details = data.get("details", {})
            self.alias = data.get("alias")
            self.risk = data.get("risk", {})
            self.kind = data.get("kind")
            self.refs = []
            for v in self.definition.values():
                self._get_nested_refs(v)
        except Exception as e:
            print(f"Error creating predicate object: {e}")

    def _get_nested_refs(self, data):
        for item in data:
            for k, v in item.items():
                if k == "$ref":
                    logging.info(f"found ref: {v}")
                    self.refs.append(item)
                elif k == "$not":
                    for m, n in v.items():
                        if m == "$ref":
                            logging.info(f"found ref: {n}")
                            self.refs.append(v)
                elif k == "$and" or k == "$or":
                    self._get_nested_refs(v)

    def as_dict(self):
        """
        Returns a dict object with only the keys needed to create a new predicate
        """
        data = {
            "definition": self.definition,
            "patterns": self.patterns,
            "predicates": self.predicates,
            "purposes": self.purposes,
            "lists": self.lists,
            "tags": self.tags,
            "details": self.details,
            "alias": self.alias,
            "risk": self.risk,
            "kind": self.kind,
        }
        return data


class Rule:
    """
    An class representing a Proofpoint ITM Rule
    """

    def __init__(self, json_data={}):
        data = copy.deepcopy(json_data)
        try:
            self.id = data.get("id")
            self.predicate = data.get("predicate", {})
            self.actions = data.get("actions", [])
            self.options = data.get("options", [])
            self.tags = data.get("tags", [])
            self.details = data.get("details", {})
            self.alias = data.get("alias")
            self.status = data.get("status")
            self.kind = data.get("kind")
        except Exception as e:
            print(f"Error creating rule object: {e}")

    def as_dict(self):
        """
        Returns a dict object with only the keys needed to create a new rule
        """
        data = {
            "predicate": self.predicate,
            "actions": self.actions,
            "options": self.options,
            "tags": self.tags,
            "details": self.details,
            "alias": self.alias,
            "status": self.status,
            "kind": self.kind,
        }
        return data


class Tag:
    """
    An class representing a Proofpoint ITM Tag
    """

    def __init__(self, json_data={}):
        data = copy.deepcopy(json_data)
        try:
            self.id = data.get("id")
            self.status = data.get("status")
            self.name = data.get("name")
            self.alias = data.get("alias")
            self.details = data.get("details", {})
        except Exception as e:
            print(f"Error creating rule object: {e}")

    def as_dict(self):
        """
        Returns a dict object with only the keys needed to create a new tag
        """
        data = {
            "status": self.status,
            "name": self.name,
            "alias": self.alias,
            "details": self.details,
        }
        return data


class AgentPolicy:
    """
    An class representing a Proofpoint ITM Agent Policy
    """

    def __init__(self, json_data={}):
        data = copy.deepcopy(json_data)
        try:
            self.id = data.get("id")
            self.alias = data.get("alias")
            self.description = data.get("description")
            self.kind = data.get("kind")
            self.refs = data.get("refs", {"rules": {"rules": []}})
            self.match = data.get("match", {})
            self.settings = data.get("settings", {})
            self.encrypt = data.get("encrypt", False)
            self.deleted = data.get("deleted", False)
            self.priority = data.get("priority", "-1")
        except Exception as e:
            print(f"Error creating agent policy object: {e}")

    def as_dict(self):
        """
        Returns a dict object with only the keys needed to create a new policy
        """
        data = {
            "description": self.description,
            "match": self.match,
            "settings": self.settings,
            "alias": self.alias,
            "kind": self.kind,
            "refs": self.refs,
            "encrypt": self.encrypt,
            "deleted": self.deleted,
            "priority": self.priority,
        }
        return data


class TargetGroup:
    """
    An class representing a Proofpoint ITM Target-Group
    """

    def __init__(self, json_data={}):
        data = copy.deepcopy(json_data)
        try:
            self.id = data.get("id")
            self.displayName = data.get("displayName")
            self.description = data.get("description", "")
            self.alias = data.get("alias")
            self.targets = data.get("targets", [])
            self.purposes = data.get("purposes", [])
            self.extent = data.get("extent", "tenant")
        except Exception as e:
            print(f"Error creating rule object: {e}")

    def as_dict(self):
        """
        Returns a dict object with only the keys needed to create a new target-group
        """
        data = {
            "displayName": self.displayName,
            "description": self.description,
            "targets": self.targets,
            "purposes": self.purposes,
            "alias": self.alias,
            "extent": self.extent,
        }
        return data


class Target:
    """
    A class representing a Proofpoint ITM notification target
    """

    def __init__(self, json_data={}):
        data = copy.deepcopy(json_data)
        try:
            self.id = data.get("id")
            self.details = data.get("details", {})
            self.relations = data.get("relations", [])
            self.kind = data.get("kind")
            self.status = data.get("status")
        except Exception as e:
            print(f"Error creating rule object: {e}")

        try:
            self.template = data["template"]
        except KeyError:
            pass

    def as_dict(self):
        """
        Returns a dict object with only the keys needed to create a new target
        """
        data = {"relations": self.relations, "details": self.details, "status": self.status, "kind": self.kind}
        try:
            data["template"] = self.template
        except Exception:
            pass

        return data


class Dictionary:
    """
    A class representing a Proofpoint ITM dictionary
    """

    def __init__(self, json_data={}):
        data = copy.deepcopy(json_data)
        try:
            self.id = data.get("id")
            self.name = data.get("name")
            self.description = data.get("description")
            self.entries = data.get("entries", [])
        except Exception as e:
            print(f"Error creating dictionary object: {e}")

        try:
            self.category = data["category"]["id"]
        except KeyError:
            print(f"Could not find category id for dictionary: {self.name}")

    def as_dict(self):
        """
        Returns a dict object with only the keys needed to create a new dictionary
        """
        data = {"name": self.name, "description": self.description, "entries": self.entries}

        try:
            data["category"] = self.category
        except Exception:
            pass

        return data


class Detector:
    """
    A class representing a Proofpoint ITM detector
    """

    def __init__(self, json_data={}):
        data = copy.deepcopy(json_data)
        try:
            self.id = data.get("id")
            self.name = data.get("name")
            self.description = data.get("description")
            self.expression = data.get("expression")
            self.dictionaries = data.get("dictionaries", [])
            self.smartIds = data.get("smartIds", [])
        except Exception as e:
            print(f"Error creating dictionary object: {e}")

        try:
            self.category = data["category"]["id"]
        except KeyError:
            pass

    def as_dict(self):
        """
        Returns a dict object with only the keys needed to create a new detector
        """
        data = {
            "name": self.name,
            "description": self.description,
            "expression": self.expression,
            "dictionaries": self.dictionaries,
            "smartIds": self.smartIds,
        }

        try:
            data["category"] = self.category
        except Exception:
            pass

        return data


@dataclass
class DetectorSet:
    """
    A class representing a Proofpoint ITM detector set
    """

    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    is_global: bool = False
    enabledDetectors: list[dict[str, Any]] = field(default_factory=list)
    category: Optional[list["Category"]] = field(default_factory=list)
    is_memory_constrained: bool = False

    @classmethod
    def from_json(cls, d: Optional[dict[str, Any]]) -> Optional["DetectorSet"]:
        if not d:
            return None
        return cls(
            id=d.get("id"),
            name=d.get("name"),
            description=d.get("description"),
            is_global=d.get("global", False),
            enabledDetectors=d.get("enabledDetectors", []),
            category=Category.from_json(d.get("category")),
            is_memory_constrained=d.get("memoryConstrained", False),
        )

    def create_payload(self) -> dict[str, Any]:
        out = {
            "name": self.name,
            "description": self.description,
            "enabledDetectors": [d["id"] for d in self.enabledDetectors],
            "category": self.category.id if self.category else None,
            "isMemoryConstrained": self.is_memory_constrained,
        }
        return {k: v for k, v in out.items() if v is not None}


def _parse_iso_dt(s: Optional[str]) -> Optional[datetime]:
    if s is None:
        return None
    # replace trailing Z
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def b64(s: str) -> str:
    return base64.b64encode(s.encode("utf-8")).decode("utf-8")


def b64_strings(obj: Any) -> Any:
    """
    Recursively base64-encodes all strings in obj.
    - str -> base64(str)
    - list -> map recursively
    - dict -> map values recursively (keys unchanged)
    - everything else unchanged
    """
    if isinstance(obj, str):
        return b64(obj)
    if isinstance(obj, list):
        return [b64_strings(x) for x in obj]
    if isinstance(obj, dict):
        return {k: b64_strings(v) for k, v in obj.items()}
    return obj


@dataclass
class Category:
    """
    A class representing a Proofpoint DLP category
    """

    id: Optional[str]
    name: Optional[str]

    @classmethod
    def from_json(cls, d: Optional[dict[str, Any]]) -> Optional["Category"]:
        if not d:
            return None
        return cls(
            id=d.get("id"),
            name=d.get("name"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
        }


@dataclass
class Boundaries:
    required_prefixes: list[str] = field(default_factory=list)
    required_suffixes: list[str] = field(default_factory=list)
    excluded_prefixes: list[str] = field(default_factory=list)
    excluded_suffixes: list[str] = field(default_factory=list)
    require_word_boundary_before: bool = True
    require_word_boundary_after: bool = True
    exclude_partial_decimals_before: bool = True
    exclude_partial_decimals_after: bool = True

    @classmethod
    def from_json(cls, d: Optional[dict[str, Any]]) -> Optional["Boundaries"]:
        if not d:
            return None
        return cls(
            required_prefixes=d.get("requiredPrefixes", []),
            required_suffixes=d.get("requiredSuffixes", []),
            excluded_prefixes=d.get("excludedPrefixes", []),
            excluded_suffixes=d.get("excludedSuffixes", []),
            require_word_boundary_before=d.get("requireWordBoundaryBefore", True),
            require_word_boundary_after=d.get("requireWordBoundaryAfter", True),
            exclude_partial_decimals_before=d.get("excludePartialDecimalsBefore", True),
            exclude_partial_decimals_after=d.get("excludePartialDecimalsAfter", True),
        )

    def to_dict(self) -> dict[str, Any]:
        raw = {
            "requiredPrefixes": self.required_prefixes,
            "requiredSuffixes": self.required_suffixes,
            "excludedPrefixes": self.excluded_prefixes,
            "excludedSuffixes": self.excluded_suffixes,
            "requireWordBoundaryBefore": self.require_word_boundary_before,
            "requireWordBoundaryAfter": self.require_word_boundary_after,
            "excludePartialDecimalsBefore": self.exclude_partial_decimals_before,
            "excludePartialDecimalsAfter": self.exclude_partial_decimals_after,
        }
        return b64_strings(raw)


@dataclass
class MatchValidator:
    """
    A class representing a Proofpoint Smart ID Match Validator
    """

    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    parameters: dict[str, Any] = field(default_factory=dict)
    parameter_types: dict[str, Any] = field(default_factory=dict)
    parameter_values: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_json(cls, d: Mapping[str, Any]) -> "MatchValidator":
        return cls(
            id=d.get("id"),
            name=d.get("name"),
            description=d.get("description"),
            parameters=d.get("parameters", {}),
            parameter_types=d.get("parameterTypes", {}),
            parameter_values=d.get("parameterValues", {}),
        )

    def to_create_entry(self) -> dict[str, Any]:
        return b64_strings(self.parameter_values or {})


def validators_to_create_map(validators: list[MatchValidator]) -> dict[str, dict[str, Any]]:
    return {v.id: v.to_create_entry() for v in validators if v.id}


@dataclass
class SmartID:
    """
    A class representing a Proofpoint ITM Smart ID
    """

    id: Optional[str] = None
    is_global: bool = False
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[Category] = None
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    regex: Optional[str] = None
    boundaries: Optional[Boundaries] = None
    match_validators: list[MatchValidator] = field(default_factory=list)
    pattern: Optional[str] = None
    detectors: list[dict[str, Any]] = field(default_factory=list)
    detector_sets: list[dict[str, Any]] = field(default_factory=list)

    CREATE_FIELDS: ClassVar[tuple[str, ...]] = (
        "name",
        "description",
        "category",
        "regex",
        "boundaries",
        "matchValidators",
        "pattern",
    )

    @classmethod
    def from_json(cls, d: Optional[dict[str, Any]]) -> Optional["SmartID"]:
        if not d:
            return None
        return cls(
            id=d.get("id"),
            is_global=d.get("global", False),
            name=d.get("name"),
            description=d.get("description"),
            category=Category.from_json(d.get("category")),
            created_at=_parse_iso_dt(d.get("createdAt")),
            modified_at=_parse_iso_dt(d.get("modifiedAt")),
            regex=d.get("regex"),
            boundaries=Boundaries.from_json(d.get("boundaries")),
            match_validators=[MatchValidator.from_json(mv) for mv in d.get("matchValidators", [])],
            pattern=d.get("pattern"),
            detectors=d.get("detectors", []),
            detector_sets=d.get("detectorSets", []),
        )

    def create_payload(self, *, drop_none: bool = False) -> dict[str, Any]:
        """Returns a dict object with only the keys needed to create a new Smart ID"""

        out: dict[str, Any] = {}
        if "name" in self.CREATE_FIELDS:
            out["name"] = self.name
        if "description" in self.CREATE_FIELDS:
            out["description"] = self.description
        if "category" in self.CREATE_FIELDS:
            if self.category and self.category.id:
                out["category"] = self.category.id
        if "regex" in self.CREATE_FIELDS:
            out["regex"] = b64(self.regex)
        if "boundaries" in self.CREATE_FIELDS and self.boundaries is not None:
            out["boundaries"] = self.boundaries.to_dict()
        if "matchValidators" in self.CREATE_FIELDS:
            out["matchValidators"] = validators_to_create_map(self.match_validators)
        if "pattern" in self.CREATE_FIELDS and self.pattern is not None:
            out["pattern"] = self.pattern

        if drop_none:
            out = {k: v for k, v in out.items() if v is not None}

        return out
