# Independent symbolic kinematics

families.json contains a nonplanar box in Q(d,s,t), a pentagon in Q(d,s12,s23,s34,s45,s51), and a one-loop box in Q(d,s,t,q2). Here q2 is the squared momentum of the one off-shell external leg. All internal masses are zero. No scale is replaced by one.

The native adapter now declares every invariant in Kira's kinematics input. Reference and test files in ../references/ and ../model_test/ retain exact symbolic coefficients, their masters and input files. ../verification.json records the symbols actually present, equality at larger seed bounds, and separate native checks after fresh rational specializations. Rational-function equality supplies the primary comparison.

The seven-batch timing study retains all failures and fallback costs. These finite target lists do not establish performance for arbitrary masses, higher numerator ranks, or general high-loop scattering. Use ../README.md for execution and resource limits.
