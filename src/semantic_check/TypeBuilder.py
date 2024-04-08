from src.tools.ast_nodes import *
from src.cmp.semantic import *
import src.cmp.visitor as visitor


class TypeBuilderVisitor:
    def __init__(self, context: Context, scope: Scope, errors) -> None:
        self.context: Context = context
        self.scope: Scope = scope
        self.errors: List[str] = errors
        self.currentType: Type = None

    @visitor.on("node")
    def visit(self, node, tabs):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node: ProgramNode):
        for statment in node.statments:
            self.visit(statment)

    @visitor.when(TypeDefinitionNode)
    def visit(self, node: TypeDefinitionNode):
        self.currentType: Type = self.context.get_type(node.id.id)
        try:
            inheritance = self.context.get_type(node.inheritance.type.id)
            if inheritance.conforms_to(self.currentType.name):
                self.errors.append(
                    SemanticError(
                        f"Dependencias circulares. El tipo {node.id.id} hereda de el tipo {node.inheritance.type.id}. --> row:{node.location[0]}, col:{node.location[1]}"
                    )
                )
                inheritance = self.context.get_type("object")
        except:
            self.errors.append(
                SemanticError(
                    f"El tipo {str(node.inheritance.type.id)} del que se hereda no esta definido. --> row:{node.inheritance.location[0]}, col:{node.inheritance.location[1]}"
                )
            )
            inheritance = self.context.get_type("object")

        self.currentType.inhertance = inheritance

        for arg in node.parameters:
            name: IdentifierNode = list(arg.items())[0][0]
            type: TypeNode = list(arg.items())[0][1]

            try:
                type = self.context.get_type(type.type)
            except:
                type = self.context.get_type("object")
                self.errors.append(
                    SemanticError(
                        f"El tipo del argumento {name.id} no esta definido. --> row:{type.location[0]}, col:{type.location[1]}"
                    )
                )

            try:
                self.currentType.define_arg(name.id, type)
            except:
                self.errors.append(
                    SemanticError(
                        f"Existenten dos argumentos con el nombre {name.id} --> row:{name.location[0]}, col:{name.location[1]}"
                    )
                )

        for attrDef in node.attributes:
            self.visit(attrDef)

        for methodDef in node.methods:
            self.visit(methodDef)

        self.currentType = None

    @visitor.when(KernAssigmentNode)
    def visit(self, node: KernAssigmentNode):
        if self.currentType:
            try:
                self.currentType.define_attribute(
                    node.id.id, self.context.get_type("object")
                )
            except:
                self.errors.append(
                    SemanticError(
                        f"El atributo {node.id.id} ya esta definido. --> row:{node.location[0]}, col:{node.location[1]}"
                    )
                )

    @visitor.when(FunctionDefinitionNode)
    def visit(self, node: FunctionDefinitionNode):
        try:
            type_annotation: TypeNode = node.type_annotation
            return_type = self.context.get_type(type_annotation.type)
        except:
            self.errors.append(
                SemanticError(
                    f"El tipo de retorno {node.type_annotation.type} no esta definido. --> row:{node.type_annotation.location[0]}, col:{node.type_annotation.location[1]}"
                )
            )
            return_type = self.context.get_type("object")

        arg_names: List[IdentifierNode] = [
            list(parama.items())[0] for parama in node.parameters
        ]
        arg_names = [name[0].id for name in arg_names]

        arg_types = []
        aux = [list(parama.items())[0] for parama in node.parameters]
        for parama in aux:
            try:
                arg_types.append(self.context.get_type(parama[1].type))
            except:
                self.errors.append(
                    SemanticError(
                        f"El tipo del parametro {parama[0].id} que se le pasa a la funcion {node.id.id} no esta definido. --> row:{parama[1].location[0]}, col:{parama[1].location[1]} "
                    )
                )
                arg_types.append(self.context.get_type("object"))

        if self.currentType:
            try:
                self.currentType.define_method(
                    node.id.id, arg_names, arg_types, return_type
                )
            except:
                self.errors.append(
                    SemanticError(
                        f"La funcion {node.id.id} ya existe en el contexto de {self.currentType.name}. --> row:{node.location[0]}, col:{node.location[1]}"
                    )
                )

    @visitor.when(CollectionNode)
    def visit(self, node: CollectionNode):
        for item in node.collection:
            self.visit(item)
