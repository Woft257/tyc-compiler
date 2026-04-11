"""
AST Generation module for TyC programming language.
This module contains the ASTGeneration class that converts parse trees
into Abstract Syntax Trees using the visitor pattern.
"""

from build.TyCVisitor import TyCVisitor
from build.TyCParser import TyCParser
from src.utils.nodes import *


class ASTGeneration(TyCVisitor):
    """AST Generation visitor for TyC language."""

    # ==================== Helpers ====================

    def getLine(self, ctx):
        return ctx.start.line if ctx.start else None

    def getColumn(self, ctx):
        return ctx.start.column if ctx.start else None

    # ==================== Program ====================

    def visitProgram(self, ctx: TyCParser.ProgramContext):
        decls = []
        decl_ctxs = ctx.decl()
        for decl_ctx in decl_ctxs:
            decl = self.visit(decl_ctx)
            if decl:
                decls.append(decl)
        program = Program(decls)
        program.line = self.getLine(ctx)
        program.column = self.getColumn(ctx)
        return program

    # ==================== Declarations ====================

    def visitDecl(self, ctx: TyCParser.DeclContext):
        if ctx.structDecl():
            return self.visit(ctx.structDecl())
        elif ctx.funcDecl():
            return self.visit(ctx.funcDecl())
        return None

    def visitFuncDecl(self, ctx: TyCParser.FuncDeclContext):
        # type? ID LPAREN paramList? RPAREN blockStmt
        return_type = self.visit(ctx.type_()) if ctx.type_() else None
        name = ctx.ID().getText()
        params = self.visit(ctx.paramList()) if ctx.paramList() else []
        body = self.visit(ctx.blockStmt())

        func_decl = FuncDecl(return_type, name, params, body)
        func_decl.line = self.getLine(ctx)
        func_decl.column = self.getColumn(ctx)
        return func_decl

    def visitParamList(self, ctx: TyCParser.ParamListContext):
        params = []
        param_ctxs = ctx.param()
        for param_ctx in param_ctxs:
            param = self.visit(param_ctx)
            if param:
                params.append(param)
        return params

    def visitParam(self, ctx: TyCParser.ParamContext):
        param_type = self.visit(ctx.type_())
        name = ctx.ID().getText()
        param = Param(param_type, name)
        param.line = self.getLine(ctx)
        param.column = self.getColumn(ctx)
        return param

    def visitStructDecl(self, ctx: TyCParser.StructDeclContext):
        # STRUCT ID LBRACE fieldDecl* RBRACE SEMI
        name = ctx.ID().getText()
        members = []
        field_ctxs = ctx.fieldDecl()
        for field_ctx in field_ctxs:
            member = self.visit(field_ctx)
            if member:
                members.append(member)

        struct_decl = StructDecl(name, members)
        struct_decl.line = self.getLine(ctx)
        struct_decl.column = self.getColumn(ctx)
        return struct_decl

    def visitFieldDecl(self, ctx: TyCParser.FieldDeclContext):
        member_type = self.visit(ctx.type_())
        name = ctx.ID().getText()
        member = MemberDecl(member_type, name)
        member.line = self.getLine(ctx)
        member.column = self.getColumn(ctx)
        return member

    # ==================== Types ====================

    def visitType(self, ctx: TyCParser.TypeContext):
        if ctx.INT():
            node = IntType()
        elif ctx.FLOAT():
            node = FloatType()
        elif ctx.STRING():
            node = StringType()
        elif ctx.VOID():
            node = VoidType()
        else:
            # ID - struct type
            node = StructType(ctx.ID().getText())

        node.line = self.getLine(ctx)
        node.column = self.getColumn(ctx)
        return node

    # ==================== Statements ====================

    def visitBlockStmt(self, ctx: TyCParser.BlockStmtContext):
        statements = []
        # (varDeclStmt | stmt)*
        for var_decl in ctx.varDeclStmt():
            stmt = self.visit(var_decl)
            if stmt:
                statements.append(stmt)
        for stmt_ctx in ctx.stmt():
            stmt = self.visit(stmt_ctx)
            if stmt:
                statements.append(stmt)

        block = BlockStmt(statements)
        block.line = self.getLine(ctx)
        block.column = self.getColumn(ctx)
        return block

    def visitVarDeclStmt(self, ctx: TyCParser.VarDeclStmtContext):
        # AUTO ID (ASSIGN expr)? SEMI
        # | type ID (ASSIGN expr)? SEMI
        if ctx.AUTO():
            var_type = None
            name = ctx.ID().getText()
        else:
            var_type = self.visit(ctx.type_())
            name = ctx.ID().getText()

        init_value = self.visit(ctx.expr()) if ctx.expr() else None

        var_decl = VarDecl(var_type, name, init_value)
        var_decl.line = self.getLine(ctx)
        var_decl.column = self.getColumn(ctx)
        return var_decl

    def visitStmt(self, ctx: TyCParser.StmtContext):
        if ctx.blockStmt():
            return self.visit(ctx.blockStmt())
        elif ctx.ifStmt():
            return self.visit(ctx.ifStmt())
        elif ctx.whileStmt():
            return self.visit(ctx.whileStmt())
        elif ctx.forStmt():
            return self.visit(ctx.forStmt())
        elif ctx.switchStmt():
            return self.visit(ctx.switchStmt())
        elif ctx.BREAK():
            break_stmt = BreakStmt()
            break_stmt.line = self.getLine(ctx)
            break_stmt.column = self.getColumn(ctx)
            return break_stmt
        elif ctx.CONTINUE():
            continue_stmt = ContinueStmt()
            continue_stmt.line = self.getLine(ctx)
            continue_stmt.column = self.getColumn(ctx)
            return continue_stmt
        elif ctx.returnStmt():
            return self.visit(ctx.returnStmt())
        elif ctx.expr():
            expr = self.visit(ctx.expr())
            expr_stmt = ExprStmt(expr)
            expr_stmt.line = self.getLine(ctx)
            expr_stmt.column = self.getColumn(ctx)
            return expr_stmt
        return None

    def visitIfStmt(self, ctx: TyCParser.IfStmtContext):
        # IF LPAREN expr RPAREN stmt (ELSE stmt)?
        condition = self.visit(ctx.expr())
        then_stmt = self.visit(ctx.stmt(0))
        else_stmt = self.visit(ctx.stmt(1)) if ctx.stmt(1) else None

        if_stmt = IfStmt(condition, then_stmt, else_stmt)
        if_stmt.line = self.getLine(ctx)
        if_stmt.column = self.getColumn(ctx)
        return if_stmt

    def visitWhileStmt(self, ctx: TyCParser.WhileStmtContext):
        # WHILE LPAREN expr RPAREN stmt
        condition = self.visit(ctx.expr())
        body = self.visit(ctx.stmt())

        while_stmt = WhileStmt(condition, body)
        while_stmt.line = self.getLine(ctx)
        while_stmt.column = self.getColumn(ctx)
        return while_stmt

    def visitForStmt(self, ctx: TyCParser.ForStmtContext):
        # FOR LPAREN forInit? SEMI expr? SEMI forUpdate? RPAREN stmt
        init = self.visit(ctx.forInit()) if ctx.forInit() else None
        condition = self.visit(ctx.expr()) if ctx.expr() else None
        update = self.visit(ctx.forUpdate()) if ctx.forUpdate() else None
        body = self.visit(ctx.stmt())

        for_stmt = ForStmt(init, condition, update, body)
        for_stmt.line = self.getLine(ctx)
        for_stmt.column = self.getColumn(ctx)
        return for_stmt

    def visitForInit(self, ctx: TyCParser.ForInitContext):
        if ctx.varDeclFor():
            return self.visit(ctx.varDeclFor())
        elif ctx.assignmentExpr():
            return self.visit(ctx.assignmentExpr())
        return None

    def visitVarDeclFor(self, ctx: TyCParser.VarDeclForContext):
        # AUTO ID (ASSIGN expr)?
        # | type ID (ASSIGN expr)?
        if ctx.AUTO():
            var_type = None
            name = ctx.ID().getText()
        else:
            var_type = self.visit(ctx.type_())
            name = ctx.ID().getText()

        init_value = self.visit(ctx.expr()) if ctx.expr() else None

        var_decl = VarDecl(var_type, name, init_value)
        var_decl.line = self.getLine(ctx)
        var_decl.column = self.getColumn(ctx)
        return var_decl

    def visitForUpdate(self, ctx: TyCParser.ForUpdateContext):
        if ctx.assignmentExpr():
            return self.visit(ctx.assignmentExpr())
        elif ctx.incDecExpr():
            return self.visit(ctx.incDecExpr())
        return None

    def visitSwitchStmt(self, ctx: TyCParser.SwitchStmtContext):
        # SWITCH LPAREN expr RPAREN LBRACE switchItem* RBRACE
        expr = self.visit(ctx.expr())
        cases = []
        default_case = None

        switch_items = ctx.switchItem()
        for item in switch_items:
            result = self.visit(item)
            if isinstance(result, CaseStmt):
                cases.append(result)
            elif isinstance(result, DefaultStmt):
                default_case = result

        switch_stmt = SwitchStmt(expr, cases, default_case)
        switch_stmt.line = self.getLine(ctx)
        switch_stmt.column = self.getColumn(ctx)
        return switch_stmt

    def visitSwitchItem(self, ctx: TyCParser.SwitchItemContext):
        # CASE expr COLON (varDeclStmt | stmt)*
        # | DEFAULT COLON (varDeclStmt | stmt)*
        if ctx.CASE():
            expr = self.visit(ctx.expr())
            statements = []
            for var_decl in ctx.varDeclStmt():
                stmt = self.visit(var_decl)
                if stmt:
                    statements.append(stmt)
            for stmt_ctx in ctx.stmt():
                stmt = self.visit(stmt_ctx)
                if stmt:
                    statements.append(stmt)

            case_stmt = CaseStmt(expr, statements)
            case_stmt.line = self.getLine(ctx)
            case_stmt.column = self.getColumn(ctx)
            return case_stmt
        else:
            # DEFAULT
            statements = []
            for var_decl in ctx.varDeclStmt():
                stmt = self.visit(var_decl)
                if stmt:
                    statements.append(stmt)
            for stmt_ctx in ctx.stmt():
                stmt = self.visit(stmt_ctx)
                if stmt:
                    statements.append(stmt)

            default_stmt = DefaultStmt(statements)
            default_stmt.line = self.getLine(ctx)
            default_stmt.column = self.getColumn(ctx)
            return default_stmt

    def visitReturnStmt(self, ctx: TyCParser.ReturnStmtContext):
        # RETURN expr? SEMI
        expr = self.visit(ctx.expr()) if ctx.expr() else None
        return_stmt = ReturnStmt(expr)
        return_stmt.line = self.getLine(ctx)
        return_stmt.column = self.getColumn(ctx)
        return return_stmt

    # ==================== Expressions ====================

    def visitExpr(self, ctx: TyCParser.ExprContext):
        return self.visit(ctx.assignmentExpr())

    def visitAssignmentExpr(self, ctx: TyCParser.AssignmentExprContext):
        # logicalOrExpr (ASSIGN assignmentExpr)?
        if ctx.ASSIGN():
            left = self.visit(ctx.logicalOrExpr())
            right = self.visit(ctx.assignmentExpr())
            assign_expr = AssignExpr(left, right)
            assign_expr.line = self.getLine(ctx)
            assign_expr.column = self.getColumn(ctx)
            return assign_expr
        else:
            return self.visit(ctx.logicalOrExpr())

    def visitLogicalOrExpr(self, ctx: TyCParser.LogicalOrExprContext):
        # logicalAndExpr (OR logicalAndExpr)*
        if ctx.OR():
            left = self.visit(ctx.logicalAndExpr(0))
            for i in range(1, len(ctx.logicalAndExpr())):
                right = self.visit(ctx.logicalAndExpr(i))
                binary_op = BinaryOp(left, '||', right)
                binary_op.line = left.line
                binary_op.column = left.column
                left = binary_op
            return left
        else:
            return self.visit(ctx.logicalAndExpr(0))

    def visitLogicalAndExpr(self, ctx: TyCParser.LogicalAndExprContext):
        # equalityExpr (AND equalityExpr)*
        if ctx.AND():
            left = self.visit(ctx.equalityExpr(0))
            for i in range(1, len(ctx.equalityExpr())):
                right = self.visit(ctx.equalityExpr(i))
                binary_op = BinaryOp(left, '&&', right)
                binary_op.line = left.line
                binary_op.column = left.column
                left = binary_op
            return left
        else:
            return self.visit(ctx.equalityExpr(0))

    def visitEqualityExpr(self, ctx: TyCParser.EqualityExprContext):
        # relationalExpr ((EQ | NEQ) relationalExpr)*
        rel_ctxs = ctx.relationalExpr()
        if len(rel_ctxs) > 1:
            left = self.visit(rel_ctxs[0])
            op = '==' if ctx.EQ() else '!='
            right = self.visit(rel_ctxs[1])
            binary_op = BinaryOp(left, op, right)
            binary_op.line = left.line
            binary_op.column = left.column
            return binary_op
        else:
            return self.visit(rel_ctxs[0])

    def visitRelationalExpr(self, ctx: TyCParser.RelationalExprContext):
        # additiveExpr ((LT | LE | GT | GE) additiveExpr)*
        add_ctxs = ctx.additiveExpr()
        if len(add_ctxs) > 1:
            left = self.visit(add_ctxs[0])
            if ctx.LT():
                op = '<'
            elif ctx.LE():
                op = '<='
            elif ctx.GT():
                op = '>'
            else:
                op = '>='
            right = self.visit(add_ctxs[1])
            binary_op = BinaryOp(left, op, right)
            binary_op.line = left.line
            binary_op.column = left.column
            return binary_op
        else:
            return self.visit(add_ctxs[0])

    def visitAdditiveExpr(self, ctx: TyCParser.AdditiveExprContext):
        # multiplicativeExpr ((PLUS | MINUS) multiplicativeExpr)*
        mult_ctxs = ctx.multiplicativeExpr()
        if len(mult_ctxs) > 1:
            left = self.visit(mult_ctxs[0])
            op = '+' if ctx.PLUS() else '-'
            for i in range(1, len(mult_ctxs)):
                right = self.visit(mult_ctxs[i])
                binary_op = BinaryOp(left, op, right)
                binary_op.line = left.line
                binary_op.column = left.column
                left = binary_op
            return left
        else:
            return self.visit(mult_ctxs[0])

    def visitMultiplicativeExpr(self, ctx: TyCParser.MultiplicativeExprContext):
        # unaryExpr ((MUL | DIV | MOD) unaryExpr)*
        unary_ctxs = ctx.unaryExpr()
        if len(unary_ctxs) > 1:
            left = self.visit(unary_ctxs[0])
            if ctx.MUL():
                op = '*'
            elif ctx.DIV():
                op = '/'
            else:
                op = '%'
            for i in range(1, len(unary_ctxs)):
                right = self.visit(unary_ctxs[i])
                binary_op = BinaryOp(left, op, right)
                binary_op.line = left.line
                binary_op.column = left.column
                left = binary_op
            return left
        else:
            return self.visit(unary_ctxs[0])

    def visitUnaryExpr(self, ctx: TyCParser.UnaryExprContext):
        # (INC | DEC) unaryExpr
        # | (NOT | PLUS | MINUS) unaryExpr
        # | postfixExpr
        if ctx.INC():
            operand = self.visit(ctx.unaryExpr())
            prefix_op = PrefixOp('++', operand)
            prefix_op.line = self.getLine(ctx)
            prefix_op.column = self.getColumn(ctx)
            return prefix_op
        elif ctx.DEC():
            operand = self.visit(ctx.unaryExpr())
            prefix_op = PrefixOp('--', operand)
            prefix_op.line = self.getLine(ctx)
            prefix_op.column = self.getColumn(ctx)
            return prefix_op
        elif ctx.NOT():
            operand = self.visit(ctx.unaryExpr())
            prefix_op = PrefixOp('!', operand)
            prefix_op.line = self.getLine(ctx)
            prefix_op.column = self.getColumn(ctx)
            return prefix_op
        elif ctx.PLUS():
            operand = self.visit(ctx.unaryExpr())
            prefix_op = PrefixOp('+', operand)
            prefix_op.line = self.getLine(ctx)
            prefix_op.column = self.getColumn(ctx)
            return prefix_op
        elif ctx.MINUS():
            operand = self.visit(ctx.unaryExpr())
            prefix_op = PrefixOp('-', operand)
            prefix_op.line = self.getLine(ctx)
            prefix_op.column = self.getColumn(ctx)
            return prefix_op
        else:
            return self.visit(ctx.postfixExpr())

    def visitPostfixExpr(self, ctx: TyCParser.PostfixExprContext):
        # primaryExpr postfixSuffix*
        result = self.visit(ctx.primaryExpr())

        suffix_ctxs = ctx.postfixSuffix()
        for suffix in suffix_ctxs:
            if suffix.DOT():
                # Member access
                member = suffix.ID().getText()
                result = MemberAccess(result, member)
                result.line = self.getLine(suffix)
                result.column = self.getColumn(suffix)
            elif suffix.INC():
                # Postfix increment
                result = PostfixOp('++', result)
                result.line = self.getLine(suffix)
                result.column = self.getColumn(suffix)
            elif suffix.DEC():
                # Postfix decrement
                result = PostfixOp('--', result)
                result.line = self.getLine(suffix)
                result.column = self.getColumn(suffix)

        return result

    def visitPrimaryExpr(self, ctx: TyCParser.PrimaryExprContext):
        # ID callSuffix?
        # | literal
        # | LPAREN expr RPAREN
        if ctx.ID():
            name = ctx.ID().getText()
            identifier = Identifier(name)
            identifier.line = self.getLine(ctx)
            identifier.column = self.getColumn(ctx)

            # Check for callSuffix
            if ctx.callSuffix():
                return self.visitCallSuffix(identifier, ctx.callSuffix())
            return identifier
        elif ctx.literal():
            return self.visit(ctx.literal())
        elif ctx.LPAREN():
            return self.visit(ctx.expr())
        return None

    def visitCallSuffix(self, identifier, ctx):
        # LPAREN argList? RPAREN
        args = self.visit(ctx.argList()) if ctx.argList() else []
        func_call = FuncCall(identifier.name, args)
        func_call.line = identifier.line
        func_call.column = identifier.column
        return func_call

    def visitArgList(self, ctx: TyCParser.ArgListContext):
        args = []
        expr_ctxs = ctx.expr()
        for expr_ctx in expr_ctxs:
            arg = self.visit(expr_ctx)
            if arg:
                args.append(arg)
        return args

    def visitIncDecExpr(self, ctx: TyCParser.IncDecExprContext):
        # (INC | DEC) primaryLValue
        # | primaryLValue (INC | DEC)
        if ctx.INC():
            operand = self.visit(ctx.primaryLValue())
            prefix_op = PrefixOp('++', operand)
            prefix_op.line = self.getLine(ctx)
            prefix_op.column = self.getColumn(ctx)
            return prefix_op
        elif ctx.DEC():
            operand = self.visit(ctx.primaryLValue())
            prefix_op = PrefixOp('--', operand)
            prefix_op.line = self.getLine(ctx)
            prefix_op.column = self.getColumn(ctx)
            return prefix_op
        else:
            # primaryLValue (INC | DEC)
            operand = self.visit(ctx.primaryLValue())
            if ctx.INC():
                postfix_op = PostfixOp('++', operand)
            else:
                postfix_op = PostfixOp('--', operand)
            postfix_op.line = self.getLine(ctx)
            postfix_op.column = self.getColumn(ctx)
            return postfix_op

    def visitPrimaryLValue(self, ctx: TyCParser.PrimaryLValueContext):
        # ID (DOT ID)*
        tokens = ctx.ID()
        name = tokens[0].getText()
        result = Identifier(name)
        result.line = self.getLine(ctx)
        result.column = self.getColumn(ctx)

        for i in range(1, len(tokens)):
            member = tokens[i].getText()
            result = MemberAccess(result, member)
            result.line = self.getLine(ctx)
            result.column = self.getColumn(ctx)

        return result

    def visitLiteral(self, ctx: TyCParser.LiteralContext):
        if ctx.INT_LIT():
            try:
                value = int(ctx.INT_LIT().getText())
            except ValueError:
                value = int(ctx.INT_LIT().getText(), 0)
            literal = IntLiteral(value)
        elif ctx.FLOAT_LIT():
            value = float(ctx.FLOAT_LIT().getText())
            literal = FloatLiteral(value)
        elif ctx.STRING_LIT():
            value = ctx.STRING_LIT().getText()
            literal = StringLiteral(value)
        else:
            literal = None

        if literal:
            literal.line = self.getLine(ctx)
            literal.column = self.getColumn(ctx)
        return literal
