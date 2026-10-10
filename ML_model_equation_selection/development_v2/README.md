# Label audit

Changing packed-weight identifiers to explicit integral indices did not resolve the low match rate. Source inspection then found that Coeff_int has an empty default constructor. The support accumulator used default values without initializing them to zero. The next implementation initializes every coefficient explicitly and repeats collection checks. These records do not supply final training labels.
