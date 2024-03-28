from AST.Nodes import*
from Semantic_Check.Semantic import*
import Semantic_Check.Visitor as visitor

# Pasemos ahora a construir los tipos.
# Nótese que al haber recolectado ya todos los tipos, se logra que
# los parámetros, valores de retorno, y otras refencias a tipos,
# puedan ser resueltas en este recorrido sin problemas.            
class TypeBuilder:
    def __init__(self, context, errors=[]):
        self.context = context
        self.current_type = None
        self.errors = errors
    
    @visitor.on('node')
    def visit(self, node):
        pass
    
    @visitor.when(ProgramNode)
    def visit(self,node):
        for dec in node.declarations:
            self.visit(dec)
        return
    
    # @visitor.when(ClassDeclarationNode)
    # def visit(self,node):
    #     try:
    #         self.current_type = self.context.get_type(node.id)
    #         if node.parent is not None:
    #             self.current_type.set_parent(self.context.get_type(node.parent))
                   
    #     except SemanticError as se:
    #         self.errors.append(se.text)
        
    #     for feat in node.features:
    #         self.visit(feat)
    #     return
    
    # @visitor.when(AttrDeclarationNode)
    # def visit(self,node):
    #     try:
    #         attrType = self.context.get_type(node.type)
    #         self.current_type.define_attribute(node.id,attrType)
    #     except SemanticError as se:
    #         self.errors.append(se.text)
    #     return

    @visitor.when(FuncDeclarationNode)
    def visit(self,node):
        try:
            returnType = self.context.get_type(node.type)
            param_names = []
            param_types = []
            for param in node.params:
                param_names.append(param[0])
                param_types.append(self.context.get_type(param[1]))
            self.current_type.define_method(node.id,param_names,param_types,returnType)
        except SemanticError as se:
            self.errors.append(se.text)
        return
