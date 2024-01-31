from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class IdentityEmail:
    value: str = field(default=None, metadata={"description": "The email address"})
    type: str = field(default=None, metadata={"description": "The type of email address"})
    primary: bool = field(default=None, metadata={"description": "Whether the email address is primary"})

@dataclass
class IdentityAddress:
    streetAddress: str = field(default=None, metadata={"description": "The street address"})
    locality: str = field(default=None, metadata={"description": "The locality"})
    region: str = field(default=None, metadata={"description": "The region"})
    postalCode: str = field(default=None, metadata={"description": "The postal code"})
    country: str = field(default=None, metadata={"description": "The country"})
    primary: bool = field(default=None, metadata={"description": "Whether the address is primary"})

@dataclass
class IdentityPhone:
    value: str = field(default=None, metadata={"description": "The phone number"})
    type: str = field(default=None, metadata={"description": "The type of phone number"})

@dataclass
class IdentityGroup:
    value: str = field(default=None, metadata={"description": "The group name"})
    display: str = field(default=None, metadata={"description": "The display name of the group"})

@dataclass
class IdentityRole:
    value: str = field(default=None, metadata={"description": "The role name"})
    primary: bool = field(default=None, metadata={"description": "Whether the role is primary"})

@dataclass
class IdentityManager:
    managerId: str = field(default=None, metadata={"description": "The ID of the manager"})

@dataclass
class IdentityExtension:
    employeeNumber: int = field(default=None, metadata={"description": "The employee number"})
    costCenter: int = field(default=None, metadata={"description": "The cost center"})
    organization: str = field(default=None, metadata={"description": "The organization"})
    division: str = field(default=None, metadata={"description": "The division"})
    department: str = field(default=None, metadata={"description": "The department"})
    manager: IdentityManager = field(default=None, metadata={"description": "The manager"})

@dataclass
class Identity:
    externalId: str = field(default=None, metadata={"description": "The external ID of the identity"})
    userType: str = field(default=None, metadata={"description": "The type of user"})
    title: str = field(default=None, metadata={"description": "The title of the user"})
    userName: str = field(default=None, metadata={"description": "The username of the user"})
    nickName: str = field(default=None, metadata={"description": "The nickname of the user"})
    displayName: str = field(default=None, metadata={"description": "The display name of the user"})
    profileUrl: str = field(default=None, metadata={"description": "The profile URL of the user"})
    emails: List[IdentityEmail] = field(default_factory=list, metadata={"description": "The emails of the user"})
    addresses: List[IdentityAddress] = field(default_factory=list, metadata={"description": "The addresses of the user"})
    phoneNumbers: List[IdentityPhone] = field(default_factory=list, metadata={"description": "The phone numbers of the user"})
    groups: List[IdentityGroup] = field(default_factory=list, metadata={"description": "The groups of the user"})
    preferredLanguage: str = field(default=None, metadata={"description": "The preferred language of the user"})
    locale: str = field(default=None, metadata={"description": "The locale of the user"})
    timezone: str = field(default=None, metadata={"description": "The timezone of the user"})
    active: bool = field(default=None, metadata={"description": "Whether the user is active"})
    enterpriseExtension: IdentityExtension = field(default=None, metadata={"description": "The enterprise extension of the user"})

