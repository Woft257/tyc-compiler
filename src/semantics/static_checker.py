"""
Static Semantic Checker for TyC Programming Language

This module implements a comprehensive static semantic checker using visitor pattern
for the TyC procedural programming language. It performs type checking,
scope management, type inference, and detects all semantic errors as
specified in the TyC language specification.
"""

from functools import reduce
from typing import (
    Dict,
    List,
    Set,
    Optional,
    Any,
    Tuple,
    NamedTuple,
    Union,
    TYPE_CHECKING,
)
from ..utils.visitor import ASTVisitor
from ..utils.nodes import (
    ASTNode,
    Program,
    StructDecl,
    MemberDecl,
    FuncDecl,
    Param,
    VarDecl,
    IfStmt,
    WhileStmt,
    ForStmt,
    BreakStmt,
    ContinueStmt,
    ReturnStmt,
    BlockStmt,
    SwitchStmt,
    CaseStmt,
    DefaultStmt,
    Type,
    IntType,
    FloatType,
    StringType,
    VoidType,
    StructType,
    BinaryOp,
    PrefixOp,
    PostfixOp,
    AssignExpr,
    MemberAccess,
    FuncCall,
    Identifier,
    StructLiteral,
    IntLiteral,
    FloatLiteral,
    StringLiteral,
    ExprStmt,
    Expr,
    Stmt,
    Decl,
)

# Type aliases for better type hints
TyCType = Union[IntType, FloatType, StringType, VoidType, StructType]


class UnresolvedAuto:
    """Marker type returned by visit_identifier when the identifier is an
    auto variable whose type has not yet been inferred."""
    def __init__(self, name: str):
        self.name = name
    def __repr__(self):
        return f"UnresolvedAuto({self.name})"
from .static_error import (
    StaticError,
    Redeclared,
    UndeclaredIdentifier,
    UndeclaredFunction,
    UndeclaredStruct,
    TypeCannotBeInferred,
    TypeMismatchInStatement,
    TypeMismatchInExpression,
    MustInLoop,
)


# ============================================================================
# Built-in function signatures
# ============================================================================

BUILTIN_FUNCTIONS: Dict[str, Tuple[Tuple[Tuple[Optional[str], ...], ...], Optional[str]]] = {
    "readInt": ((), "int"),
    "readFloat": ((), "float"),
    "readString": ((), "string"),
    "printInt": (("int",), None),
    "printFloat": (("float",), None),
    "printString": (("string",), None),
}


# ============================================================================
# Symbol records
# ============================================================================

class Symbol:
    """A symbol binding: name -> type."""
    __slots__ = ("name", "sym_type")

    def __init__(self, name: str, sym_type: Optional[TyCType]):
        self.name = name
        self.sym_type = sym_type


# ============================================================================
# StaticChecker
# ============================================================================

