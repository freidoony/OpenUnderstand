
"""
## Description
This module find all OpenUnderstand import demand and importby demand references in a Java project


## References


"""

__author__ = 'Rahim Fereydoni'
__version__ = '0.1.0'

from db.models import EntityModel, KindModel
from gen.javaLabeled.JavaParserLabeled import JavaParserLabeled
from gen.javaLabeled.JavaParserLabeledListener import JavaParserLabeledListener


class ImportDemandAndImportByDemand(JavaParserLabeledListener):

    def __init__(self, file_name, name, content):
        self.imports_star = []
        self.file_name = file_name
        self.name = name
        self.content = content
        java_file_kind = KindModel.get_or_none(is_ent_kind=True, _name="Java File")
        self.ent_file = EntityModel.get_or_none(_kind=java_file_kind, _name=name, _longname=file_name)
        if self.ent_file is None:
            EntityModel.get_or_create(_kind=java_file_kind, _name=name, _longname=file_name,
                                      _contents=content)
            print("Add File Entity " + name)
            self.ent_file = EntityModel.get_or_none(_kind=java_file_kind, _name=name, _longname=file_name)
        else:
            self.ent_file._contents = content
            self.ent_file.save()
        self.imports_star = []

    def enterImportDeclaration(self, ctx: JavaParserLabeled.ImportDeclarationContext):
        if '*' in ctx.getText():
            self.imports_star.append((ctx.qualifiedName().getText(), ctx.start.line, ctx.start.column))

    def enterPackageDeclaration(self, ctx: JavaParserLabeled.PackageDeclarationContext):
        package = ctx.qualifiedName().getText()
        name = package
        package_arr = []
        if "." in package:
            package_arr = package.split('.')
            name = package_arr[-2] + "." + package_arr[-1]
        java_package_kind = KindModel.get_or_none(is_ent_kind=True, _name="Java Package")
        ent = EntityModel.get_or_none(_kind=java_package_kind, _name=name, _longname=package)
        if (ent is not None) and (self.name.lower() < ent._parent._name.lower()):
            ent._parent = self.ent_file._id
            ent.save()
        elif ent is None:
            EntityModel.get_or_create(_kind=java_package_kind, _parent=self.ent_file._id, _name=name, _longname=package,
                                      _contents='')
            print("Add Package Entity " + package)
        for i in range(1, len(package_arr)):
            subpackage = package_arr[0:i]
            package = ".".join(subpackage)
            if len(subpackage) > 1:
                name = subpackage[-2] + "." + subpackage[-1]
            else:
                name = package
            ent = EntityModel.get_or_none(_kind=java_package_kind, _name=name, _longname=package)
            if ent is None:
                EntityModel.get_or_create(_kind=java_package_kind, _parent=self.ent_file._id, _name=name,
                                          _longname=package,
                                          _contents='')
                print("Add SubPackage Entity " + package)
            else:
                ent._parent = self.ent_file._id
                ent.save()
