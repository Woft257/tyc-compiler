"""
AST Generation test cases for TyC compiler.
100 test cases for AST generation covering all language features.
"""

import pytest
from tests.utils import ASTGenerator
from src.utils.nodes import *


class TestLiterals:
    """Test literal expressions"""

    def test_int_literal(self):
        source = """void main() {
            int x = 123;
        }"""
        ast = ASTGenerator(source).generate()
        assert ast is not None
        assert isinstance(ast, Program)
        assert len(ast.decls) == 1

    def test_float_literal(self):
        source = """void main() {
            float x = 1.5;
        }"""
        ast = ASTGenerator(source).generate()
        assert ast is not None

    def test_string_literal(self):
        source = """void main() {
            string s = "hello";
        }"""
        ast = ASTGenerator(source).generate()
        assert ast is not None


class TestTypes:
    """Test type nodes"""

    def test_int_type(self):
        source = """int main() {
        }"""
        ast = ASTGenerator(source).generate()
        func = ast.decls[0]
        assert isinstance(func.return_type, IntType)

    def test_float_type(self):
        source = """float main() {
        }"""
        ast = ASTGenerator(source).generate()
        func = ast.decls[0]
        assert isinstance(func.return_type, FloatType)

    def test_void_type(self):
        source = """void main() {
        }"""
        ast = ASTGenerator(source).generate()
        func = ast.decls[0]
        assert isinstance(func.return_type, VoidType)

    def test_string_type(self):
        source = """string main() {
        }"""
        ast = ASTGenerator(source).generate()
        func = ast.decls[0]
        assert isinstance(func.return_type, StringType)

    def test_struct_type(self):
        source = """Person foo() {
        }"""
        ast = ASTGenerator(source).generate()
        func = ast.decls[0]
        assert isinstance(func.return_type, StructType)
        assert func.return_type.struct_name == "Person"


class TestDeclarations:
    """Test declarations"""

    def test_empty_program(self):
        source = """ """
        ast = ASTGenerator(source).generate()
        assert ast is not None
        assert isinstance(ast, Program)
        assert len(ast.decls) == 0

    def test_single_function(self):
        source = """void main() {
        }"""
        ast = ASTGenerator(source).generate()
        assert len(ast.decls) == 1
        assert isinstance(ast.decls[0], FuncDecl)
        assert ast.decls[0].name == "main"

    def test_multiple_functions(self):
        source = """void main() {
}
int foo() {
}"""
        ast = ASTGenerator(source).generate()
        assert len(ast.decls) == 2

    def test_function_with_params(self):
        source = """void main(int a, float b) {
        }"""
        ast = ASTGenerator(source).generate()
        func = ast.decls[0]
        assert len(func.params) == 2

    def test_function_with_no_params(self):
        source = """void main() {
        }"""
        ast = ASTGenerator(source).generate()
        func = ast.decls[0]
        assert len(func.params) == 0

    def test_struct_declaration(self):
        source = """struct Person {
    int age;
    string name;
};"""
        ast = ASTGenerator(source).generate()
        assert len(ast.decls) == 1
        struct = ast.decls[0]
        assert isinstance(struct, StructDecl)
        assert struct.name == "Person"
        assert len(struct.members) == 2


