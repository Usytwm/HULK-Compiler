from src.tools.ast_nodes import *
from src.cmp.semantic import *
import src.cmp.visitor as visitor


class TypeBuilderVisitor:
    def __init__(self, context: Context, scope: Scope, errors: List[str]) -> None:
        self.context = context
        self.scope = scope
        self.errors = errors
        self.currentType: Type

    @visitor.on("node")
    def visit(self, node, tabs):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node: ProgramNode):
        for classDef in node.statments:
            self.visit(classDef)

    @visitor.when(TypeDefinitionNode)
    def visit(self, node: TypeDefinitionNode):
        self.currentType: Type = self.context.get_type(node.id)
        try:
            inheritance = self.context.get_type(node.inheritance)
        except:
            self.errors.append(f"El tipo {node.inheritance} no esta definido")
            inheritance = self.context.get_type("object")

        self.currentType.inheritance = inheritance

        for param in node.parameters:
            name = param.items[0].key
            value = param.items[0].value

            type = self.context.get_type(value)
            try:
                self.currentType.define_argument(name, type)
            except:
                self.errors.append(f"El tipo {value} no esta definido")

        for attrDef in node.attribute:
            self.visit(attrDef)
        for methodDef in node.methods:
            self.visit(methodDef)

        self.currentType = None

    @visitor.when(KernAssigmentNode)
    def visit(self, node: KernAssigmentNode):
        if node.id in self.args:
            self.currentType.define_attribute(node.id, self.args[node.id])
        else:
            attr_type = self.context.get_type(node.id)
            if self.currentType.get_attribute(node.id, attr_type) is not None:
                self.currentType.define_attribute(node.id, attr_type)
            else:
                self.currentType.define_attribute(node.id, Type("object"))

    @visitor.when(FunctionDefinitionNode)
    def visit(self, node: FunctionDefinitionNode):
        try:
            return_type = self.context.get_type(node.type_annotation)
        except:
            self.errors.append(f"El tipo de retorno {node.id} no esta definido")
            return_type = self.context.get_type("object")
        arg_types = []
        for param in node.parameters:
            try:
                arg_types.append(self.context.get_type(param.items[0].value))
            except:
                self.errors.append(
                    f"El tipo de retorno {param.items[0].value} no esta definido"
                )
                arg_types.append(self.context.get_type("object"))

        arg_names = [
            t.items[0].key for t in node.parameters if t[0].key in self.context
        ]
        if self.currentType:
            try:
                self.currentType.define_method(
                    node.id, arg_names, arg_types, return_type
                )
            except:
                self.errors.append(f"La funcion {node.id} ya existe en el contexto")
        else:
            exist = False
            for func in self.scope.functions[node.id]:
                if len(arg_names) == len(func.param_names):
                    exist = True
                    break
            if exist:
                self.errors.append(f"La funcion {node.id} ya existe en el contexto")
            else:
                method = Method(node.id, arg_names, arg_types, return_type)
                self.scope.functions[node.id].append(method)
