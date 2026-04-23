"""
Test cases for TyC Static Semantic Checker

This module contains 100 test cases for the static semantic checker
covering all 8 error types and comprehensive valid program scenarios.
"""

from tests.utils import Checker
from src.utils.nodes import (
    Program,
    FuncDecl,
    BlockStmt,
    VarDecl,
    AssignExpr,
    ExprStmt,
    IntType,
    FloatType,
    StringType,
    VoidType,
    StructType,
    IntLiteral,
    FloatLiteral,
    StringLiteral,
    Identifier,
    BinaryOp,
    MemberAccess,
    FuncCall,
    StructDecl,
    MemberDecl,
    Param,
    ReturnStmt,
    PrefixOp,
    PostfixOp,
    WhileStmt,
    ForStmt,
    IfStmt,
    BreakStmt,
    ContinueStmt,
    SwitchStmt,
    CaseStmt,
    DefaultStmt,
    StructLiteral,
)


# ============================================================================
# Valid Programs (test_001 - test_015)
# ============================================================================


def test_001():
    """Test a valid program that should pass all checks"""
    source = """
void main() {
    int x = 5;
    int y = x + 1;
}
"""
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected


def test_002():
    """Test valid program with auto type inference"""
    source = """
void main() {
    auto x = 10;
    auto y = 3.14;
    auto z = x + y;
}
"""
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected


def test_003():
    """Test valid program with functions"""
    source = """
int add(int x, int y) {
    return x + y;
}
void main() {
    int sum = add(5, 3);
}
"""
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected


def test_004():
    """Test valid program with struct"""
    source = """
struct Point {
    int x;
    int y;
};
void main() {
    Point p;
    p.x = 10;
    p.y = 20;
}
"""
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected


def test_005():
    """Test valid program with nested blocks"""
    source = """
void main() {
    int x = 10;
    {
        int y = 20;
        int z = x + y;
    }
}
"""
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected


def test_006():
    """Test valid program with while loop"""
    source = """
void main() {
    int i = 0;
    while (i < 10) {
        i = i + 1;
    }
}
"""
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected


def test_007():
    """Test valid program with for loop"""
    source = """
void main() {
    int sum = 0;
    for (int i = 0; i < 10; i = i + 1) {
        sum = sum + i;
    }
}
"""
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected


def test_008():
    """Test valid program with if-else"""
    source = """
void main() {
    int x = 5;
    if (x > 0) {
        x = 10;
    } else {
        x = 0;
    }
}
"""
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected


def test_009():
    """Test valid program with switch statement"""
    source = """
void main() {
    int day = 3;
    switch (day) {
        case 1: printInt(1); break;
        case 2: printInt(2); break;
        default: printInt(0);
    }
}
"""
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected


def test_010():
    """Test valid program with auto inferred from first use"""
    source = """
void main() {
    auto a;
    a = 42;
    printInt(a);
}
"""
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected


def test_011():
    """Test valid program with built-in functions"""
    source = """
void main() {
    int x = readInt();
    printInt(x);
    float f = readFloat();
    printFloat(f);
    string s = readString();
    printString(s);
}
"""
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected


def test_012():
    """Test valid program with nested struct"""
    source = """
struct Inner {
    int value;
};
struct Outer {
    Inner nested;
    int id;
};
void main() {
    Outer o;
    o.id = 1;
}
"""
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected


def test_013():
    """Test valid program with break and continue in loop"""
    source = """
void main() {
    int i = 0;
    while (i < 10) {
        i = i + 1;
        if (i == 5) {
            continue;
        }
        if (i == 9) {
            break;
        }
        printInt(i);
    }
}
"""
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected


def test_014():
    """Test valid program with prefix and postfix increment"""
    source = """
void main() {
    int x = 0;
    ++x;
    x++;
    --x;
    x--;
    printInt(x);
}
"""
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected


def test_015():
    """Test valid program with struct and member access"""
    source = """
struct Point {
    int x;
    int y;
};
void main() {
    Point p;
    p.x = 10;
    p.y = 20;
    printInt(p.x);
    printInt(p.y);
}
"""
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected


# ============================================================================
# Redeclared Error Tests (test_016 - test_030)
# ============================================================================


def test_016():
    """Redeclared Struct"""
    source = """
struct Point {
    int x;
    int y;
};
struct Point {
    int z;
};
void main() {}
"""
    Checker(source).check_from_source()
    result = Checker(source).check_from_source()
    assert "Redeclared(Struct, Point)" in result


