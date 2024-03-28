from src.syntax_analysis.grammar_LR1 import gramm_Hulk_LR1
from src.syntax_analysis.LR1Parser import LR1Parser
from src.lexical_analysis.lexer import Lexer
from pathlib import Path
from cmp.cil import PrintVisitor
import typer


def report_and_exit(errors):
    if len(errors) == 0:
        raise typer.Exit(code=0)

    # typer.echo(errors[0])
    for error in errors:
        typer.echo(error)
    raise typer.Exit(code=1)


def pipeline(input_file: Path, output_file: Path = None):
    errors = []

    if not input_file.is_file:
        pass

    if len(errors) > 0:
        report_and_exit(errors)

    text = input_file.read_text()

    # define grammar
    grammar, idx, type_id, string, num = gramm_Hulk_LR1()

    tokens = Lexer(grammar, idx, type_id, string, num, text, errors)

    if len(errors) > 0:
        report_and_exit(errors)
    parser = LR1Parser(grammar, errors)

    if len(errors) > 0:
        report_and_exit(errors)

    parse, operations = parser(tokens)

    if len(errors) > 0:
        report_and_exit(errors)

    """""
    # print("-------------------------------Initial AST-------------------------------")
    # formatter = FormatVisitorST()
    # tree = formatter.visit(ast)
    # print(tree)

    visitors = [TypeCollector(errors), TypeBuilder(errors)]
    for visitor in visitors:
        ast = visitor.visit(ast)

    type_checker = TypeChecker(errors)
    scope, typed_ast = type_checker.visit(ast)

    # formatter = FormatVisitorTypedAst()
    # print("-------------------------------Typed AST-------------------------------")
    # tree = formatter.visit(typed_ast)
    # print(tree)

    
    """""

if __name__ == "__main__":
    #input_file = Path("...")
    #output_file =  Path("...")

    #pipeline()
    typer.run(pipeline)