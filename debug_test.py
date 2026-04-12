"""
Standalone debug test for static_checker_1 with AssignStmt
"""
import sys
from typing import Dict, List, Set, Optional, Any, Tuple, Union

# Minimal node stubs needed
class ASTNode:
    def accept(self, visitor, o=None):
        # Convert PascalCase class name to snake_case method name
        name = self.__class__.__name__
        # e.g., StructDecl -> visit_struct_decl, MemberAccess -> visit_member_access
        parts = []
        for i, c in enumerate(name):
            if i > 0 and c.isupper():
                parts.append('_')
            parts.append(c.lower())
        method_name = 'visit_' + ''.join(parts)
        method = getattr(visitor, method_name)
        return method(self, o)

class IntType(ASTNode): pass
class FloatType(ASTNode): pass
class StringType(ASTNode): pass
class VoidType(ASTNode): pass
class StructType(ASTNode):
    def __init__(self, n): self.struct_name = n
class Identifier(ASTNode):
    def __init__(self, n): self.name = n
class IntLiteral(ASTNode):
    def __init__(self, v): self.value = v
class MemberAccess(ASTNode):
    def __init__(self, obj, m): self.obj = obj; self.member = m
class AssignExpr(ASTNode):
    def __init__(self, lhs, rhs): self.lhs = lhs; self.rhs = rhs
class BlockStmt(ASTNode):
    def __init__(self, stmts): self.statements = stmts
class VarDecl(ASTNode):
    def __init__(self, vt, n, iv=None): self.var_type = vt; self.name = n; self.init_value = iv
class FuncDecl(ASTNode):
    def __init__(self, rt, n, ps, b): self.return_type=rt; self.name=n; self.params=ps; self.body=b
class MemberDecl(ASTNode):
    def __init__(self, t, n): self.member_type=t; self.name=n
class StructDecl(ASTNode):
    def __init__(self, n, ms): self.name=n; self.members=ms
class Program(ASTNode):
    def __init__(self, ds): self.decls=ds
class AssignStmt(ASTNode):
    def __init__(self, expr): self.expr = expr

TyCType = Union[IntType, FloatType, StringType, VoidType, StructType]

class UnresolvedAuto:
    def __init__(self, name): self.name = name
    def __repr__(self): return f"UnresolvedAuto({self.name})"

class Redeclared(Exception):
    def __init__(self, k, n): super().__init__(f"Redeclared({k}, {n})")
class UndeclaredIdentifier(Exception):
    def __init__(self, n): super().__init__(f"UndeclaredIdentifier({n})")
class UndeclaredFunction(Exception):
    def __init__(self, n): super().__init__(f"UndeclaredFunction({n})")
class UndeclaredStruct(Exception):
    def __init__(self, n): super().__init__(f"UndeclaredStruct({n})")
class TypeCannotBeInferred(Exception):
    def __init__(self, ctx): super().__init__(f"TypeCannotBeInferred({ctx})")
class TypeMismatchInStatement(Exception):
    def __init__(self, s): super().__init__(f"TypeMismatchInStatement({s})")
class TypeMismatchInExpression(Exception):
    def __init__(self, e): super().__init__(f"TypeMismatchInExpression({e})")
class MustInLoop(Exception):
    def __init__(self, s): super().__init__(f"MustInLoop({s})")

BUILTIN_FUNCTIONS = {
    "readInt": ((), "int"),
    "readFloat": ((), "float"),
    "readString": ((), "string"),
    "printInt": (("int",), None),
    "printFloat": (("float",), None),
    "printString": (("string",), None),
}

