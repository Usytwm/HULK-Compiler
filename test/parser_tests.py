from ..src.LR1Parser import LR1Parser, table_to_dataframe
from ..src.grammar.grammar import define_hulk_grammar
from pandas import DataFrame




G = define_hulk_grammar
parser = LR1Parser(G)

display(table_to_dataframe(parser.action))
display(table_to_dataframe(parser.goto))