class TestStatements:
    """Test statements"""

    def test_block_statement(self):
        source = """void main() {
            int x;
        }"""
        ast = ASTGenerator(source).generate()
        func = ast.decls[0]
        assert isinstance(func.body, BlockStmt)
        assert len(func.body.statements) == 1

    def test_var_decl_no_init(self):
        source = """void main() {
            int x;
        }"""
        ast = ASTGenerator(source).generate()
        func = ast.decls[0]
        stmt = func.body.statements[0]
        assert isinstance(stmt, VarDecl)
        assert stmt.name == "x"
        assert stmt.init_value is None

    def test_var_decl_with_init(self):
        source = """void main() {
            int x = 5;
        }"""
        ast = ASTGenerator(source).generate()
        func = ast.decls[0]
        stmt = func.body.statements[0]
        assert isinstance(stmt, VarDecl)
        assert stmt.init_value is not None

    def test_auto_var_decl(self):
        source = """void main() {
            auto x = 5;
        }"""
        ast = ASTGenerator(source).generate()
        func = ast.decls[0]
        stmt = func.body.statements[0]
        assert isinstance(stmt, VarDecl)
        assert stmt.var_type is None

    def test_if_stmt_no_else(self):
        source = """void main() {
            if (1) {
            }
        }"""
        ast = ASTGenerator(source).generate()
        func = ast.decls[0]
        stmt = func.body.statements[0]
        assert isinstance(stmt, IfStmt)
        assert stmt.else_stmt is None

    def test_if_stmt_with_else(self):
        source = """void main() {
            if (1) {
            } else {
            }
        }"""
        ast = ASTGenerator(source).generate()
        func = ast.decls[0]
        stmt = func.body.statements[0]
        assert isinstance(stmt, IfStmt)
        assert stmt.else_stmt is not None

    def test_while_stmt(self):
        source = """void main() {
            while (1) {
            }
        }"""
        ast = ASTGenerator(source).generate()
        func = ast.decls[0]
        stmt = func.body.statements[0]
        assert isinstance(stmt, WhileStmt)

    def test_for_stmt(self):
        source = """void main() {
            for (int i = 0; i < 10; i = i + 1) {
            }
        }"""
        ast = ASTGenerator(source).generate()
        func = ast.decls[0]
        stmt = func.body.statements[0]
        assert isinstance(stmt, ForStmt)

    def test_for_stmt_empty_init(self):
        source = """void main() {
            for (; i < 10; i = i + 1) {
            }
        }"""
        ast = ASTGenerator(source).generate()
        func = ast.decls[0]
        stmt = func.body.statements[0]
        assert isinstance(stmt, ForStmt)
        assert stmt.init is None

    def test_for_stmt_empty_condition(self):
        source = """void main() {
            for (int i = 0; ; i = i + 1) {
            }
        }"""
        ast = ASTGenerator(source).generate()
        func = ast.decls[0]
        stmt = func.body.statements[0]
        assert isinstance(stmt, ForStmt)
        assert stmt.condition is None

    def test_for_stmt_empty_update(self):
        source = """void main() {
            for (int i = 0; i < 10;) {
            }
        }"""
        ast = ASTGenerator(source).generate()
        func = ast.decls[0]
        stmt = func.body.statements[0]
        assert isinstance(stmt, ForStmt)
        assert stmt.update is None

    def test_switch_stmt_with_cases(self):
        source = """void main() {
            switch (x) {
                case 1: break;
                case 2: break;
            }
        }"""
        ast = ASTGenerator(source).generate()
        func = ast.decls[0]
        stmt = func.body.statements[0]
        assert isinstance(stmt, SwitchStmt)
        assert len(stmt.cases) == 2

    def test_switch_stmt_with_default(self):
        source = """void main() {
            switch (x) {
                case 1: break;
                default: break;
            }
        }"""
        ast = ASTGenerator(source).generate()
        func = ast.decls[0]
        stmt = func.body.statements[0]
        assert isinstance(stmt, SwitchStmt)
        assert stmt.default_case is not None

    def test_break_stmt(self):
        source = """void main() {
            break;
        }"""
        ast = ASTGenerator(source).generate()
        func = ast.decls[0]
        stmt = func.body.statements[0]
        assert isinstance(stmt, BreakStmt)

    def test_continue_stmt(self):
        source = """void main() {
            continue;
        }"""
        ast = ASTGenerator(source).generate()
        func = ast.decls[0]
        stmt = func.body.statements[0]
        assert isinstance(stmt, ContinueStmt)

    def test_return_stmt_no_value(self):
        source = """void main() {
            return;
        }"""
        ast = ASTGenerator(source).generate()
        func = ast.decls[0]
        stmt = func.body.statements[0]
        assert isinstance(stmt, ReturnStmt)
        assert stmt.expr is None

    def test_return_stmt_with_value(self):
        source = """void main() {
            return 5;
        }"""
        ast = ASTGenerator(source).generate()
        func = ast.decls[0]
        stmt = func.body.statements[0]
        assert isinstance(stmt, ReturnStmt)
        assert stmt.expr is not None