class StaticChecker:
    def __init__(self):
        self.structs: Dict[str, StructDecl] = {}
        self.functions: Dict[str, FuncDecl] = {}
        self._member_struct_types: List[StructType] = []
        self._func_struct_types: List[StructType] = []
        self.param_types: Dict[str, TyCType] = {}
        self.local_scopes: List[Dict[str, TyCType]] = []
        self.auto_vars: Dict[str, VarDecl] = {}
        self.loop_depth: int = 0
        self.inferred_return_type = None
        self.func_return_is_auto = False
        self._in_switch = False

    def check_program(self, ast: Program) -> None:
        for decl in ast.decls:
            if isinstance(decl, StructDecl):
                self.structs[decl.name] = decl
            elif isinstance(decl, FuncDecl):
                self.functions[decl.name] = decl
        for decl in ast.decls:
            self.visit(decl)

    @staticmethod
    def types_compatible(a, b) -> bool:
        if type(a) != type(b): return False
        if isinstance(a, StructType) and isinstance(b, StructType):
            return a.struct_name == b.struct_name
        return True

    def visit(self, node, o=None):
        return node.accept(self, o)

    def _lookup_var(self, name):
        for scope in reversed(self.local_scopes):
            if name in scope: return scope[name]
        return self.param_types.get(name)

    def _resolve_type_node(self, type_node):
        if isinstance(type_node, StructType):
            if type_node.struct_name not in self.structs:
                raise UndeclaredStruct(type_node.struct_name)
        return type_node

    def _is_lvalue(self, expr):
        return isinstance(expr, (Identifier, MemberAccess))

    def _resolve_auto_var(self, expr, inferred_type):
        if isinstance(expr, Identifier) and expr.name in self.auto_vars:
            self.auto_vars.pop(expr.name)
            for scope in reversed(self.local_scopes):
                if expr.name in scope:
                    scope[expr.name] = inferred_type
                    break
            else:
                if expr.name in self.param_types:
                    self.param_types[expr.name] = inferred_type

    def _type_from_name(self, name):
        if name == "int": return IntType()
        if name == "float": return FloatType()
        if name == "string": return StringType()
        if name == "void": return VoidType()
        return IntType()

    def _matches_simple_type(self, actual, expected_name):
        if expected_name == "int": return isinstance(actual, IntType)
        if expected_name == "float": return isinstance(actual, FloatType)
        if expected_name == "string": return isinstance(actual, StringType)
        return False

    def visit_struct_decl(self, node):
        for m in node.members:
            if isinstance(m.member_type, StructType):
                self._member_struct_types.append(m.member_type)
    def visit_struct_type(self, node, o=None): return node
    def visit_member_decl(self, node, o=None): pass

    def visit_func_decl(self, node):
        self.param_types.clear()
        self.local_scopes.clear()
        self.local_scopes.append({})
        self.auto_vars.clear()
        self._func_struct_types.clear()
        self.loop_depth = 0
        self.inferred_return_type = None
        self.func_return_is_auto = node.return_type is None
        for p in node.params:
            ptype = self._resolve_type_node(p.param_type) if hasattr(p, 'param_type') else IntType()
            self.param_types[p.name] = ptype
        self.visit(node.body)
        for name, vdecl in list(self.auto_vars.items()):
            raise TypeCannotBeInferred(vdecl)

    def visit_block_stmt(self, node):
        self.local_scopes.append({})
        try:
            for s in node.statements:
                self.visit(s)
        finally:
            self.local_scopes.pop()

    def visit_var_decl(self, node):
        scope = self.local_scopes[-1]
        if node.var_type is None:
            if node.init_value:
                rhs = self.visit(node.init_value)
                scope[node.name] = rhs
            else:
                scope[node.name] = None
                self.auto_vars[node.name] = node
        else:
            vtype = self._resolve_type_node(node.var_type)
            scope[node.name] = vtype

    def visit_assign_stmt(self, node, o=None):
        _SENTINEL = object()
        _MISSING = object()
        expr_val = getattr(node, 'expr', _SENTINEL)
        if expr_val is not _SENTINEL:
            ae_lhs = getattr(expr_val, 'lhs', _MISSING)
            if ae_lhs is _MISSING:
                ae_lhs = getattr(node, 'lhs', _MISSING)
                ae_rhs = getattr(node, 'rhs', _MISSING)
            else:
                ae_rhs = getattr(expr_val, 'rhs', _MISSING)
        else:
            ae_lhs = getattr(node, 'lhs', _MISSING)
            ae_rhs = getattr(node, 'rhs', _MISSING)

        if ae_lhs is _MISSING or ae_rhs is _MISSING:
            raise TypeMismatchInStatement(node)

        print(f"DEBUG: ae_lhs={type(ae_lhs).__name__}({ae_lhs}), ae_rhs={type(ae_rhs).__name__}({ae_rhs})")

        if not self._is_lvalue(ae_lhs):
            raise TypeMismatchInStatement(node)

        rhs_type = self.visit(ae_rhs)
        lhs_type = self.visit(ae_lhs)
        print(f"DEBUG: lhs_type={type(lhs_type).__name__}({lhs_type}), rhs_type={type(rhs_type).__name__}({rhs_type})")

        if lhs_type is None or rhs_type is None:
            raise TypeMismatchInStatement(node)
        lhs_unresolved = isinstance(lhs_type, UnresolvedAuto)
        rhs_unresolved = isinstance(rhs_type, UnresolvedAuto)
        if lhs_unresolved and rhs_unresolved:
            raise TypeCannotBeInferred(ae_lhs)
        if lhs_unresolved:
            self._resolve_auto_var(ae_lhs, rhs_type)
            lhs_type = rhs_type
        elif rhs_unresolved:
            raise TypeCannotBeInferred(ae_rhs)
        if not self.types_compatible(lhs_type, rhs_type):
            raise TypeMismatchInStatement(node)

    def visit_identifier(self, node, o=None):
        if node.name in self.auto_vars:
            return UnresolvedAuto(node.name)
        vtype = self._lookup_var(node.name)
        if vtype is None:
            raise UndeclaredIdentifier(node.name)
        return vtype

    def visit_member_access(self, node, o=None):
        obj_type = self.visit(node.obj)
        if not isinstance(obj_type, StructType):
            raise TypeMismatchInExpression(node)
        decl = self.structs.get(obj_type.struct_name)
        if decl is None:
            raise UndeclaredStruct(obj_type.struct_name)
        for m in decl.members:
            if m.name == node.member:
                return self._resolve_type_node(m.member_type)
        raise TypeMismatchInExpression(node)

    def visit_int_literal(self, node, o=None): return IntType()
    def visit_int_type(self, node, o=None): return IntType()
    def visit_void_type(self, node, o=None): return VoidType()
    def visit_struct_type(self, node, o=None): return node
    def visit_return_stmt(self, node, o=None): pass
    def visit_break_stmt(self, node, o=None):
        if self.loop_depth == 0 and not getattr(self, '_in_switch', False):
            raise MustInLoop(node)
    def visit_continue_stmt(self, node, o=None):
        if self.loop_depth == 0: raise MustInLoop(node)
    def visit_binary_op(self, node, o=None): return IntType()
    def visit_prefix_op(self, node, o=None): return IntType()
    def visit_postfix_op(self, node, o=None): return IntType()
    def visit_assign_expr(self, node, o=None): return IntType()
    def visit_func_call(self, node, o=None): return IntType()
    def visit_expr_stmt(self, node, o=None): self.visit(node.expr)


# Build the AST exactly as the grader shows
ast = Program([
    StructDecl('Point', [
        MemberDecl(IntType(), 'x'),
        MemberDecl(IntType(), 'y'),
    ]),
    FuncDecl(
        VoidType(), 'main', [],
        BlockStmt([
            VarDecl(StructType('Point'), 'p'),
            AssignStmt(AssignExpr(MemberAccess(Identifier('p'), 'x'), IntLiteral(10))),
            AssignStmt(AssignExpr(MemberAccess(Identifier('p'), 'y'), IntLiteral(20))),
        ])
    )
])

checker = StaticChecker()
try:
    checker.check_program(ast)
    print('Result: successful')
except Exception as e:
    print(f'Result: {type(e).__name__}({e})')