class StaticChecker(ASTVisitor):
    """
    Static semantic checker for TyC.

    Two-pass algorithm:
      1. Collect struct and function declarations into the global environment.
         Detect Redeclared errors among structs and among functions.
      2. For each function body, check local declarations, type inference,
         and all expression/statement constraints.
    """

    # ------------------------------------------------------------------ constructor
    def __init__(self):
        # Global environment
        self.structs: Dict[str, StructDecl] = {}   # name -> StructDecl
        self.functions: Dict[str, FuncDecl] = {}   # name -> FuncDecl

        # Ordered lists for forward-reference checking
        self._struct_decl_order: List[str] = []   # struct names in declaration order
        self._func_decl_order: List[str] = []     # function names in declaration order

        self._member_struct_types: List[StructType] = []  # struct types in struct member decls
        self._func_struct_types: List[StructType] = []  # struct types in function bodies

        # Per-function environment (reset on each FuncDecl)
        self.param_types: Dict[str, TyCType] = {}      # param name -> type
        self.local_scopes: List[Dict[str, TyCType]] = []  # block scopes (innermost last)
        self.auto_vars: Dict[str, VarDecl] = {}           # auto var name -> VarDecl (unresolved)

        # Loop context counter (for break/continue validation)
        self.loop_depth: int = 0

        # Inferred return type for the current function (None until first return)
        self.inferred_return_type: Optional[Type] = None

        # Track whether the current function return type is auto (inferred)
        self.func_return_is_auto: bool = False

        # Flag: inside a switch statement (for break validation)
        self._in_switch: bool = False

    # ------------------------------------------------------------------ entry point
    def check_program(self, ast: Program) -> None:
        """Check the program; raises the first semantic error encountered."""
        self._error = False
        self.visit_program(ast)
        # After the first pass through all declarations, check unreferenced auto vars
        # This is handled inside visit_func_decl when the block finishes

    # ------------------------------------------------------------------ type helpers
    @staticmethod
    def _type_name(t: Type) -> str:
        if isinstance(t, IntType):      return "int"
        if isinstance(t, FloatType):   return "float"
        if isinstance(t, StringType):   return "string"
        if isinstance(t, VoidType):     return "void"
        if isinstance(t, StructType):   return t.struct_name
        return "unknown"

    @staticmethod
    def types_compatible(a: Type, b: Type) -> bool:
        """True when a and b are the same concrete type."""
        if type(a) != type(b):
            return False
        if isinstance(a, StructType) and isinstance(b, StructType):
            return a.struct_name == b.struct_name
        return True

    # ------------------------------------------------------------------ lookup helpers
    def _lookup_var(self, name: str) -> Optional[TyCType]:
        """Search local scopes innermost-first, then params."""
        for scope in reversed(self.local_scopes):
            if name in scope:
                return scope[name]
        return self.param_types.get(name)

    def _lookup_param(self, name: str) -> Optional[TyCType]:
        return self.param_types.get(name)

    def _add_var(self, name: str, vtype: Optional[TyCType], block_scope: bool = True) -> None:
        """Add a variable to the innermost block scope."""
        if self.local_scopes:
            self.local_scopes[-1][name] = vtype
        elif block_scope:
            # At top-level of function (no block pushed yet)
            scope = self.local_scopes[-1] if self.local_scopes else {}
            self.local_scopes.append({})

    def _new_block(self) -> None:
        """Push a new block scope."""
        self.local_scopes.append({})

    def _end_block(self) -> Tuple[Dict[str, TyCType], Dict[str, VarDecl]]:
        """Pop the innermost block scope."""
        scope = self.local_scopes.pop() if self.local_scopes else {}
        # NOTE: auto_vars are tracked at function-level and are NOT removed on block exit.
        # An auto var that is still unresolved at the end of the function body
        # will be caught by the final check in visit_func_decl.
        return scope, {}

    # ------------------------------------------------------------------ Program & declarations (pass 1: global collection)
    def visit_program(self, node: "Program") -> None:
        # ---- Pass 1: collect structs and functions, detect Redeclared ----
        for decl in node.decls:
            if isinstance(decl, StructDecl):
                if decl.name in self.structs:
                    raise Redeclared("Struct", decl.name)
                self.structs[decl.name] = decl
                self._struct_decl_order.append(decl.name)
            elif isinstance(decl, FuncDecl):
                if decl.name in self.functions:
                    raise Redeclared("Function", decl.name)
                self.functions[decl.name] = decl
                self._func_decl_order.append(decl.name)

        # ---- Pass 2: check each declaration ----
        for decl in node.decls:
            self.visit(decl)

        # ---- Pass 3: validate struct types used in function bodies ----
        # Deferred: struct type references in function bodies
        for stype in self._func_struct_types:
            if stype.struct_name not in self.structs:
                raise UndeclaredStruct(stype.struct_name)

        # ---- Pass 4: validate struct types used in struct member declarations ----
        # Struct member types can have forward references; check after all structs exist.
        for stype in self._member_struct_types:
            if stype.struct_name not in self.structs:
                raise UndeclaredStruct(stype.struct_name)

    def visit_struct_decl(self, node: "StructDecl", o: Any = None) -> None:
        # Check duplicate member names
        seen_members: Set[str] = set()
        for member in node.members:
            if member.name in seen_members:
                raise Redeclared("Member", member.name)
            seen_members.add(member.name)
            # Struct members cannot use undeclared struct types
            self.visit(member)

    def visit_member_decl(self, node: "MemberDecl", o: Any = None) -> None:
        if isinstance(node.member_type, StructType):
            self._member_struct_types.append(node.member_type)

    def visit_func_decl(self, node: "FuncDecl", o: Any = None) -> None:
        # ---- Reset per-function environment ----
        self.param_types.clear()
        self.local_scopes.clear()
        self.local_scopes.append({})   # function-level scope
        self.auto_vars.clear()
        self._func_struct_types.clear()
        self.loop_depth = 0
        self.inferred_return_type = None

        # Determine if return type is auto (None == auto)
        self.func_return_is_auto = node.return_type is None

        # Register parameters (check RedeclaredParameter)
        param_names: Set[str] = set()
        for p in node.params:
            if p.name in param_names:
                raise Redeclared("Parameter", p.name)
            param_names.add(p.name)
            ptype = self._resolve_type_node(p.param_type)
            self.param_types[p.name] = ptype

        # Check body
        self.visit(node.body)

        # After body: validate return type consistency
        # 1. Unresolved auto vars that were never assigned -> error
        for name, vdecl in list(self.auto_vars.items()):
            raise TypeCannotBeInferred(vdecl)

        # 2. Explicit return type must match inferred type from return statements
        if node.return_type is not None:
            # Explicit return type
            explicit_type = self._resolve_type_node(node.return_type)
            if self.inferred_return_type is None:
                # No return statements returned a value; only void returns
                pass  # void return is fine
            elif not self.types_compatible(explicit_type, self.inferred_return_type):
                raise TypeMismatchInStatement(node.body)

    def visit_param(self, node: "Param") -> None:
        self.visit(node.param_type)

    # ------------------------------------------------------------------ Type visitors
    def visit_int_type(self, node: "IntType", o: Any = None) -> IntType:
        return IntType()

    def visit_float_type(self, node: "FloatType", o: Any = None) -> FloatType:
        return FloatType()

    def visit_string_type(self, node: "StringType", o: Any = None) -> StringType:
        return StringType()

    def visit_void_type(self, node: "VoidType", o: Any = None) -> VoidType:
        return VoidType()

    def visit_struct_type(self, node: "StructType", o: Any = None) -> StructType:
        # Struct members can have forward references (handled via _member_struct_types).
        # For all other uses (function params, variable decls, member access), validate now.
        if o == "struct_member":
            return node
        # Track for deferred validation (allows forward references)
        self._func_struct_types.append(node)
        return node

    # ------------------------------------------------------------------ Block & statements
    def visit_block_stmt(self, node: "BlockStmt", o: Any = None) -> None:
        self._new_block()
        try:
            for stmt in node.statements:
                self.visit(stmt)
        finally:
            self._end_block()
        # After visiting all statements in the block: check for unresolved auto vars
        # that were never assigned a value within this block.
        # NOTE: These are already tracked in self.auto_vars by visit_var_decl.
        # The final check happens in visit_func_decl after the entire function body.

    def visit_var_decl(self, node: "VarDecl", o: Any = None) -> None:
        scope = self.local_scopes[-1]

        # RedeclaredVariable check: same block
        if node.name in scope:
            raise Redeclared("Variable", node.name)

        # RedeclaredVariable: local var cannot shadow a parameter
        if node.name in self.param_types:
            raise Redeclared("Variable", node.name)

        if node.var_type is None:
            # ---- auto declaration ----
            if node.init_value is not None:
                # Infer from initializer
                rhs_type = self.visit(node.init_value)
                if rhs_type is None:
                    raise TypeCannotBeInferred(node)
                scope[node.name] = rhs_type
            else:
                # No initializer: track for later inference
                scope[node.name] = None   # temporary
                self.auto_vars[node.name] = node
        else:
            # ---- explicit type ----
            vtype = self._resolve_type_node(node.var_type)
            scope[node.name] = vtype
            if node.init_value is not None:
                rhs_type = self.visit(node.init_value)
                if not self.types_compatible(vtype, rhs_type):
                    raise TypeMismatchInStatement(node)

    def visit_if_stmt(self, node: "IfStmt", o: Any = None) -> None:
        cond_type = self.visit(node.condition)
        if isinstance(cond_type, UnresolvedAuto):
            # Auto var used in int context: infer as int
            inferred = IntType()
            self._resolve_auto_var(node.condition, inferred)
            cond_type = inferred
        if not self.types_compatible(cond_type, IntType()):
            raise TypeMismatchInStatement(node)
        self.visit(node.then_stmt)
        if node.else_stmt:
            self.visit(node.else_stmt)

    def visit_while_stmt(self, node: "WhileStmt", o: Any = None) -> None:
        cond_type = self.visit(node.condition)
        if isinstance(cond_type, UnresolvedAuto):
            inferred = IntType()
            self._resolve_auto_var(node.condition, inferred)
            cond_type = inferred
        if not self.types_compatible(cond_type, IntType()):
            raise TypeMismatchInStatement(node)
        self.loop_depth += 1
        try:
            self.visit(node.body)
        finally:
            self.loop_depth -= 1

    def visit_for_stmt(self, node: "ForStmt", o: Any = None) -> None:
        if node.init:
            self.visit(node.init)
        if node.condition:
            cond_type = self.visit(node.condition)
            if isinstance(cond_type, UnresolvedAuto):
                inferred = IntType()
                self._resolve_auto_var(node.condition, inferred)
                cond_type = inferred
            if not self.types_compatible(cond_type, IntType()):
                raise TypeMismatchInStatement(node)
        if node.update:
            self.visit(node.update)
        self.loop_depth += 1
        try:
            self.visit(node.body)
        finally:
            self.loop_depth -= 1

    def visit_switch_stmt(self, node: "SwitchStmt", o: Any = None) -> None:
        expr_type = self.visit(node.expr)
        if not self.types_compatible(expr_type, IntType()):
            raise TypeMismatchInStatement(node)
        # Break is valid in switch statements (not just loops)
        self._in_switch = True
        try:
            for case in node.cases:
                self.visit(case)
            if node.default_case:
                self.visit(node.default_case)
        finally:
            self._in_switch = False

    def visit_case_stmt(self, node: "CaseStmt", o: Any = None) -> None:
        self.visit(node.expr)
        for stmt in node.statements:
            self.visit(stmt)

    def visit_default_stmt(self, node: "DefaultStmt", o: Any = None) -> None:
        for stmt in node.statements:
            self.visit(stmt)

    def visit_break_stmt(self, node: "BreakStmt", o: Any = None) -> None:
        if self.loop_depth == 0 and not getattr(self, '_in_switch', False):
            raise MustInLoop(node)

    def visit_continue_stmt(self, node: "ContinueStmt", o: Any = None) -> None:
        if self.loop_depth == 0:
            raise MustInLoop(node)

    def visit_return_stmt(self, node: "ReturnStmt", o: Any = None) -> None:
        if node.expr is None:
            ret_type = VoidType()
        else:
            ret_type = self.visit(node.expr)
            if isinstance(ret_type, UnresolvedAuto):
                raise TypeCannotBeInferred(node)

        if self.inferred_return_type is None:
            # First return in this function: record or infer type
            self.inferred_return_type = ret_type
        else:
            # Subsequent return: type must match inferred type
            if not self.types_compatible(self.inferred_return_type, ret_type):
                raise TypeMismatchInStatement(node)

    def visit_expr_stmt(self, node: "ExprStmt", o: Any = None) -> None:
        if isinstance(node.expr, AssignExpr):
            # Assignment as statement: use TypeMismatchInStatement
            ae = node.expr
            if not self._is_lvalue(ae.lhs):
                raise TypeMismatchInStatement(node)

            rhs_type = self.visit(ae.rhs)
            lhs_type = self.visit(ae.lhs)

            lhs_unresolved = isinstance(lhs_type, UnresolvedAuto)
            rhs_unresolved = isinstance(rhs_type, UnresolvedAuto)
            if lhs_unresolved and rhs_unresolved:
                raise TypeCannotBeInferred(ae)
            if lhs_unresolved:
                self._resolve_auto_var(ae.lhs, rhs_type)
                lhs_type = rhs_type
            elif rhs_unresolved:
                raise TypeCannotBeInferred(ae)

            if not self.types_compatible(lhs_type, rhs_type):
                raise TypeMismatchInStatement(node)
        else:
            self.visit(node.expr)

    # ------------------------------------------------------------------ Expressions (return Type)
    def visit_binary_op(self, node: "BinaryOp", o: Any = None) -> TyCType:
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)
        op = node.operator

        left_unresolved = isinstance(left_type, UnresolvedAuto)
        right_unresolved = isinstance(right_type, UnresolvedAuto)

        # If BOTH operands are unresolved autos, type cannot be inferred
        if left_unresolved and right_unresolved:
            raise TypeCannotBeInferred(node)

        # If one operand is unresolved auto, infer from the concrete other operand
        if left_unresolved:
            self._resolve_auto_var_from_unresolved(left_type, right_type)
            left_type = right_type
        if right_unresolved:
            self._resolve_auto_var_from_unresolved(right_type, left_type)
            right_type = left_type

        # Arithmetic +, -, *, /
        if op in ("+", "-", "*", "/"):
            if isinstance(left_type, StringType) and isinstance(right_type, StringType) and op == "+":
                return StringType()
            if not isinstance(left_type, (IntType, FloatType)):
                raise TypeMismatchInExpression(node)
            if not isinstance(right_type, (IntType, FloatType)):
                raise TypeMismatchInExpression(node)
            if isinstance(left_type, FloatType) or isinstance(right_type, FloatType):
                return FloatType()
            return IntType()

        # Modulus %
        elif op == "%":
            if not isinstance(left_type, IntType) or not isinstance(right_type, IntType):
                raise TypeMismatchInExpression(node)
            return IntType()

        # Relational ==, !=, <, <=, >, >=
        elif op in ("==", "!=", "<", "<=", ">", ">="):
            if not isinstance(left_type, (IntType, FloatType)):
                raise TypeMismatchInExpression(node)
            if not isinstance(right_type, (IntType, FloatType)):
                raise TypeMismatchInExpression(node)
            return IntType()

        # Logical &&, ||
        elif op in ("&&", "||"):
            if not isinstance(left_type, IntType) or not isinstance(right_type, IntType):
                raise TypeMismatchInExpression(node)
            return IntType()

        else:
            return IntType()

    def visit_prefix_op(self, node: "PrefixOp", o: Any = None) -> TyCType:
        op = node.operator
        if op in ("++", "--"):
            operand_type = self.visit(node.operand)
            if not self._is_lvalue(node.operand):
                raise TypeMismatchInExpression(node)
            if isinstance(operand_type, UnresolvedAuto):
                return IntType()
            if not isinstance(operand_type, IntType):
                raise TypeMismatchInExpression(node)
            return IntType()
        elif op == "!":
            operand_type = self.visit(node.operand)
            if not isinstance(operand_type, (IntType, UnresolvedAuto)):
                raise TypeMismatchInExpression(node)
            return IntType()
        elif op in ("+", "-"):
            operand_type = self.visit(node.operand)
            if isinstance(operand_type, UnresolvedAuto):
                return IntType()
            if not isinstance(operand_type, (IntType, FloatType)):
                raise TypeMismatchInExpression(node)
            return operand_type
        else:
            return IntType()

    def visit_postfix_op(self, node: "PostfixOp", o: Any = None) -> TyCType:
        operand_type = self.visit(node.operand)
        if not self._is_lvalue(node.operand):
            raise TypeMismatchInExpression(node)
        if isinstance(operand_type, UnresolvedAuto):
            return IntType()
        if not isinstance(operand_type, IntType):
            raise TypeMismatchInExpression(node)
        return IntType()

    def visit_assign_expr(self, node: "AssignExpr", o: Any = None) -> TyCType:
        if not self._is_lvalue(node.lhs):
            raise TypeMismatchInExpression(node)
        rhs_type = self.visit(node.rhs)

        lhs_type = self.visit(node.lhs)
        lhs_unresolved = isinstance(lhs_type, UnresolvedAuto)
        rhs_unresolved = isinstance(rhs_type, UnresolvedAuto)

        if lhs_unresolved and rhs_unresolved:
            raise TypeCannotBeInferred(node)
        if lhs_unresolved:
            # LHS is unresolved auto: infer from RHS
            self._resolve_auto_var(node.lhs, rhs_type)
            lhs_type = rhs_type
        elif rhs_unresolved:
            raise TypeCannotBeInferred(node)

        if not self.types_compatible(lhs_type, rhs_type):
            raise TypeMismatchInExpression(node)

        return lhs_type

    def visit_member_access(self, node: "MemberAccess", o: Any = None) -> TyCType:
        obj_type = self.visit(node.obj)
        if not isinstance(obj_type, StructType):
            raise TypeMismatchInExpression(node)
        struct_decl = self.structs.get(obj_type.struct_name)
        if struct_decl is None:
            raise UndeclaredStruct(obj_type.struct_name)
        # Find member
        for member in struct_decl.members:
            if member.name == node.member:
                return self._resolve_type_node(member.member_type)
        raise TypeMismatchInExpression(node)

    def visit_func_call(self, node: "FuncCall", o: Any = None) -> TyCType:
        func_name = node.name

        # Built-in functions
        if func_name in BUILTIN_FUNCTIONS:
            param_types_expected, return_type_name = BUILTIN_FUNCTIONS[func_name]
            if len(node.args) != len(param_types_expected):
                raise TypeMismatchInExpression(node)
            for arg, expected in zip(node.args, param_types_expected):
                arg_type = self.visit(arg)
                if isinstance(arg_type, UnresolvedAuto):
                    # Auto var being passed to a built-in: infer as the expected type
                    inferred_type = self._type_from_name(expected)
                    self._resolve_auto_var_from_name(arg_type.name, expected)
                elif expected and not self._matches_simple_type(arg_type, expected):
                    raise TypeMismatchInExpression(node)
            if return_type_name == "int":    return IntType()
            if return_type_name == "float":  return FloatType()
            if return_type_name == "string": return StringType()
            if return_type_name is None:     return VoidType()
            return VoidType()

        # User-defined function
        if func_name not in self.functions:
            raise UndeclaredFunction(func_name)
        func_decl = self.functions[func_name]

        # Check forward reference: if function not yet validated, validate it now
        if not hasattr(self, '_checked_funcs'):
            self._checked_funcs: Set[str] = set()
        if func_name not in self._checked_funcs:
            self._checked_funcs.add(func_name)
            old_param_types = dict(self.param_types)
            old_local_scopes = list(self.local_scopes)
            old_auto_vars = dict(self.auto_vars)
            old_loop_depth = self.loop_depth
            old_inferred = self.inferred_return_type
            old_func_auto = self.func_return_is_auto
            old_in_switch = self._in_switch
            # Temporarily check the called function's body
            self._check_func_body(func_decl)
            # Restore current function state
            self.param_types = old_param_types
            self.local_scopes = old_local_scopes
            self.auto_vars = old_auto_vars
            self.loop_depth = old_loop_depth
            self.inferred_return_type = old_inferred
            self.func_return_is_auto = old_func_auto
            self._in_switch = old_in_switch

        if len(node.args) != len(func_decl.params):
            raise TypeMismatchInExpression(node)
        for arg, param in zip(node.args, func_decl.params):
            arg_type = self.visit(arg)
            param_type = self._resolve_type_node(param.param_type)
            if not self.types_compatible(arg_type, param_type):
                raise TypeMismatchInExpression(node)

        if func_decl.return_type is None:
            # auto return
            if self.inferred_return_type is None:
                return IntType()   # placeholder; caller will handle via return inference
            return self.inferred_return_type
        return self._resolve_type_node(func_decl.return_type)

    def visit_identifier(self, node: "Identifier", o: Any = None) -> TyCType:
        # Check if this identifier is an auto variable (may be unresolved).
        # auto_vars tracks all unresolved auto declarations at function level.
        if node.name in self.auto_vars:
            return UnresolvedAuto(node.name)
        # Look up in local scopes (parameters and local variables)
        vtype = self._lookup_var(node.name)
        if vtype is None:
            raise UndeclaredIdentifier(node.name)
        return vtype

    def visit_struct_literal(self, node: "StructLiteral", o: Any = None) -> TyCType:
        for val in node.values:
            self.visit(val)
        return IntType()   # StructLiteral returns a struct; caller should use StructType if available

    # Literals
    def visit_int_literal(self, node: "IntLiteral", o: Any = None) -> IntType:
        return IntType()

    def visit_float_literal(self, node: "FloatLiteral", o: Any = None) -> FloatType:
        return FloatType()

    def visit_string_literal(self, node: "StringLiteral", o: Any = None) -> StringType:
        return StringType()

    # =========================================================================
    # Internal helpers
    # =========================================================================

    def _resolve_type_node(self, type_node: Type) -> TyCType:
        """Visit a type node and return the resolved Type object."""
        if isinstance(type_node, StructType):
            if type_node.struct_name not in self.structs:
                raise UndeclaredStruct(type_node.struct_name)
        return type_node

    def _resolve_type_if_concrete(self, type_node: Type) -> TyCType:
        """Resolve a type node; if struct type not yet declared, just return it."""
        return type_node

    def _is_concrete_type(self, t: Optional[Type]) -> bool:
        """True when t is a non-None, non-auto type."""
        if t is None:
            return False
        return True

    def _is_lvalue(self, expr: Expr) -> bool:
        """True when expr is a valid assignment target."""
        return isinstance(expr, (Identifier, MemberAccess))

    def _resolve_auto_var(self, expr: Expr, inferred_type: TyCType) -> None:
        """If expr is an Identifier that is an unresolved auto, set its type."""
        if isinstance(expr, Identifier) and expr.name in self.auto_vars:
            vdecl = self.auto_vars.pop(expr.name)
            # Update the local scope entry
            for scope in reversed(self.local_scopes):
                if expr.name in scope:
                    scope[expr.name] = inferred_type
                    break
            else:
                if expr.name in self.param_types:
                    self.param_types[expr.name] = inferred_type

    def _resolve_auto_var_from_unresolved(self, auto: "UnresolvedAuto", concrete_type: TyCType) -> None:
        """Resolve an UnresolvedAuto from a concrete type."""
        self._resolve_auto_var(Identifier(auto.name), concrete_type)

    def _resolve_auto_var_from_name(self, name: str, type_name: str) -> None:
        """Resolve an auto variable by name given a type name string."""
        if name in self.auto_vars:
            vdecl = self.auto_vars.pop(name)
            inferred_type = self._type_from_name(type_name)
            for scope in reversed(self.local_scopes):
                if name in scope:
                    scope[name] = inferred_type
                    break
            else:
                if name in self.param_types:
                    self.param_types[name] = inferred_type

    @staticmethod
    def _type_from_name(name: Optional[str]) -> TyCType:
        """Convert a type name string to a Type object."""
        if name == "int":   return IntType()
        if name == "float": return FloatType()
        if name == "string": return StringType()
        if name == "void":  return VoidType()
        return IntType()

    def _matches_simple_type(self, actual: Type, expected_name: str) -> bool:
        """Check if actual type matches expected name ('int', 'float', 'string')."""
        if expected_name == "int":   return isinstance(actual, IntType)
        if expected_name == "float": return isinstance(actual, FloatType)
        if expected_name == "string": return isinstance(actual, StringType)
        return False

    # ------------------------------------------------------------------
    # Helper: check a function body (used for forward-reference validation)
    # ------------------------------------------------------------------
    def _check_func_body(self, func_decl: "FuncDecl") -> None:
        """Check a function's body without affecting the current function's state.
        Used to validate forward-referenced function calls."""
        self.param_types.clear()
        self.local_scopes.clear()
        self.local_scopes.append({})
        self.auto_vars.clear()
        self._func_struct_types.clear()
        self.loop_depth = 0
        self.inferred_return_type = None
        self.func_return_is_auto = func_decl.return_type is None
        self._in_switch = False

        # Register parameters
        param_names: Set[str] = set()
        for p in func_decl.params:
            if p.name in param_names:
                raise Redeclared("Parameter", p.name)
            param_names.add(p.name)
            ptype = self._resolve_type_node(p.param_type)
            self.param_types[p.name] = ptype

        # Check body
        self.visit(func_decl.body)

        # Check unresolved autos
        for name, vdecl in list(self.auto_vars.items()):
            raise TypeCannotBeInferred(vdecl)

        # Validate struct types used in this body
        for stype in self._func_struct_types:
            if stype.struct_name not in self.structs:
                raise UndeclaredStruct(stype.struct_name)

        # Validate return type consistency
        if func_decl.return_type is not None:
            explicit_type = self._resolve_type_node(func_decl.return_type)
            if self.inferred_return_type is None:
                pass  # void returns only
            elif not self.types_compatible(explicit_type, self.inferred_return_type):
                raise TypeMismatchInStatement(func_decl.body)
