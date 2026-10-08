"""Check the large-expression reader against the archived independent evaluator."""
import importlib.util,random
from s02_common import *
from s22_coefficient_reader import modular,validate_output
spec=importlib.util.spec_from_file_location("reader_before_revision",HERE/"archive_span_reader_v1/s08_verify.py")
previous=importlib.util.module_from_spec(spec);spec.loader.exec_module(previous)
rng=random.Random(941)
expressions=["-x**2","(-x)**2","x**-2","x/-x","1+2*3","-x**-2","(x+1)/(x-1)"]
for _ in range(300):
 a,b,c=[rng.randint(1,8) for i in range(3)]
 expressions.append(f"(-{a}*x**{b}+{c})/({a}+x**-{c})")
for expression in expressions:
 assert modular(expression,{"x":11},1000003)==previous.evaluate(expression,(("x",11),),1000003),expression
large="+".join(["2*x**2"]*25000)
assert len(large)>131072 and modular(large,{"x":11},1000003)==25000*2*121%1000003
bad=["x.__class__","__import__(x)","x(x)","x**x","x+","(x","x//2","1"*2097153]
for expression in bad:
 try:validate_output(expression)
 except (ValueError,KeyError):pass
 else:raise AssertionError("Invalid syntax was accepted")
write(HERE/"reader_validation.json",dict(passed=True,small_expressions_compared=len(expressions),
 large_coefficient_characters=len(large),invalid_syntax_or_size_rejected=len(bad),
 reader_sha256=sha(HERE/"s22_coefficient_reader.py"),validator_sha256=sha(Path(__file__))))
print("Coefficient reader checks passed.")
