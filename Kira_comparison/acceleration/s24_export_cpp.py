"""Write exact float32 row weights as C++ constants."""
import json,pathlib,numpy as np
HERE=pathlib.Path(__file__).resolve().parent
with np.load(HERE/"row_weights.npz",allow_pickle=False) as data:weights={k:data[k] for k in data.files}
assert weights["encoder.0.weight"].shape==(32,132)
lines=["// Frozen trained row weights; exported float32 values.","#pragma once","namespace kira_row_weights {",
 "inline constexpr unsigned score_hidden=%d;"%weights["scorer.0.weight"].shape[0]]
for key,array in sorted(weights.items()):
 values=[]
 for value in array.ravel():
  s=format(float(value),".9g")
  if "." not in s and "e" not in s:s+=".0"
  values.append(s+"f")
 lines.append("inline constexpr float "+key.replace(".","_")+"[]={"+",".join(values)+"};")
lines.append("}")
(HERE/"s24_row_weights.h").write_text("\n".join(lines)+"\n")
print("C++ weights exported")
