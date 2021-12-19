"""
Open Understand main driver
to create project parse tree, analyze project, and create symbol table db
It is the same Understand und command line tool

"""
import os
from pprint import pprint

from antlr4 import FileStream, CommonTokenStream, ParseTreeWalker

from analysis_passes.importDemand_importbyDemand import ImportDemandAndImportByDemand
from db.api import open as db_open, create_db, Kind
from db.fill import main
from db.models import ProjectModel, EntityModel, KindModel, ReferenceModel
from gen.javaLabeled.JavaLexer import JavaLexer
from gen.javaLabeled.JavaParserLabeled import JavaParserLabeled


class Project:

    def start_analyze(self, project_address):
        self.imports_star = []
        for root, dirs, files in os.walk(project_address):
            for file in files:
                if file.endswith('.java'):
                    address = os.path.join(root, file)
                    try:
                        stream = FileStream(address)
                    except:
                        print(file, 'can not read')
                        continue
                    lexer = JavaLexer(stream)
                    tokens = CommonTokenStream(lexer)
                    parser = JavaParserLabeled(tokens)
                    tree = parser.compilationUnit()
                    listener = ImportDemandAndImportByDemand(address, file, stream.strdata)
                    walker = ParseTreeWalker()
                    walker.walk(
                        listener=listener,
                        t=tree
                    )
                    if len(listener.imports_star) > 0:
                        self.imports_star.append((listener.ent_file, listener.imports_star))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    db = db_open("/home/nobitex/PycharmProjects/OpenUnderstand/database.db")
    p = Project()
    root = ProjectModel.get_or_none().root
    print("Start Analyze Entity (Package and File)")
    print("...........")
    p.start_analyze(root)
    print("...........")
    print("End Analyze Entity (Package and File)")
    print("---------------------------------------")
    # Add Import and Importby Demand Reference
    print("Start Analyze Reference (ImportDemand and ImportByDemand)")
    print("...........")
    java_unknown_package_kind = KindModel.get_or_none(is_ent_kind=True, _name="Java Unknown Package")
    java_import_demand = KindModel.get_or_none(is_ent_kind=False, _name="Java Import Demand")
    java_importby_demand = KindModel.get_or_none(is_ent_kind=False, _name="Java Importby Demand")
    for import_star in p.imports_star:
        for package in import_star[1]:
            ent = EntityModel.get_or_none(_longname=package[0])
            if ent is None:
                name = package[0]
                if "." in package[0]:
                    package_arr = package[0].split('.')
                    name = package_arr[-2] + "." + package_arr[-1]
                EntityModel.get_or_create(_kind=java_unknown_package_kind, _parent=import_star[0]._id, _name=name,
                                          _longname=package[0],
                                          _contents='')
                print("Add Package Unknown Entity " + package[0])
                ent = EntityModel.get_or_none(_longname=package[0])
            ref = ReferenceModel.get_or_none(_kind=java_import_demand, _file=import_star[0], _ent=ent, _scope=import_star[0])
            if ref is None:
                ReferenceModel.get_or_create(_kind=java_import_demand, _file=import_star[0], _line=package[1], _column=package[2], _ent=ent,
                                         _scope=import_star[0])
                print("Add Import Demand Reference in " + import_star[0]._name + " by " + ent._longname)
            else:
                ref._line = package[1]
                ref._column = package[2]
                ref.save()
            ref = ReferenceModel.get_or_none(_kind=java_importby_demand, _file=import_star[0], _ent=import_star[0],
                                             _scope=ent)
            if ref is None:
                ReferenceModel.get_or_create(_kind=java_importby_demand, _file=import_star[0], _line=package[1],
                                             _column=package[2], _ent=import_star[0],
                                             _scope=ent)
                print("Add Importby Demand Reference in "+import_star[0]._name+" by "+ent._longname)
            else:
                ref._line = package[1]
                ref._column = package[2]
                ref.save()
    print("...........")
    print("Stop Analyze Reference (ImportDemand and ImportByDemand)")
    # create_db("/home/nobitex/PycharmProjects/OpenUnderstand/database.db", project_dir="/home/nobitex/PycharmProjects/OpenUnderstand/benchmark/calculator_app")
    # main()
#     db = db_open("/home/nobitex/PycharmProjects/OpenUnderstand/database.db")
#     ent = db.lookup("Admin", "method")[0]
#     """
#     Use name Admin.java(3) Java Use
# Use id Admin.java(4) Java Use
# Use grade Admin.java(5) Java Use
#     """
#     print(ent, ent.kind())
#     print(ent, ent.simplename())
#     for ref in ent.refs(entkindstring="method", unique=True):
#         print(ref)
#