def test_017():
    """Redeclared Function"""
    source = """
int add(int x, int y) {
    return x + y;
}
int add(int a, int b) {
    return a + b;
}
void main() {}
"""
    result = Checker(source).check_from_source()
    assert "Redeclared(Function, add)" in result


def test_018():
    """Redeclared Variable in same block"""
    source = """
void main() {
    int count = 10;
    int count = 20;
}
"""
    result = Checker(source).check_from_source()
    assert "Redeclared(Variable, count)" in result


def test_019():
    """Redeclared Parameter in same parameter list"""
    source = """
int calculate(int x, float y, int x) {
    return x + y;
}
void main() {}
"""
    result = Checker(source).check_from_source()
    assert "Redeclared(Parameter, x)" in result


def test_020():
    """Redeclared Variable: local variable reuses parameter name"""
    source = """
void func(int x) {
    int x = 10;
}
void main() {}
"""
    result = Checker(source).check_from_source()
    assert "Redeclared(Variable, x)" in result


def test_021():
    """Redeclared Variable: local variable reuses parameter name in nested block"""
    source = """
void func(int x) {
    {
        int x = 10;
    }
}
void main() {}
"""
    result = Checker(source).check_from_source()
    assert "Redeclared(Variable, x)" in result


def test_022():
    """Redeclared Member in same struct"""
    source = """
struct Point {
    int x;
    int x;
};
void main() {}
"""
    result = Checker(source).check_from_source()
    assert "Redeclared(Member, x)" in result


def test_023():
    """Redeclared Variable across different blocks in same function (valid)"""
    source = """
void main() {
    int x = 10;
    {
        int y = 20;
    }
    int y = 30;
}
"""
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected


def test_024():
    """Shadowing outer local variable in nested block is allowed in TyC"""
    source = """
void main() {
    int value = 100;
    {
        int value = 200;
    }
}
"""
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected


def test_025():
    """Redeclared Variable: same name in nested block shadows outer local (valid)"""
    source = """
void main() {
    int x = 10;
    {
        int x = 20;
    }
}
"""
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected


def test_026():
    """Redeclared Variable: in same block (second occurrence)"""
    source = """
void main() {
    int a = 1;
    int b = 2;
    int a = 3;
}
"""
    result = Checker(source).check_from_source()
    assert "Redeclared(Variable, a)" in result


def test_027():
    """Redeclared Variable: for-loop init declares same name"""
    source = """
void main() {
    int i = 0;
    for (int i = 0; i < 10; i = i + 1) {
    }
}
"""
    result = Checker(source).check_from_source()
    assert "Redeclared(Variable, i)" in result


def test_028():
    """Shadowing in while loop body (creates its own block scope) is allowed"""
    source = """
void main() {
    int x = 0;
    while (x < 10) {
        int x = 5;
        x = x + 1;
    }
}
"""
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected


def test_029():
    """Redeclared Variable: multiple parameters same name"""
    source = """
void test(int a, int a) {}
void main() {}
"""
    result = Checker(source).check_from_source()
    assert "Redeclared(Parameter, a)" in result


def test_030():
    """Redeclared Variable: if body redeclares parameter"""
    source = """
void func(int z) {
    if (1) {
        int z = 5;
    }
}
void main() {}
"""
    result = Checker(source).check_from_source()
    assert "Redeclared(Variable, z)" in result


# ============================================================================
# UndeclaredIdentifier Error Tests (test_031 - test_040)
# ============================================================================


def test_031():
    """UndeclaredIdentifier: variable used without declaration"""
    source = """
void main() {
    int result = undeclaredVar + 10;
}
"""
    result = Checker(source).check_from_source()
    assert "UndeclaredIdentifier(undeclaredVar)" in result


def test_032():
    """UndeclaredIdentifier: variable used before declaration in same scope"""
    source = """
void main() {
    int x = y + 5;
    int y = 10;
}
"""
    result = Checker(source).check_from_source()
    assert "UndeclaredIdentifier(y)" in result


def test_033():
    """UndeclaredIdentifier: out-of-scope access"""
    source = """
void method1() {
    int localVar = 42;
}
void method2() {
    int value = localVar + 1;
}
"""
    result = Checker(source).check_from_source()
    assert "UndeclaredIdentifier(localVar)" in result


