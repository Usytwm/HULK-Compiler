from AST.Nodes import*
from Semantic_Check.Semantic import*
import Semantic_Check.Visitor as visitor

WRONG_SIGNATURE = 'Method "%s" already defined in "%s" with a different signature.'
SELF_IS_READONLY = 'Variable "self" is read-only.'
LOCAL_ALREADY_DEFINED = 'Variable "%s" is already defined in method "%s".'
INCOMPATIBLE_TYPES = 'Cannot convert "%s" into "%s".'
VARIABLE_NOT_DEFINED = 'Variable "%s" is not defined in "%s".'
INVALID_OPERATION = 'Operation is not defined between "%s" and "%s".'

class TypeChecker:
    
    def __init__(self, context, errors=[]):
        self.context = context
        self.current_type = None
        self.current_method = None
        self.errors = errors

    @visitor.on('node')
    def visit(self, node, scope):
        pass
    
    @visitor.when(ProgramNode)
    def visit(self, node, scope=None):
        scope = node.scope
        ans = []
        for i,st in enumerate( node.declarations):
            self.visit(st,scope)
            if len(self.errors)>0: return self.errors,ans
            if isinstance(st, DeclarationNode) and (isinstance(st,IfElseExprNode) or isinstance(st,IfExprNode)):
                self.errors.append(f' IF expresion can be used only within a function  \n ');
                return self.errors,ans
            if isinstance(st, DeclarationNode) and isinstance(st,ReturnNode)  :
                self.errors.append(f' return can be used only within a function  \n ');
                return self.errors,ans
            if isinstance(st, DeclarationNode) and  isinstance(st,ForNode)  :
                self.errors.append(f' For expresion can be used only within a function  \n ');
                return self.errors,ans
            ans = node.run(i,self.errors,ans)
            
        return self.errors,ans
    
    @visitor.when(VarDeclarationNode)
    def visit(self, node, scope):
        try:
            type_var = self.context.get_type(node.type)
            type_exp = self.visit(node.expr,scope)
            if type_var is not type_exp and type_exp is not None:
                self.errors.append(INCOMPATIBLE_TYPES % (node.type,type_exp.name))
                return None
            else:
                if scope.is_var_defined(node.idx):
                    self.errors.append(LOCAL_ALREADY_DEFINED %(node.idx,"scope"))
                    return None
                elif scope.parent is not None:
                    scope.def_var(node.idx," ",type_var)
            return type_var
        except SemanticError as se:
            self.errors.append(se.text)
            return
    
    @visitor.when(GetNode)
    def visit(self, node, scope):
        if not scope.is_var_defined(node.var):  # Si la variable no esta definida
            self.errors.append(f'The variable {node.var} does not exists ')
            return None
        elif not hasattr(scope.get_local_variable_info(node.var),node.attr):      #Verifica si la variable contiene ese atributo o propiedad
            self.errors.append(f' The variable {node.attr} does not contain the attribute {node.attr} ') # Si la variable no contiene esa propiedad
            return None
        try:
            var = scope.get_local_variable_info(node.var)
            type_ = type(getattr(var,node.attr)).__name__
            return self.context.get_type(type_)
        except SemanticError as se:
            self.errors.append(se.text)
            return
    
    @visitor.when(SetNode)
    def visit(self, node, scope):
        if not scope.is_var_defined(node.var):  # Si la variable no esta definida
            self.errors.append(f'The variable {node.var} does not exists ')
            return None
        elif not hasattr(scope.get_local_variable_info(node.var),node.attr):      #Verifica si la variable contiene ese atributo o propiedad
            self.errors.append(f' The variable {node.attr} does not contain the attribute {node.attr} ') # Si la variable no contiene esa propiedad
            return None 
        try:
            var = scope.get_local_variable_info(node.var) #dame la variable
            type_exp = self.visit(node.exp,scope)
            if isinstance(type_exp,str):
                type_exp=  self.context.get_type(type_exp)
            if node.attr == "age":
                var_type = self.context.get_type("int")
            else:
                var_type = self.context.get_type("str")
        
            if type_exp is not None and type_exp is not var_type:
                self.errors.append(INCOMPATIBLE_TYPES % (var_type.name,type_exp))
                return None 
            return self.context.get_type('void')
        except SemanticError as se:
            self.errors.append(se.text)
            return
    
    @visitor.when(AddRemoveNode)
    def visit(self, node, context):
        if not context.is_var_defined(node.name_patient):
            self.errors.append(f'Patient {node.name_patient} does not exists ')
            return None
        if node.func != "add" and node.func != "remove":
            self.errors.append(f'Patient {node.name_patient} does not contain a {node.func} ')
            return None
        return self.context.get_type('void')
              
    @visitor.when(FuncDeclarationNode)
    def visit(self, node, scope):
        if scope.parent is not None:
            self.errors.append(f'Unable to define one function within another')
            return None
        if scope.check_func_defined(node.idx,len(node.params)):
            self.errors.append(f'The feature {node.idx} alredy exists')
            return None
        else: scope.def_function(node)
        try:
            returnType = self.context.get_type(node.type)
            param_names = []
            param_types = []
            for param in node.params:
                param_names.append(param[0])
                param_types.append(self.context.get_type(param[1]))
            
            # self.current_type.define_method(node.idx,param_names,param_types,returnType)
            # self.current_method = self.current_type.get_method(node.idx)
            #innerScope = scope.create_child_scope()
            # for name,typex in zip(self.current_method.param_names, self.current_method.param_types):
            #     innerScope.def_var(name," ",typex)
            innerScope = scope.create_child_context()
            for i,name in enumerate(param_names):
                innerScope.def_var(name," ",param_types[i])
            for i, exp in enumerate( node.stat_list):
                type_exp = self.visit(exp,innerScope)
                if isinstance(type_exp,str):
                    type_exp = self.context.get_type(type_exp)
                if isinstance(exp,ReturnNode) and i <= len(node.stat_list)-1 :
                    break
                if isinstance(exp,ReturnNode) and returnType.name is VoidType().name  :
                    self.errors.append(INCOMPATIBLE_TYPES % (returnType.name,type_exp.name))
                    return None
                 
            if type_exp is not None and returnType.name is not VoidType().name and type_exp is not returnType:
                self.errors.append(INCOMPATIBLE_TYPES % (returnType.name,type_exp.name))
                return None
            scope.remove_child_context(innerScope)
        except SemanticError as se:
            self.errors.append(se.text)
        return
    
    @visitor.when(CallNode) #Verifica que el tipo de los parametros resividos sea el correcto
    def visit(self, node, scope):        
        if not scope.check_func_defined(node.idx,len(node.args)):
            self.errors.append(f'The feature {node.idx} does not exist with {len(node.args)} arguments')
            return None
        try:
            #if node.obj is None:
            #    meth = self.current_type.get_method(node.id)
            #else:
                #typex = self.context.get_type(node.obj.lex)
                #meth = typex.get_method(node.id)
            func = scope.get_function_info(node.idx,len(node.args))
            #typescall = []
            for i,arg in enumerate(node.args):
                typecall = self.visit(arg,scope)
                typemeth = self.context.get_type(func.params[i][1])
                if typecall is not typemeth:
                    self.errors.append(INCOMPATIBLE_TYPES % (typecall.name,typemeth.name))
                    return None
            
            return func.type
        except SemanticError as se:
            self.errors.append(se.text)
            return

    
    @visitor.when(ReturnNode)
    def visit(self, node, scope):
        return self.visit(node.expr,scope)
        # try:
        #     type = self.visit(node.expr,scope)
        #     return type
        # except SemanticError as se:
        #     self.errors.append(se.text)
        #     return

    @visitor.when(PrintNode)
    def visit(self, node, scope):
        self.visit(node.expr,scope)
        #print = self.visit(node.expr,scope)
        # if print is not None:
        #     return self.context.get_type('void')
        # return print
        # try: self.visit(node.expr,scope)
        # except SemanticError as se:
        #     self.errors.append(se.text)
        #     return

    @visitor.when(PatientNode)
    def visit(self,node,scope):
        if scope.is_var_defined(node.name):
            self.errors.append(f'The variable {node.name} exists')
            return None
        return
    
            
    # @visitor.when(RedefVarDeclarationNode)
    # def visit(self, node, scope):
    #     try:
    #         var = scope.find_variable(node.id)
    #         if var is None:
    #             self.errors.append(VARIABLE_NOT_DEFINED % (node.id,self.current_type.name))
    #             return None
    #         type_exp = self.visit(node.expr,scope)
    #         if var.type is not type_exp and type_exp is not None:
    #             self.errors.append(INCOMPATIBLE_TYPES % (type_exp.name,var.type.name))
    #             return None
    #         else: return var.type
    #     except SemanticError as se:
    #         self.errors.append(se.text)
    #         return

    @visitor.when(RedefVarDeclarationNode)
    def visit(self, node, scope):
        if not scope.is_var_defined(node.idx):
            self.errors.append(f'The variable {node.idx} does not exist')
            return None
        try:    
            type_exp = self.visit(node.expr,scope)
            if not isinstance(type_exp,Type) :type_exp = self.context.get_type(type_exp)
            var_type = scope.get_type_variable(node.idx)
            if not isinstance(var_type,Type) :var_type = self.context.get_type(var_type)
            if type_exp is not var_type:
                self.errors.append(INCOMPATIBLE_TYPES%(var_type.name,type_exp.name))
                return None
        except SemanticError as se:
            self.errors.append(se.text)
            return
    
    @visitor.when(ForNode)
    def visit(self, node, scope):
        if node.idx != node.idx_counter:
            self.errors.append(f'The id {node.idx} must be equal to {node.idx_counter}')
            return None
        if node.counter_one != node.counter_two:
            self.errors.append(f'The id {node.counter_one} must be equal to {node.counter_two}')
            return None
        child = scope.create_child_context()
        type_ = scope.get_type_variable(node.idx)
        if isinstance(type_,str): type_ = self.context.get_type(type_) 
        if type_ is not None and type_.name is not IntType().name:
            self.errors.append(f'The id {node.idx} must be equal to "int" ')
            
        child.def_var(node.idx,node.idx_value,type_)
        for i in node.body:
            self.visit(i,child)
        scope.remove_child_context(child)
        
    @visitor.when(IfExprNode)
    def visit(self, node, scope):
        type_exp = self.visit(node.expr,scope)
        _type = self.context.get_type("bool")
        if type_exp is not _type:
            self.errors.append(INCOMPATIBLE_TYPES % (_type.name,type_exp.name))
            return None
        for i in node.body:
            self.visit(i,scope)
        return    
    
    @visitor.when(IfElseExprNode)
    def visit(self, node, scope):
        type_exp = self.visit(node.eva_expr,scope)
        _type = self.context.get_type("bool")
        if type_exp is not _type:
            self.errors.append(INCOMPATIBLE_TYPES % (_type.name,type_exp.name))
            return None
        for i in node.one_body:
            self.visit(i,scope)
        for i in node.two_body:
            self.visit(i,scope)
        
        
    @visitor.when(VariableNode)
    def visit(self, node, scope):
        if not scope.is_var_defined(node.idx):
            self.errors.append(VARIABLE_NOT_DEFINED % (node.idx,"scope"))
            return None
        else:
            type = scope.get_type_variable(node.idx)
            if type is not str:
                return type
            else: 
                var_type = self.context.get_type(type)
                return var_type
            
    
    @visitor.when(BinaryNode)
    def visit(self, node, scope):
        try:
            typeLeft = self.visit(node.left,scope)
            if isinstance(typeLeft,str):typeLeft = self.context.get_type(typeLeft)
            typeRight = self.visit(node.right,scope)
            if isinstance(typeRight,str):typeRight = self.context.get_type(typeRight)
            if typeLeft.name != 'int' or typeRight.name != 'int':
                self.errors.append(INVALID_OPERATION %(typeLeft.name,typeRight.name))
                return None
            return self.context.get_type('int')
        except SemanticError as se:
            self.errors.append(se.text)
            return
    
    @visitor.when(LeqNode)
    def visit(self, node, scope):
        try:
            typeLeft = self.visit(node.left,scope)
            typeRight = self.visit(node.right,scope)
            if typeLeft.name != 'int' or typeRight.name != 'int':
                self.errors.append(INVALID_OPERATION %(typeLeft.name,typeRight.name))
                return None
            if(typeLeft is not None and typeRight is not None):
                return self.context.get_type('bool')
            else: return None
        except SemanticError as se:
            self.errors.append(se.text)
            return
            
    @visitor.when(EqualNode)
    def visit(self, node, scope):
        try:
            type_left = self.visit(node.left,scope)
            type_right = self.visit(node.right,scope)
            if(type_left is not None and type_right is not None):
                return self.context.get_type('bool')
            else: return None
        except SemanticError as se:
            self.errors.append(se.text)
            return
    
    @visitor.when(GeqNode)
    def visit(self, node, scope):
        try:
            typeLeft = self.visit(node.left,scope)
            typeRight = self.visit(node.right,scope)
            if typeLeft.name != 'int' or typeRight.name != 'int':
                self.errors.append(INVALID_OPERATION %(typeLeft.name,typeRight.name))
                return None
            if(typeLeft is not None and typeRight is not None):
                return self.context.get_type('bool')
            else: return None
        except SemanticError as se:
            self.errors.append(se.text)
            return
        
    @visitor.when(NotNode)
    def visit(self, node, scope):
        try:
            typeLeft =self.visit(node.left,scope)
            typeRight=self.visit(node.right,scope)
            if(typeLeft is not None and typeRight is not None):
                return self.context.get_type('bool')
            else: return None
        except SemanticError as se:
            self.errors.append(se.text)
            return
        
    @visitor.when(LessNode)
    def visit(self, node, scope):
        try:
            typeLeft = self.visit(node.left,scope)
            typeRight = self.visit(node.right,scope)
            if typeLeft.name != 'int' or typeRight.name != 'int':
                self.errors.append(INVALID_OPERATION %(typeLeft.name,typeRight.name))
                return None
            if(typeLeft is not None and typeRight is not None):
                return self.context.get_type('bool')
            else: return None            
        except SemanticError as se:
            self.errors.append(se.text)
            return
        
    @visitor.when(GreaterNode)
    def visit(self, node, scope):
        try:
            typeLeft = self.visit(node.left,scope)
            typeRight = self.visit(node.right,scope)
            if typeLeft.name != 'int' or typeRight.name != 'int':
                self.errors.append(INVALID_OPERATION %(typeLeft.name,typeRight.name))
                return None
            if(typeLeft is not None and typeRight is not None):
                return self.context.get_type('bool')
            else: return None
        except SemanticError as se:
            self.errors.append(se.text)
            return
        
    @visitor.when(FindNode)
    def visit(self,node,scope):
        if not scope.is_var_defined(node.patient):
            self.errors.append(f'The variable {node.patient} does not exist')
            return None
        elif not isinstance( scope.get_local_variable_info(node.patient), Patient):
                self.errors.append(f'The type of {node.patient} does not correct')
                return None    
        return self.context.get_type('bool')
    
    @visitor.when(CancerNode)
    def visit(self,node,scope):
        if not scope.is_var_defined(node.patient):
            self.errors.append(f'The variable {node.patient} does not exist')
            return None
        elif not isinstance( scope.get_local_variable_info(node.patient), Patient):
                self.errors.append(f'The type of {node.patient} does not correct')
                return None
        if node.cancer != "BreastCancer" and node.cancer != "OvarianCancer" and node.cancer != "PancreaticCancer":
            self.errors.append(f'{node.cancer} no existe')
            return None  
        return self.context.get_type('bool')

    
        
    @visitor.when(ConstantNumNode)
    def visit(self, node, scope):
        return self.context.get_type('int')
    
    @visitor.when(ConstantStrNode)
    def visit(self, node, scope):
        return self.context.get_type('str')

    
    @visitor.when(ConstantBoolNode)
    def visit(self, node, scope):
        return self.context.get_type('bool')
   