"""
Template classes
"""
from abc import ABC, abstractmethod
from typing import Any, TypeVar
import autosar.xml.enumeration as ar_enum
import autosar.xml.element as ar_element

Workspace = TypeVar("Workspace")
Package = TypeVar("Package")


class TemplateBase(ABC):
    """
    Base class for all Templates
    """


class GenericTemplate(TemplateBase):
    """
    Generic template class

    This gives the user the most flexibility
    but the Workspace will not do anything to help.
    """

    @abstractmethod
    def apply(self, workspace: Workspace, **kwargs) -> Any:
        """
        Apply this template to the workspace
        """


class ElementTemplate(TemplateBase):
    """
    Template class for elements.

    Requires that a namespace has been
    setup in the workspace before calling
    the apply method
    """

    def __init__(self,
                 element_name: str,
                 namespace_name: str,
                 package_role: ar_enum.PackageRole,
                 depends: list[TemplateBase] | None = None) -> None:
        self.element_name = element_name
        self.namespace_name = namespace_name
        self.package_role = package_role
        self.depends = depends

    @abstractmethod
    def apply(self, package: Package, workspace: Workspace, **kwargs) -> ar_element.ARElement:
        """
        This apply method shall solely focus on creating the
        new element and return it. The workspace will handle the rest.

        The workspace will automatically do the following:

        * Make sure any dependencies have been created (optional)
        * Make sure the necessary package has been created
        * Make sure the element doesn't already exists

        It's up to the implementer of the apply-method to call package.append to add the newly
        created element
        """

    def ref(self, workspace: Workspace) -> str:
        """
        Reference the element will have once created
        """
        package_ref = workspace.get_package_ref_by_role(self.namespace_name, self.package_role)
        return package_ref + "/" + self.element_name