def test_034():
    """UndeclaredIdentifier: variable used in a different function (separate scope)"""
    source = """
void caller() {
    printInt(x);
}
void main() {}
"""
    result = Checker(source).check_from_source()
    assert "UndeclaredIdentifier(x)" in result


def test_035():
    """UndeclaredIdentifier: parameter used in function body"""
    source = """
int compute(int a, int b) {
    return a + b + c;
}
void main() {}
"""
    result = Checker(source).check_from_source()
    assert "UndeclaredIdentifier(c)" in result


def test_036():
    """UndeclaredIdentifier: variable used in different function"""
    source = """
void caller() {
    int a = undefVar + 1;
}
void main() {}
"""
    result = Checker(source).check_from_source()
    assert "UndeclaredIdentifier(undefVar)" in result


def test_037():
    """UndeclaredIdentifier: variable in while loop condition"""
    source = """
void main() {
    while (unknownVar < 10) {
        unknownVar = unknownVar + 1;
    }
}
"""
    result = Checker(source).check_from_source()
    assert "UndeclaredIdentifier(unknownVar)" in result


def test_038():
    """UndeclaredIdentifier: variable in for init"""
    source = """
void main() {
    for (int i = undeclared; i < 10; i = i + 1) {
    }
}
"""
    result = Checker(source).check_from_source()
    assert "UndeclaredIdentifier(undeclared)" in result


def test_039():
    """UndeclaredIdentifier: variable in if condition"""
    source = """
void main() {
    if (undefVar > 0) {
    }
}
"""
    result = Checker(source).check_from_source()
    assert "UndeclaredIdentifier(undefVar)" in result


def test_040():
    """UndeclaredIdentifier: variable after assignment (valid)"""
    source = """
void main() {
    int a = 5;
    int b = a + 10;
}
"""
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected


# ============================================================================
# UndeclaredFunction Error Tests (test_041 - test_045)
# ============================================================================


def test_041():
    """UndeclaredFunction: called without declaration"""
    source = """
void main() {
    int result = calculate(5, 3);
}
"""
    result = Checker(source).check_from_source()
    assert "UndeclaredFunction(calculate)" in result


def test_042():
    """UndeclaredFunction: function called that doesn't exist"""
    source = """
void test() {
    int value = nonexistent(10, 20);
}
void main() {}
"""
    result = Checker(source).check_from_source()
    assert "UndeclaredFunction(nonexistent)" in result


def test_043():
    """UndeclaredFunction: nested call to undeclared function"""
    source = """
int caller() {
    return helper();
}
void main() {}
"""
    result = Checker(source).check_from_source()
    assert "UndeclaredFunction(helper)" in result


def test_044():
    """UndeclaredFunction: function with wrong number of arguments"""
    source = """
int multiply(int x, int y) {
    return x * y;
}
void main() {
    int result = multiply(5);
}
"""
    result = Checker(source).check_from_source()
    assert "TypeMismatchInExpression" in result


def test_045():
    """UndeclaredFunction: built-in functions are valid"""
    source = """
void main() {
    int x = readInt();
    printInt(x);
}
"""
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected


# ============================================================================
# UndeclaredStruct Error Tests (test_046 - test_050)
# ============================================================================


def test_046():
    """UndeclaredStruct: struct type never declared at all"""
    source = """
void main() {
    Point p;
}
"""
    result = Checker(source).check_from_source()
    assert "UndeclaredStruct(Point)" in result


def test_048():
    """UndeclaredStruct: struct type never declared"""
    source = """
void test() {
    UnknownType var;
}
void main() {}
"""
    result = Checker(source).check_from_source()
    assert "UndeclaredStruct(UnknownType)" in result


def test_047():
    """Struct member with forward struct reference (valid in TyC)"""
    source = """
struct Address {
    string street;
    City city;
};
struct City {
    string name;
};
void main() {}
"""
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected


def test_048():
    """Struct used before declaration in function (valid in TyC)"""
    source = """
void test() {
    Person person;
}
struct Person {
    string name;
    int age;
};
void main() {}
"""
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected


def test_049():
    """UndeclaredStruct: variable with undeclared struct type"""
    source = """
void main() {
    UnknownType var;
}
"""
    result = Checker(source).check_from_source()
    assert "UndeclaredStruct(UnknownType)" in result


def test_050():
    """UndeclaredStruct: struct type never declared"""
    source = """
void main() {
    StructXYZ s;
}
"""
    result = Checker(source).check_from_source()
    assert "UndeclaredStruct(StructXYZ)" in result


