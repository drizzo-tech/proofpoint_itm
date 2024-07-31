from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

class Identity_Attr(BaseModel):
    key: str
    value: str


class Identity_Role(BaseModel):
    value: str
    primary: bool

class Identity_Group(BaseModel):
    value: str
    display: str

class Identity_Address(BaseModel):
    streetAddress: Optional[str] = None
    locality: Optional[str] = None
    region: Optional[str] = None
    postalCode: Optional[str] = None
    country: Optional[str] = None
    primary: Optional[bool] = None

class Identity_Email(BaseModel):
    value: str
    type: Optional[str] = None
    primary: Optional[bool] = None

class Identity_Name(BaseModel):
    givenName: str
    familyName: str
    honorificPrefix: Optional[str] = None

class Identity_Meta_Entity(BaseModel):
    name: Optional[str] = None
    vendor: Optional[str] = None

class Identity_Meta(BaseModel):
    resourceType: str = "User"
    created: Optional[str] = None
    lastModified: Optional[str] = None
    entity: Optional[Identity_Meta_Entity] = None

class Identity_Manager(BaseModel):
    managerId: str

class Identity_Ext_Enterprise(BaseModel):
    employeeNumber: Optional[str] = None
    organization: Optional[str] = None
    division: Optional[str] = None
    department: Optional[str] = None
    manager: Optional[Identity_Manager] = None

class Identity_Ext_Pfpt_Identifier(BaseModel):
    name: str
    value: str

    @field_validator("value")
    @classmethod
    def validate_value(cls, v):
        if len(v) < 6:
            raise ValueError("Identifier value must be at least 6 characters")
        return v

class Identity_Ext_Pfpt_Attribute(BaseModel):
    key: str
    value: str

class Identity_Ext_Pfpt(BaseModel):
    identifiers: Optional[List[Identity_Ext_Pfpt_Identifier]] = None
    attributes: Optional[List[Identity_Ext_Pfpt_Attribute]] = None

class Identity(BaseModel):
    externalId: Optional[str] = None
    userType: Optional[str] = None
    title: Optional[str] = None
    userName: str
    displayName: str
    name: Identity_Name
    emails: List[Identity_Email] = Field(min_length=1)
    addresses: Optional[List[Identity_Address]] = None
    groups: Optional[List[Identity_Group]] = None
    roles: Optional[List[Identity_Role]] = None
    meta: Optional[Identity_Meta] = None
    active: Optional[bool] = None
    urn_scim_schemas_extension_enterprise_1_0: Optional[List[Identity_Ext_Enterprise]] = Field(default=None, serialization_alias="urn:scim:schemas:extension:enterprise:1.0")
    urn_scim_schemas_extension_pfpt_sigma_1_0: Optional[Identity_Ext_Pfpt] = Field(default=None, serialization_alias="urn:scim:schemas:extension:pfpt:sigma:1.0")
