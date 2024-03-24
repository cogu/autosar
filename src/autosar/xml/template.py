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
                 depends: list[TemplateBase] | None = None,
                 append_to_package: bool = True) -> None:
        self.element_name = element_name
        self.namespace_name = namespace_name
        self.package_role = package_role
        self.depends = depends
        self.append_to_package = append_to_package

    @abstractmethod
    def create(self,
               package: ar_element.Package,
               workspace: Workspace,
               dependencies: dict[str, ar_element.ARElement] | None,
               **kwargs) -> ar_element.ARElement:
        """
        Element creation method.

        The workspace will automatically do the following:

        Before call:

        * Make sure any (optional) dependencies have been created
        * Make sure the necessary package has been created
        * Make sure the element doesn't already exists

        After call:

        * Appends the returned element to the package

        """

    def ref(self, workspace: Workspace) -> str:
        """
        Reference the element will have once created
        """
        package_ref = workspace.get_package_ref_by_role(self.namespace_name, self.package_role)
        return package_ref + "/" + self.element_name