# ============================================================================
# TypeCannotBeInferred Error Tests (test_051 - test_062)
# ============================================================================


def test_051():
    """TypeCannotBeInferred: two auto variables used in expression without init"""
    source = """
void main() {
    auto x;
    auto y;
    auto result = x + y;
}
"""
    result = Checker(source).check_from_source()
    assert "TypeCannotBeInferred" in result


def test_052():
    """TypeCannotBeInferred: assignment between two unresolved autos"""
    source = """
void main() {
    auto x;
    auto y;
    x = y;
}
"""
    result = Checker(source).check_from_source()
    assert "TypeCannotBeInferred" in result


def test_053():
    """TypeCannotBeInferred: auto variable never used"""
    source = """
void main() {
    auto x;
}
"""
    result = Checker(source).check_from_source()
    assert "TypeCannotBeInferred" in result


def test_054():
    """TypeCannotBeInferred: auto used in return without inference"""
    source = """
int getValue() {
    auto x;
    return x;
}
void main() {}
"""
    result = Checker(source).check_from_source()
    assert "TypeCannotBeInferred" in result


def test_055():
    """TypeCannotBeInferred: auto in comparison"""
    source = """
void main() {
    auto x;
    auto y;
    int result = x < y;
}
"""
    result = Checker(source).check_from_source()
    assert "TypeCannotBeInferred" in result


def test_056():
    """TypeCannotBeInferred: auto in multiplication"""
    source = """
void main() {
    auto a;
    auto b;
    int c = a * b;
}
"""
    result = Checker(source).check_from_source()
    assert "TypeCannotBeInferred" in result


def test_057():
    """TypeCannotBeInferred: two unresolved autos in multiplication"""
    source = """
void main() {
    auto a;
    auto b;
    auto c = a + b;
}
"""
    result = Checker(source).check_from_source()
    assert "TypeCannotBeInferred" in result


def test_058():
    """TypeCannotBeInferred: auto variable in binary op with unknown"""
    source = """
void main() {
    auto x;
    auto y;
    auto z = x * y;
}
"""
    result = Checker(source).check_from_source()
    assert "TypeCannotBeInferred" in result


def test_059():
    """TypeCannotBeInferred: auto assigned to auto (mutual dependency)"""
    source = """
void main() {
    auto a;
    auto b;
    a = b;
}
"""
    result = Checker(source).check_from_source()
    assert "TypeCannotBeInferred" in result


def test_060():
    """TypeCannotBeInferred: two unresolved autos in while condition"""
    source = """
void main() {
    auto x;
    auto y;
    while (x < y) {
        x = x + 1;
    }
}
"""
    result = Checker(source).check_from_source()
    assert "TypeCannotBeInferred" in result


def test_061():
    """TypeMismatchInStatement: auto var assigned to incompatible type"""
    source = """
void main() {
    auto x = 10;
    x = "text";
}
"""
    result = Checker(source).check_from_source()
    assert "TypeMismatchInStatement" in result


def test_062():
    """TypeCannotBeInferred: unused auto in block"""
    source = """
void main() {
    auto a;
    auto b = 10;
}
"""
    result = Checker(source).check_from_source()
    assert "TypeCannotBeInferred" in result


# ============================================================================
# TypeMismatchInStatement Error Tests (test_063 - test_075)
# ============================================================================


def test_063():
    """TypeMismatchInStatement: non-int condition in if"""
    source = """
void main() {
    float x = 5.0;
    if (x) {
        printInt(1);
    }
}
"""
    result = Checker(source).check_from_source()
    assert "TypeMismatchInStatement" in result


def test_064():
    """TypeMismatchInStatement: non-int condition in while"""
    source = """
void main() {
    float f = 1.5;
    while (f) {
        printFloat(f);
    }
}
"""
    result = Checker(source).check_from_source()
    assert "TypeMismatchInStatement" in result


def test_065():
    """TypeMismatchInStatement: assignment type mismatch"""
    source = """
void main() {
    int x = 10;
    string text = "hello";
    x = text;
}
"""
    result = Checker(source).check_from_source()
    assert "TypeMismatchInStatement" in result


def test_066():
    """TypeMismatchInStatement: assignment string to int"""
    source = """
void main() {
    int x = 10;
    x = "text";
}
"""
    result = Checker(source).check_from_source()
    assert "TypeMismatchInStatement" in result