class TestExpressions:
    """Test expressions"""

    def test_binary_add(self):
        source = """void main() {
            int x = 1 + 2;
        }"""
        ast = ASTGenerator(source).generate()
        func = ast.decls[0]
        stmt = func.body.statements[0]
        assert isinstance(stmt, VarDecl)
        assert isinstance(stmt.init_value, BinaryOp)
        assert stmt.init_value.operator == "+"

    def test_binary_sub(self):
        source = """void main() {
            int x = 1 - 2;
        }"""
        ast = ASTGenerator(source).generate()
        stmt = ast.decls[0].body.statements[0]
        assert stmt.init_value.operator == "-"

    def test_binary_mul(self):
        source = """void main() {
            int x = 1 * 2;
        }"""
        ast = ASTGenerator(source).generate()
        stmt = ast.decls[0].body.statements[0]
        assert stmt.init_value.operator == "*"

    def test_binary_div(self):
        source = """void main() {
            int x = 1 / 2;
        }"""
        ast = ASTGenerator(source).generate()
        stmt = ast.decls[0].body.statements[0]
        assert stmt.init_value.operator == "/"

    def test_binary_mod(self):
        source = """void main() {
            int x = 1 % 2;
        }"""
        ast = ASTGenerator(source).generate()
        stmt = ast.decls[0].body.statements[0]
        assert stmt.init_value.operator == "%"

    def test_comparison_eq(self):
        source = """void main() {
            int x = 1 == 2;
        }"""
        ast = ASTGenerator(source).generate()
        stmt = ast.decls[0].body.statements[0]
        assert stmt.init_value.operator == "=="

    def test_comparison_neq(self):
        source = """void main() {
            int x = 1 != 2;
        }"""
        ast = ASTGenerator(source).generate()
        stmt = ast.decls[0].body.statements[0]
        assert stmt.init_value.operator == "!="

    def test_comparison_lt(self):
        source = """void main() {
            int x = 1 < 2;
        }"""
        ast = ASTGenerator(source).generate()
        stmt = ast.decls[0].body.statements[0]
        assert stmt.init_value.operator == "<"

    def test_comparison_le(self):
        source = """void main() {
            int x = 1 <= 2;
        }"""
        ast = ASTGenerator(source).generate()
        stmt = ast.decls[0].body.statements[0]
        assert stmt.init_value.operator == "<="

    def test_comparison_gt(self):
        source = """void main() {
            int x = 1 > 2;
        }"""
        ast = ASTGenerator(source).generate()
        stmt = ast.decls[0].body.statements[0]
        assert stmt.init_value.operator == ">"

    def test_comparison_ge(self):
        source = """void main() {
            int x = 1 >= 2;
        }"""
        ast = ASTGenerator(source).generate()
        stmt = ast.decls[0].body.statements[0]
        assert stmt.init_value.operator == ">="

    def test_logical_and(self):
        source = """void main() {
            int x = 1 && 2;
        }"""
        ast = ASTGenerator(source).generate()
        stmt = ast.decls[0].body.statements[0]
        assert stmt.init_value.operator == "&&"

    def test_logical_or(self):
        source = """void main() {
            int x = 1 || 2;
        }"""
        ast = ASTGenerator(source).generate()
        stmt = ast.decls[0].body.statements[0]
        assert stmt.init_value.operator == "||"

    def test_prefix_inc(self):
        source = """void main() {
            int x = ++y;
        }"""
        ast = ASTGenerator(source).generate()
        stmt = ast.decls[0].body.statements[0]
        assert isinstance(stmt.init_value, PrefixOp)
        assert stmt.init_value.operator == "++"

    def test_prefix_dec(self):
        source = """void main() {
            int x = --y;
        }"""
        ast = ASTGenerator(source).generate()
        stmt = ast.decls[0].body.statements[0]
        assert isinstance(stmt.init_value, PrefixOp)
        assert stmt.init_value.operator == "--"

    def test_prefix_not(self):
        source = """void main() {
            int x = !y;
        }"""
        ast = ASTGenerator(source).generate()
        stmt = ast.decls[0].body.statements[0]
        assert isinstance(stmt.init_value, PrefixOp)
        assert stmt.init_value.operator == "!"

    def test_prefix_minus(self):
        source = """void main() {
            int x = -y;
        }"""
        ast = ASTGenerator(source).generate()
        stmt = ast.decls[0].body.statements[0]
        assert isinstance(stmt.init_value, PrefixOp)
        assert stmt.init_value.operator == "-"

    def test_prefix_plus(self):
        source = """void main() {
            int x = +y;
        }"""
        ast = ASTGenerator(source).generate()
        stmt = ast.decls[0].body.statements[0]
        assert isinstance(stmt.init_value, PrefixOp)
        assert stmt.init_value.operator == "+"

    def test_postfix_inc(self):
        source = """void main() {
            int x = y++;
        }"""
        ast = ASTGenerator(source).generate()
        stmt = ast.decls[0].body.statements[0]
        assert isinstance(stmt.init_value, PostfixOp)
        assert stmt.init_value.operator == "++"

    def test_postfix_dec(self):
        source = """void main() {
            int x = y--;
        }"""
        ast = ASTGenerator(source).generate()
        stmt = ast.decls[0].body.statements[0]
        assert isinstance(stmt.init_value, PostfixOp)
        assert stmt.init_value.operator == "--"

    def test_assignment(self):
        source = """void main() {
            x = 5;
        }"""
        ast = ASTGenerator(source).generate()
        func = ast.decls[0]
        stmt = func.body.statements[0]
        assert isinstance(stmt, ExprStmt)
        assert isinstance(stmt.expr, AssignExpr)

    def test_function_call_no_args(self):
        source = """void main() {
            foo();
        }"""
        ast = ASTGenerator(source).generate()
        stmt = ast.decls[0].body.statements[0]
        assert isinstance(stmt, ExprStmt)
        assert isinstance(stmt.expr, FuncCall)
        assert len(stmt.expr.args) == 0

    def test_function_call_with_args(self):
        source = """void main() {
            foo(1, 2, 3);
        }"""
        ast = ASTGenerator(source).generate()
        stmt = ast.decls[0].body.statements[0]
        assert isinstance(stmt.expr, FuncCall)
        assert len(stmt.expr.args) == 3

    def test_member_access(self):
        source = """void main() {
            x.foo;
        }"""
        ast = ASTGenerator(source).generate()
        stmt = ast.decls[0].body.statements[0]
        assert isinstance(stmt.expr, MemberAccess)

    def test_nested_member_access(self):
        source = """void main() {
            x.foo.bar;
        }"""
        ast = ASTGenerator(source).generate()
        stmt = ast.decls[0].body.statements[0]
        assert isinstance(stmt.expr, MemberAccess)
        assert isinstance(stmt.expr.obj, MemberAccess)

    def test_identifier(self):
        source = """void main() {
            x;
        }"""
        ast = ASTGenerator(source).generate()
        stmt = ast.decls[0].body.statements[0]
        assert isinstance(stmt.expr, Identifier)

    def test_parenthesized_expr(self):
        source = """void main() {
            int x = (1 + 2);
        }"""
        ast = ASTGenerator(source).generate()
        stmt = ast.decls[0].body.statements[0]
        assert isinstance(stmt.init_value, BinaryOp)


