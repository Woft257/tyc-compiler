"""
Code generator for TyC.
"""

from typing import Any

from ..utils.nodes import *
from ..utils.visitor import BaseVisitor
from .emitter import *
from .frame import *
from .io import IO_SYMBOL_LIST
from .utils import *


class StringArrayType:
    """Marker type for JVM main(String[] args)."""
    pass


class CodeGenerator(BaseVisitor):
    """Full AST -> Jasmin code generator for TyC."""

    def __init__(self):
        self.emit = None
        self.functions = {}
        self.structs = {}  # name -> [(member_name, member_type), ...]
        self.current_return_type = VoidType()
        self.class_name = "TyC"

    def _lookup_symbol(self, name: str, sym_list: list[Symbol]) -> Symbol:
        for sym in reversed(sym_list):
            if sym.name == name:
                return sym
        raise RuntimeError(f"Undeclared symbol: {name}")

    def _get_member_type(self, struct_name: str, member_name: str):
        for name, typ in self.structs[struct_name]:
            if name == member_name:
                return typ
        raise RuntimeError(f"Unknown member {member_name} in struct {struct_name}")

    def _infer_type(self, node: Expr, o: Access):
        if isinstance(node, IntLiteral):
            return IntType()
        if isinstance(node, FloatLiteral):
            return FloatType()
        if isinstance(node, StringLiteral):
            return StringType()
        if isinstance(node, Identifier):
            return self._lookup_symbol(node.name, o.sym).type
        if isinstance(node, AssignExpr):
            return self._infer_type(node.rhs, o)
        if isinstance(node, FuncCall):
            return self.functions[node.name].type.return_type
        if isinstance(node, MemberAccess):
            obj_type = self._infer_type(node.obj, o)
            return self._get_member_type(obj_type.struct_name, node.member)
        if isinstance(node, PrefixOp):
            if node.operator in ["!", "++", "--"]:
                return IntType()
            return self._infer_type(node.operand, o)
        if isinstance(node, PostfixOp):
            return IntType()
        if isinstance(node, StructLiteral):
            target = getattr(o, 'target_type', None)
            return target if target else IntType()
        if isinstance(node, BinaryOp):
            if node.operator in ["+", "-", "*", "/", "%"]:
                left_type = self._infer_type(node.left, o)
                right_type = self._infer_type(node.right, o)
                if is_float_type(left_type) or is_float_type(right_type):
                    return FloatType()
                return IntType()
            if node.operator in ["<", "<=", ">", ">=", "==", "!=", "&&", "||"]:
                return IntType()
        return IntType()

    def visit_program(self, node: Program, o: Any = None):
        self.emit = Emitter(f"{self.class_name}.j")
        self.emit.print_out(self.emit.emit_prolog(self.class_name))

        for io_sym in IO_SYMBOL_LIST:
            self.functions[io_sym.name] = io_sym

        # First pass: collect struct metadata and generate struct .j files
        for decl in node.decls:
            if isinstance(decl, StructDecl):
                self.visit(decl, None)

        # Second pass: collect function signatures
        for decl in node.decls:
            if isinstance(decl, FuncDecl):
                return_type = decl.return_type if decl.return_type else VoidType()
                param_types = [p.param_type for p in decl.params]
                self.functions[decl.name] = Symbol(
                    decl.name, FunctionType(param_types, return_type), CName(self.class_name)
                )

        # Third pass: generate function code
        for decl in node.decls:
            if isinstance(decl, FuncDecl):
                self.visit(decl, None)

        self.emit.emit_epilog()

    def visit_func_decl(self, node: FuncDecl, o: Any = None):
        self.current_return_type = node.return_type if node.return_type else VoidType()
        frame = Frame(node.name, self.current_return_type)
        frame.enter_scope(True)

        if node.name == "main":
            mtype = FunctionType([StringArrayType()], VoidType())
        else:
            mtype = FunctionType([p.param_type for p in node.params], self.current_return_type)

        self.emit.print_out(self.emit.emit_method(node.name, mtype, True))

        start_label = frame.get_start_label()
        end_label = frame.get_end_label()
        self.emit.print_out(self.emit.emit_label(start_label, frame))

        local_syms: list[Symbol] = []
        if node.name == "main":
            args_idx = frame.get_new_index()
            self.emit.print_out(
                self.emit.emit_var(
                    args_idx, "args", StringArrayType(), start_label, end_label
                )
            )

        for param in node.params:
            idx = frame.get_new_index()
            self.emit.print_out(
                self.emit.emit_var(idx, param.name, param.param_type, start_label, end_label)
            )
            local_syms.append(Symbol(param.name, param.param_type, Index(idx)))

        sub_body = SubBody(frame, local_syms)
        self.visit(node.body, sub_body)

        if is_void_type(self.current_return_type):
            self.emit.print_out(self.emit.emit_return(VoidType(), frame))

        self.emit.print_out(self.emit.emit_label(end_label, frame))
        frame.exit_scope()
        self.emit.print_out(self.emit.emit_end_method(frame))

    def visit_block_stmt(self, node: BlockStmt, o: SubBody = None):
        for stmt in node.statements:
            o = self.visit(stmt, o)
        return o

    def visit_var_decl(self, node: VarDecl, o: SubBody = None):
        frame = o.frame
        idx = frame.get_new_index()
        # If auto and no init, we assume it's IntType as a fallback for minimal codegen
        # unless semantic checker populated it (which we assume happens or explicit type is given).
        if node.var_type:
            var_type = node.var_type
        elif node.init_value:
            var_type = self._infer_type(node.init_value, Access(frame, o.sym))
        else:
            var_type = IntType() # fallback

        self.emit.print_out(
            self.emit.emit_var(
                idx, node.name, var_type, frame.get_start_label(), frame.get_end_label()
            )
        )
        if node.init_value is not None:
            rhs_access = Access(frame, o.sym)
            if isinstance(node.init_value, StructLiteral):
                rhs_access.target_type = var_type
            rhs_code, _ = self.visit(node.init_value, rhs_access)
            self.emit.print_out(rhs_code)
            self.emit.print_out(self.emit.emit_write_var(node.name, var_type, idx, frame))
        o.sym.append(Symbol(node.name, var_type, Index(idx)))
        return o

    def visit_expr_stmt(self, node: ExprStmt, o: SubBody = None):
        code, expr_type = self.visit(node.expr, Access(o.frame, o.sym))
        self.emit.print_out(code)
        if not is_void_type(expr_type):
            self.emit.print_out(self.emit.emit_pop(o.frame))
        return o

    def visit_if_stmt(self, node: IfStmt, o: SubBody = None):
        frame = o.frame
        cond_code, _ = self.visit(node.condition, Access(frame, o.sym))
        else_label = frame.get_new_label()
        end_label = frame.get_new_label()
        self.emit.print_out(cond_code)
        self.emit.print_out(self.emit.emit_if_false(else_label, frame))
        self.visit(node.then_stmt, o)
        self.emit.print_out(self.emit.emit_goto(end_label, frame))
        self.emit.print_out(self.emit.emit_label(else_label, frame))
        if node.else_stmt:
            self.visit(node.else_stmt, o)
        self.emit.print_out(self.emit.emit_label(end_label, frame))
        return o

    def visit_while_stmt(self, node: WhileStmt, o: SubBody = None):
        frame = o.frame
        start_label = frame.get_new_label()
        end_label = frame.get_new_label()
        self.emit.print_out(self.emit.emit_label(start_label, frame))
        cond_code, _ = self.visit(node.condition, Access(frame, o.sym))
        self.emit.print_out(cond_code)
        self.emit.print_out(self.emit.emit_if_false(end_label, frame))
        self.visit(node.body, o)
        self.emit.print_out(self.emit.emit_goto(start_label, frame))
        self.emit.print_out(self.emit.emit_label(end_label, frame))
        return o

    def visit_return_stmt(self, node: ReturnStmt, o: SubBody = None):
        if node.expr is None:
            self.emit.print_out(self.emit.emit_return(VoidType(), o.frame))
            return o
        code, ret_type = self.visit(node.expr, Access(o.frame, o.sym))
        self.emit.print_out(code)
        self.emit.print_out(self.emit.emit_return(ret_type, o.frame))
        return o

    def _coerce_code(self, left_code, left_type, right_code, right_type, frame):
        """Insert i2f coercion when one operand is int and the other is float."""
        if is_float_type(left_type) and is_int_type(right_type):
            return left_code, right_code + self.emit.emit_i2f(frame)
        if is_int_type(left_type) and is_float_type(right_type):
            return left_code + self.emit.emit_i2f(frame), right_code
        return left_code, right_code

    def visit_binary_op(self, node: BinaryOp, o: Access = None):
        frame = o.frame

        # Short-circuit && 
        if node.operator == "&&":
            left_code, _ = self.visit(node.left, o)
            false_label = frame.get_new_label()
            end_label = frame.get_new_label()
            code = left_code
            frame.pop()
            code += self.emit.jvm.emitIFEQ(false_label)
            right_code, _ = self.visit(node.right, o)
            code += right_code
            frame.pop()
            code += self.emit.jvm.emitIFEQ(false_label)
            code += self.emit.emit_push_iconst(1, frame)
            code += self.emit.emit_goto(end_label, frame)
            code += self.emit.emit_label(false_label, frame)
            code += self.emit.emit_push_iconst(0, frame)
            code += self.emit.emit_label(end_label, frame)
            return code, IntType()

        # Short-circuit ||
        if node.operator == "||":
            left_code, _ = self.visit(node.left, o)
            true_label = frame.get_new_label()
            end_label = frame.get_new_label()
            code = left_code
            frame.pop()
            code += self.emit.jvm.emitIFNE(true_label)
            right_code, _ = self.visit(node.right, o)
            code += right_code
            frame.pop()
            code += self.emit.jvm.emitIFNE(true_label)
            code += self.emit.emit_push_iconst(0, frame)
            code += self.emit.emit_goto(end_label, frame)
            code += self.emit.emit_label(true_label, frame)
            code += self.emit.emit_push_iconst(1, frame)
            code += self.emit.emit_label(end_label, frame)
            return code, IntType()

        left_code, left_type = self.visit(node.left, o)
        right_code, right_type = self.visit(node.right, o)

        if node.operator in ["+", "-"]:
            result_type = FloatType() if is_float_type(left_type) or is_float_type(right_type) else IntType()
            left_code, right_code = self._coerce_code(left_code, left_type, right_code, right_type, frame)
            return (
                left_code + right_code
                + self.emit.emit_add_op(node.operator, result_type, frame),
                result_type,
            )
        if node.operator in ["*", "/"]:
            result_type = FloatType() if is_float_type(left_type) or is_float_type(right_type) else IntType()
            left_code, right_code = self._coerce_code(left_code, left_type, right_code, right_type, frame)
            return (
                left_code + right_code
                + self.emit.emit_mul_op(node.operator, result_type, frame),
                result_type,
            )
        if node.operator == "%":
            return left_code + right_code + self.emit.emit_mod(frame), IntType()
        if node.operator in ["<", "<=", ">", ">=", "==", "!="]:
            op_type = FloatType() if is_float_type(left_type) or is_float_type(right_type) else IntType()
            left_code, right_code = self._coerce_code(left_code, left_type, right_code, right_type, frame)
            return left_code + right_code + self.emit.emit_re_op(node.operator, op_type, frame), IntType()
        raise RuntimeError(f"Unsupported operator: {node.operator}")

    def visit_assign_expr(self, node: AssignExpr, o: Access = None):
        frame = o.frame

        # Assignment to struct member: p.x = expr
        if isinstance(node.lhs, MemberAccess):
            obj_code, obj_type = self.visit(node.lhs.obj, o)
            struct_name = obj_type.struct_name
            mem_name = node.lhs.member
            mem_type = self._get_member_type(struct_name, mem_name)
            # Pass target_type for struct literal RHS
            rhs_access = Access(frame, o.sym)
            if isinstance(node.rhs, StructLiteral):
                rhs_access.target_type = mem_type
            rhs_code, rhs_type = self.visit(node.rhs, rhs_access)
            code = obj_code + rhs_code
            code += self.emit.emit_dup_x1(frame)
            code += self.emit.emit_put_field(f"{struct_name}/{mem_name}", mem_type, frame)
            return code, rhs_type

        # Assignment to identifier: x = expr
        if isinstance(node.lhs, Identifier):
            lhs_sym = self._lookup_symbol(node.lhs.name, o.sym)
            # Pass target_type for struct literal RHS
            rhs_access = Access(frame, o.sym)
            if isinstance(node.rhs, StructLiteral):
                rhs_access.target_type = lhs_sym.type
            rhs_code, rhs_type = self.visit(node.rhs, rhs_access)
            idx = lhs_sym.value.value
            code = rhs_code + self.emit.emit_dup(frame) + self.emit.emit_write_var(
                node.lhs.name, lhs_sym.type, idx, frame
            )
            return code, rhs_type

        raise RuntimeError(f"Unsupported assignment LHS: {type(node.lhs)}")

    def visit_func_call(self, node: FuncCall, o: Access = None):
        frame = o.frame
        fn_sym = self.functions[node.name]
        fn_type = fn_sym.type
        code = ""
        for i, arg in enumerate(node.args):
            arg_access = Access(frame, o.sym)
            # Pass target_type for struct literal args
            if isinstance(arg, StructLiteral) and i < len(fn_type.param_types):
                arg_access.target_type = fn_type.param_types[i]
            arg_code, _ = self.visit(arg, arg_access)
            code += arg_code
        code += self.emit.emit_invoke_static(f"{fn_sym.value.value}/{node.name}", fn_type, frame)
        return code, fn_type.return_type

    def visit_identifier(self, node: Identifier, o: Access = None):
        sym = self._lookup_symbol(node.name, o.sym)
        return self.emit.emit_read_var(node.name, sym.type, sym.value.value, o.frame), sym.type

    def visit_int_literal(self, node: IntLiteral, o: Access = None):
        return self.emit.emit_push_iconst(node.value, o.frame), IntType()

    def visit_float_literal(self, node: FloatLiteral, o: Access = None):
        return self.emit.emit_push_fconst(str(node.value), o.frame), FloatType()

    def visit_string_literal(self, node: StringLiteral, o: Access = None):
        return self.emit.emit_push_const(node.value, StringType(), o.frame), StringType()

    def visit_struct_decl(self, node: StructDecl, o: Any = None):
        # Store struct metadata
        members = [(m.name, m.member_type) for m in node.members]
        self.structs[node.name] = members

        # Generate a separate .j class file for this struct
        struct_emit = Emitter(f"{node.name}.j")
        code = ""
        code += struct_emit.jvm.emitSOURCE(f"{node.name}.java")
        code += struct_emit.jvm.emitCLASS(f"public {node.name}")
        code += struct_emit.jvm.emitSUPER("java/lang/Object")

        # Fields
        for mem_name, mem_type in members:
            jvm_type = struct_emit.get_jvm_type(mem_type)
            code += f".field public {mem_name} {jvm_type}\n"

        # Default constructor
        code += "\n.method public <init>()V\n"
        code += "\taload_0\n"
        code += "\tinvokespecial java/lang/Object/<init>()V\n"
        code += "\treturn\n"
        code += ".end method\n"

        struct_emit.buff.append(code)
        struct_emit.emit_epilog()
        return None

    def visit_member_decl(self, node: MemberDecl, o: Any = None):
        return None

    def visit_param(self, node: Param, o: Any = None):
        return None

    def visit_int_type(self, node: IntType, o: Any = None):
        return node

    def visit_float_type(self, node: FloatType, o: Any = None):
        return node

    def visit_string_type(self, node: StringType, o: Any = None):
        return node

    def visit_void_type(self, node: VoidType, o: Any = None):
        return node

    def visit_struct_type(self, node: StructType, o: Any = None):
        return node

    def visit_for_stmt(self, node: ForStmt, o: SubBody = None):
        frame = o.frame

        # Visit init (VarDecl or ExprStmt)
        if node.init:
            o = self.visit(node.init, o)

        loop_start_label = frame.get_new_label()
        break_label = frame.get_new_label()
        continue_label = frame.get_new_label()

        # Push break/continue labels manually (continue → update, not condition)
        frame.con_label.append(continue_label)
        frame.brk_label.append(break_label)

        # Loop start: check condition
        self.emit.print_out(self.emit.emit_label(loop_start_label, frame))
        if node.condition:
            cond_code, _ = self.visit(node.condition, Access(frame, o.sym))
            self.emit.print_out(cond_code)
            self.emit.print_out(self.emit.emit_if_false(break_label, frame))

        # Body
        self.visit(node.body, o)

        # Continue label: update
        self.emit.print_out(self.emit.emit_label(continue_label, frame))
        if node.update:
            update_code, _ = self.visit(node.update, Access(frame, o.sym))
            self.emit.print_out(update_code)
            self.emit.print_out(self.emit.emit_pop(frame))

        # Jump back to condition
        self.emit.print_out(self.emit.emit_goto(loop_start_label, frame))

        # Break label
        self.emit.print_out(self.emit.emit_label(break_label, frame))

        # Pop break/continue labels
        frame.con_label.pop()
        frame.brk_label.pop()
        return o

    def visit_switch_stmt(self, node: SwitchStmt, o: SubBody = None):
        frame = o.frame

        # Evaluate switch expression
        expr_code, _ = self.visit(node.expr, Access(frame, o.sym))
        self.emit.print_out(expr_code)

        end_label = frame.get_new_label()
        frame.brk_label.append(end_label)

        # Generate labels for each case body and default
        case_body_labels = [frame.get_new_label() for _ in node.cases]
        default_body_label = frame.get_new_label() if node.default_case else None

        # Phase 1: Comparison jump table
        for i, case in enumerate(node.cases):
            self.emit.print_out(self.emit.emit_dup(frame))
            case_val_code, _ = self.visit(case.expr, Access(frame, o.sym))
            self.emit.print_out(case_val_code)
            next_cmp_label = frame.get_new_label()
            # if_icmpne: pops two, jumps if not equal
            frame.pop()
            frame.pop()
            self.emit.print_out(self.emit.jvm.emitIFICMPNE(next_cmp_label))
            # Match: pop the original switch value and goto body
            self.emit.print_out(self.emit.emit_pop(frame))
            self.emit.print_out(self.emit.emit_goto(case_body_labels[i], frame))
            self.emit.print_out(self.emit.emit_label(next_cmp_label, frame))

        # No case matched: pop switch value, goto default or end
        self.emit.print_out(self.emit.emit_pop(frame))
        if default_body_label:
            self.emit.print_out(self.emit.emit_goto(default_body_label, frame))
        else:
            self.emit.print_out(self.emit.emit_goto(end_label, frame))

        # Phase 2: Case bodies (fall-through)
        for i, case in enumerate(node.cases):
            self.emit.print_out(self.emit.emit_label(case_body_labels[i], frame))
            for stmt in case.statements:
                o = self.visit(stmt, o)

        # Default body
        if node.default_case:
            self.emit.print_out(self.emit.emit_label(default_body_label, frame))
            for stmt in node.default_case.statements:
                o = self.visit(stmt, o)

        self.emit.print_out(self.emit.emit_label(end_label, frame))
        frame.brk_label.pop()
        return o

    def visit_case_stmt(self, node: CaseStmt, o: Any = None):
        # Handled inside visit_switch_stmt
        return None

    def visit_default_stmt(self, node: DefaultStmt, o: Any = None):
        # Handled inside visit_switch_stmt
        return None

    def visit_break_stmt(self, node: BreakStmt, o: SubBody = None):
        frame = o.frame
        self.emit.print_out(self.emit.emit_goto(frame.get_break_label(), frame))
        return o

    def visit_continue_stmt(self, node: ContinueStmt, o: SubBody = None):
        frame = o.frame
        self.emit.print_out(self.emit.emit_goto(frame.get_continue_label(), frame))
        return o

    def visit_prefix_op(self, node: PrefixOp, o: Access = None):
        frame = o.frame
        op = node.operator

        # Unary + : no-op
        if op == "+":
            return self.visit(node.operand, o)

        # Unary - : negate
        if op == "-":
            code, typ = self.visit(node.operand, o)
            return code + self.emit.emit_neg_op(typ, frame), typ

        # Logical NOT
        if op == "!":
            code, typ = self.visit(node.operand, o)
            # if operand == 0 → push 1, else push 0
            label_f = frame.get_new_label()
            label_o = frame.get_new_label()
            frame.pop()
            not_code = self.emit.jvm.emitIFNE(label_f)
            not_code += self.emit.emit_push_iconst(1, frame)
            not_code += self.emit.emit_goto(label_o, frame)
            not_code += self.emit.emit_label(label_f, frame)
            not_code += self.emit.emit_push_iconst(0, frame)
            not_code += self.emit.emit_label(label_o, frame)
            return code + not_code, IntType()

        # Prefix ++ / -- on Identifier
        if isinstance(node.operand, Identifier):
            sym = self._lookup_symbol(node.operand.name, o.sym)
            idx = sym.value.value
            code = self.emit.emit_read_var(node.operand.name, sym.type, idx, frame)
            code += self.emit.emit_push_iconst(1, frame)
            if op == "++":
                code += self.emit.emit_add_op("+", IntType(), frame)
            else:
                code += self.emit.emit_add_op("-", IntType(), frame)
            code += self.emit.emit_dup(frame)
            code += self.emit.emit_write_var(node.operand.name, sym.type, idx, frame)
            return code, IntType()

        # Prefix ++ / -- on MemberAccess
        if isinstance(node.operand, MemberAccess):
            obj_code, obj_type = self.visit(node.operand.obj, o)
            struct_name = obj_type.struct_name
            mem_name = node.operand.member
            mem_type = self._get_member_type(struct_name, mem_name)
            code = obj_code
            code += self.emit.emit_dup(frame)
            code += self.emit.emit_get_field(f"{struct_name}/{mem_name}", mem_type, frame)
            code += self.emit.emit_push_iconst(1, frame)
            if op == "++":
                code += self.emit.emit_add_op("+", IntType(), frame)
            else:
                code += self.emit.emit_add_op("-", IntType(), frame)
            code += self.emit.emit_dup_x1(frame)
            code += self.emit.emit_put_field(f"{struct_name}/{mem_name}", mem_type, frame)
            return code, IntType()

        raise RuntimeError(f"PrefixOp {op} on unsupported operand type")

    def visit_postfix_op(self, node: PostfixOp, o: Access = None):
        frame = o.frame
        op = node.operator

        # Postfix ++ / -- on Identifier
        if isinstance(node.operand, Identifier):
            sym = self._lookup_symbol(node.operand.name, o.sym)
            idx = sym.value.value
            code = self.emit.emit_read_var(node.operand.name, sym.type, idx, frame)
            code += self.emit.emit_dup(frame)
            code += self.emit.emit_push_iconst(1, frame)
            if op == "++":
                code += self.emit.emit_add_op("+", IntType(), frame)
            else:
                code += self.emit.emit_add_op("-", IntType(), frame)
            code += self.emit.emit_write_var(node.operand.name, sym.type, idx, frame)
            return code, IntType()

        # Postfix ++ / -- on MemberAccess
        if isinstance(node.operand, MemberAccess):
            obj_code, obj_type = self.visit(node.operand.obj, o)
            struct_name = obj_type.struct_name
            mem_name = node.operand.member
            mem_type = self._get_member_type(struct_name, mem_name)
            code = obj_code
            code += self.emit.emit_dup(frame)
            code += self.emit.emit_get_field(f"{struct_name}/{mem_name}", mem_type, frame)
            code += self.emit.emit_dup_x1(frame)
            code += self.emit.emit_push_iconst(1, frame)
            if op == "++":
                code += self.emit.emit_add_op("+", IntType(), frame)
            else:
                code += self.emit.emit_add_op("-", IntType(), frame)
            code += self.emit.emit_put_field(f"{struct_name}/{mem_name}", mem_type, frame)
            return code, IntType()

        raise RuntimeError(f"PostfixOp {op} on unsupported operand type")

    def visit_member_access(self, node: MemberAccess, o: Access = None):
        obj_code, obj_type = self.visit(node.obj, o)
        struct_name = obj_type.struct_name
        mem_type = self._get_member_type(struct_name, node.member)
        code = obj_code + self.emit.emit_get_field(
            f"{struct_name}/{node.member}", mem_type, o.frame
        )
        return code, mem_type

    def visit_struct_literal(self, node: StructLiteral, o: Access = None):
        frame = o.frame
        target_type = getattr(o, 'target_type', None)
        if target_type is None:
            raise RuntimeError("StructLiteral requires target_type in Access")
        struct_name = target_type.struct_name
        members = self.structs[struct_name]

        code = self.emit.emit_new_instance(struct_name, frame)
        for i, val_expr in enumerate(node.values):
            mem_name, mem_type = members[i]
            code += self.emit.emit_dup(frame)
            # Pass target_type for nested struct literals
            sub_access = Access(frame, o.sym)
            if isinstance(val_expr, StructLiteral):
                sub_access.target_type = mem_type
            val_code, _ = self.visit(val_expr, sub_access)
            code += val_code
            code += self.emit.emit_put_field(f"{struct_name}/{mem_name}", mem_type, frame)
        return code, target_type