def test_067():
    """TypeMismatchInStatement: assignment float to int (no coercion)"""
    source = """
void main() {
    int x = 10;
    float f = 3.14;
    x = f;
}
"""
    result = Checker(source).check_from_source()
    assert "TypeMismatchInStatement" in result


def test_068():
    """TypeMismatchInStatement: struct assignment type mismatch"""
    source = """
struct Point {
    int x;
    int y;
};
struct Person {
    string name;
    int age;
};
void main() {
    Point p;
    Person person;
    p = person;
}
"""
    result = Checker(source).check_from_source()
    assert "TypeMismatchInStatement" in result


def test_069():
    """TypeMismatchInStatement: return type mismatch"""
    source = """
int getValue() {
    return "invalid";
}
void main() {}
"""
    result = Checker(source).check_from_source()
    assert "TypeMismatchInStatement" in result


def test_070():
    """TypeMismatchInStatement: return string as int"""
    source = """
string getText() {
    return 42;
}
void main() {}
"""
    result = Checker(source).check_from_source()
    assert "TypeMismatchInStatement" in result


def test_071():
    """TypeMismatchInStatement: void function returns value"""
    source = """
void returnError() {
    return 10;
}
void main() {}
"""
    result = Checker(source).check_from_source()
    assert "TypeMismatchInStatement" in result


def test_072():
    """TypeMismatchInStatement: non-void function returns void"""
    source = """
int returnVoidError() {
    return;
}
void main() {}
"""
    result = Checker(source).check_from_source()
    assert "TypeMismatchInStatement" in result


def test_073():
    """TypeMismatchInStatement: switch expression type mismatch"""
    source = """
void main() {
    float f = 3.14;
    switch (f) {
        case 1: break;
    }
}
"""
    result = Checker(source).check_from_source()
    assert "TypeMismatchInStatement" in result


def test_074():
    """TypeMismatchInStatement: condition in for loop non-int"""
    source = """
void main() {
    float flag = 1.0;
    for (int i = 0; flag; i = i + 1) {
        i = i + 1;
    }
}
"""
    result = Checker(source).check_from_source()
    assert "TypeMismatchInStatement" in result


def test_075():
    """TypeMismatchInStatement: auto assigned to incompatible type"""
    source = """
void main() {
    auto x = 10;
    x = "text";
}
"""
    result = Checker(source).check_from_source()
    assert "TypeMismatchInStatement" in result


# ============================================================================
# TypeMismatchInExpression Error Tests (test_076 - test_088)
# ============================================================================


def test_076():
    """TypeMismatchInExpression: arithmetic with string"""
    source = """
void main() {
    int x = 5;
    string text = "hello";
    int sum = x + text;
}
"""
    result = Checker(source).check_from_source()
    assert "TypeMismatchInExpression" in result


def test_077():
    """TypeMismatchInExpression: modulus with float"""
    source = """
void main() {
    float f = 3.14;
    int x = 10;
    int result = f % x;
}
"""
    result = Checker(source).check_from_source()
    assert "TypeMismatchInExpression" in result


def test_078():
    """TypeMismatchInExpression: relational with string"""
    source = """
void main() {
    int x = 10;
    string text = "hello";
    int result = x < text;
}
"""
    result = Checker(source).check_from_source()
    assert "TypeMismatchInExpression" in result


def test_079():
    """TypeMismatchInExpression: logical and with float"""
    source = """
void main() {
    float f = 3.14;
    int x = 10;
    int result = f && x;
}
"""
    result = Checker(source).check_from_source()
    assert "TypeMismatchInExpression" in result


def test_080():
    """TypeMismatchInExpression: logical not on float"""
    source = """
void main() {
    float f = 3.14;
    int not = !f;
}
"""
    result = Checker(source).check_from_source()
    assert "TypeMismatchInExpression" in result


def test_081():
    """TypeMismatchInExpression: increment on float"""
    source = """
void main() {
    float f = 3.14;
    ++f;
}
"""
    result = Checker(source).check_from_source()
    assert "TypeMismatchInExpression" in result


def test_082():
    """TypeMismatchInExpression: postfix increment on float"""
    source = """
void main() {
    float f = 3.14;
    f++;
}
"""
    result = Checker(source).check_from_source()
    assert "TypeMismatchInExpression" in result


def test_083():
    """TypeMismatchInExpression: increment on literal"""
    source = """
void main() {
    int x = ++5;
}
"""
    result = Checker(source).check_from_source()
    assert "TypeMismatchInExpression" in result