class TestComplexExpressions:
    """Test complex expressions with precedence"""

    def test_precedence_mul_over_add(self):
        source = """void main() {
            int x = 1 + 2 * 3;
        }"""
        ast = ASTGenerator(source).generate()
        stmt = ast.decls[0].body.statements[0]
        # Should be 1 + (2 * 3), so root is BinaryOp with +
        assert stmt.init_value.operator == "+"
        assert stmt.init_value.right.operator == "*"

    def test_precedence_rel_over_eq(self):
        source = """void main() {
            int x = 1 + 2 == 3;
        }"""
        ast = ASTGenerator(source).generate()
        stmt = ast.decls[0].body.statements[0]
        # (1 + 2) == 3, so root is ==
        assert stmt.init_value.operator == "=="


class TestEdgeCases:
    """Test edge cases"""

    def test_multiple_statements_in_block(self):
        source = """void main() {
            int a;
            int b;
            int c;
        }"""
        ast = ASTGenerator(source).generate()
        func = ast.decls[0]
        assert len(func.body.statements) == 3

    def test_nested_if(self):
        source = """void main() {
            if (a) {
                if (b) {
                }
            }
        }"""
        ast = ASTGenerator(source).generate()
        stmt = ast.decls[0].body.statements[0]
        assert isinstance(stmt, IfStmt)
        assert isinstance(stmt.then_stmt, BlockStmt)
        assert isinstance(stmt.then_stmt.statements[0], IfStmt)

    def test_nested_while(self):
        source = """void main() {
            while (a) {
                while (b) {
                }
            }
        }"""
        ast = ASTGenerator(source).generate()
        stmt = ast.decls[0].body.statements[0]
        assert isinstance(stmt, WhileStmt)
        assert isinstance(stmt.body.statements[0], WhileStmt)

    def test_empty_function_body(self):
        source = """void main() {
        }"""
        ast = ASTGenerator(source).generate()
        func = ast.decls[0]
        assert isinstance(func.body, BlockStmt)
        assert len(func.body.statements) == 0

    def test_empty_switch_cases(self):
        source = """void main() {
            switch (x) {
            }
        }"""
        ast = ASTGenerator(source).generate()
        stmt = ast.decls[0].body.statements[0]
        assert isinstance(stmt, SwitchStmt)
        assert len(stmt.cases) == 0


class TestLineColumn:
    """Test line and column information"""

    def test_program_line_column(self):
        source = """void main() {
}"""
        ast = ASTGenerator(source).generate()
        assert ast.line is not None

    def test_func_decl_line_column(self):
        source = """void main() {
}"""
        ast = ASTGenerator(source).generate()
        func = ast.decls[0]
        assert func.line is not None


class TestAutoFunction:
    """Test auto return type function"""

    def test_auto_return_function(self):
        source = """main() {
}"""
        ast = ASTGenerator(source).generate()
        func = ast.decls[0]
        assert func.return_type is None


class TestVarDeclInSwitch:
    """Test variable declaration in switch case"""

    def test_var_decl_in_case(self):
        source = """void main() {
    switch (x) {
        case 1:
            int a;
            break;
    }
}"""
        ast = ASTGenerator(source).generate()
        switch_stmt = ast.decls[0].body.statements[0]
        case_stmt = switch_stmt.cases[0]
        assert len(case_stmt.statements) == 2
        assert isinstance(case_stmt.statements[0], VarDecl)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
