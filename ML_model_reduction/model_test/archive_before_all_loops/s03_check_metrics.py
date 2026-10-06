"""Independent analytical checks before evaluating held-out families."""
from s00_test_common import *
def main():
    assert coefficient("(d-4)/(2*s)",{"d":9,"s":3},101)==5*pow(6,-1,101)%101
    assert coefficient("s**(-2)",{"s":3},101)==pow(9,-1,101)
    assert eval_terms([dict(indices=[1],coefficient="s"),dict(indices=[1],coefficient="-s")],{"s":3},101)=={}
    try:coefficient("__import__('os').system('false')",{},101)
    except ValueError:pass
    else:raise AssertionError("Unsafe expression accepted")
    try:coefficient("1/s",{"s":0},101)
    except ZeroDivisionError:pass
    else:raise AssertionError("Singular point accepted")
    r=classify([.25,.5,.25],0,["a","b","c"])
    assert r["predicted"]==1 and r["rank"]==2
    assert abs(r["brier"]-.875)<1e-12 and abs(r["nll"]-math.log(4))<1e-12
    tie=classify([.5,.5],0,["z","a"]);assert tie["predicted"]==1 and tie["rank"]==2
    bins=reliability([.6,.6,1.0],[1,0,1])
    assert bins[0]["reference_accuracy"]==.5 and bins[0]["mean_confidence"]==.6
    assert bins[-1]["reference_accuracy"]==1 and bins[-1]["count"]==1
    assert classify([1.],0,["only"])["brier"]==0
    write_json(TEST/"metric_checks.json",dict(status="passed",rational_field_evaluation=True,
        unsafe_syntax_rejected=True,singular_points_rejected=True,known_brier_and_log_loss=True,
        stable_tie_ranking=True,reliability_bins=True,forced_case=True))
    print("Analytical metric and field checks passed",flush=True)
if __name__=="__main__":main()