def test_084():
    """TypeMismatchInExpression: member access on int"""
    source = """
void main() {
    int x = 10;
    int value = x.member;
}
"""
    result = Checker(source).check_from_source()
    assert "TypeMismatchInExpression" in result


def test_085():
    """TypeMismatchInExpression: member access on non-existent member"""
    source = """
struct Point {
    int x;
    int y;
};
void main() {
    Point p;
    int invalid = p.z;
}
"""
    result = Checker(source).check_from_source()
    assert "TypeMismatchInExpression" in result


def test_086():
    """TypeMismatchInExpression: function call wrong number of arguments"""
    source = """
int add(int x, int y) {
    return x + y;
}
void main() {
    int result = add(10);
}
"""
    result = Checker(source).check_from_source()
    assert "TypeMismatchInExpression" in result


def test_087():
    """TypeMismatchInExpression: function call argument type mismatch"""
    source = """
void process(int x) {}
void main() {
    string text = "123";
    process(text);
}
"""
    result = Checker(source).check_from_source()
    assert "TypeMismatchInExpression" in result


def test_088():
    """TypeMismatchInExpression: assignment expression with invalid LHS"""
    source = """
void main() {
    int x = (5 = x) + 3;
}
"""
    result = Checker(source).check_from_source()
    assert "TypeMismatchInExpression" in result


# ============================================================================
# MustInLoop Error Tests (test_089 - test_100)
# ============================================================================


def test_089():
    """MustInLoop: break outside loop"""
    source = """
void main() {
    break;
}
"""
    result = Checker(source).check_from_source()
    assert "MustInLoop" in result


def test_090():
    """MustInLoop: continue outside loop"""
    source = """
void main() {
    continue;
}
"""
    result = Checker(source).check_from_source()
    assert "MustInLoop" in result


def test_091():
    """MustInLoop: break in if without loop"""
    source = """
void main() {
    if (1) {
        break;
    }
}
"""
    result = Checker(source).check_from_source()
    assert "MustInLoop" in result


def test_092():
    """MustInLoop: continue in if without loop"""
    source = """
void main() {
    if (1) {
        continue;
    }
}
"""
    result = Checker(source).check_from_source()
    assert "MustInLoop" in result


def test_093():
    """MustInLoop: continue in switch (not allowed)"""
    source = """
void main() {
    int x = 1;
    switch (x) {
        case 1:
            continue;
            break;
    }
}
"""
    result = Checker(source).check_from_source()
    assert "MustInLoop" in result


def test_094():
    """MustInLoop: break/continue in helper function called from loop"""
    source = """
void helperMethod() {
    break;
}
void main() {
    for (int i = 0; i < 10; i = i + 1) {
        helperMethod();
    }
}
"""
    result = Checker(source).check_from_source()
    assert "MustInLoop" in result


def test_095():
    """MustInLoop: continue in helper function called from loop"""
    source = """
void helperMethod() {
    continue;
}
void main() {
    int i = 0;
    while (i < 10) {
        helperMethod();
        i = i + 1;
    }
}
"""
    result = Checker(source).check_from_source()
    assert "MustInLoop" in result


def test_096():
    """MustInLoop: break in nested if inside loop is valid"""
    source = """
void main() {
    for (int i = 0; i < 10; i = i + 1) {
        if (i == 5) {
            break;
        }
    }
}
"""
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected


def test_097():
    """MustInLoop: continue in nested if inside loop is valid"""
    source = """
void main() {
    for (int i = 0; i < 10; i = i + 1) {
        if (i % 2 == 0) {
            continue;
        }
        printInt(i);
    }
}
"""
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected


def test_098():
    """MustInLoop: break in switch is valid"""
    source = """
void main() {
    int day = 2;
    switch (day) {
        case 1: printInt(1); break;
        case 2: printInt(2); break;
        default: printInt(0);
    }
}
"""
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected


def test_099():
    """MustInLoop: break in nested loops"""
    source = """
void main() {
    for (int i = 0; i < 5; i = i + 1) {
        for (int j = 0; j < 5; j = j + 1) {
            if (j > 3) {
                break;
            }
        }
    }
}
"""
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected


def test_100():
    """MustInLoop: continue in nested loops"""
    source = """
void main() {
    for (int i = 0; i < 5; i = i + 1) {
        for (int j = 0; j < 5; j = j + 1) {
            if (i == j) {
                continue;
            }
            printInt(i);
        }
    }
}
"""
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected
