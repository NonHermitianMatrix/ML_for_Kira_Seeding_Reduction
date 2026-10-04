# Project rules

## Instruction priority and maintenance

- Follow the user's latest instructions first, then the rules in this file, subject to mandatory system and developer instructions.
- Record new project rules here whenever the user states them. If a new rule contradicts an existing rule, update the existing rule to reflect the user's latest instructions instead of retaining conflicting rules.
- Read this file before project work and keep it current.

## Scope and autonomous execution

- Only do what the user explicitly requests. Do not expand the scope or begin project implementation, experiments, training, or benchmarks without an explicit instruction.
- A request to create report files authorizes creating those files and rendering the requested PDF; it does not authorize starting the research project.
- Do not ask the user for permission. Perform necessary steps within the explicitly requested scope automatically, subject to applicable system and developer constraints.
- Treat the project as a physics and mathematics problem. Formulate explanations and proposed methods through Feynman integral families, sectors, master integrals, and their algebraic identities. Keep the physical and mathematical structure central when discussing data generation, reductions, and minimality; use computational methods as tools for this formulation and avoid reframing the discussion as a generic computer science problem.

## Resource safeguards

- Always protect the system from running out of RAM or filling storage.
- The user reports only 20 GB of available storage. Use no more than 10 GB (10,000,000,000 bytes) in total for this project's files, tools, dependencies, caches, logs, outputs, and temporary files, including any stored outside the project directory. This is a ceiling, not a storage target; use substantially less whenever possible.
- Check available RAM and disk space before resource-intensive work, and monitor usage during that work.
- Bound concurrency, memory use, and output size; use small trials before scaling up expensive computations.
- Keep headroom for the operating system and other workloads. Pause, reduce, or stop project jobs before resource exhaustion, and manage project-generated temporary files without deleting valuable user data.

## Working directory

- Perform project work on Hoffman in `/u/home/r/rushil/ML_for_Kira_Seeding_Reduction`, accessed as `rushil@hoffman2.idre.ucla.edu`.
- The original local folder is /home/physics/projects/ML_for_Kira_SeedReduction. The Hoffman copy is the primary working directory. Keep all newly generated data on Hoffman and GitHub only; do not download generated datasets or their temporary copies to the local machine. Use the local environment to connect and inspect tool output.
- Keep the Hoffman working copy linked to `git@github.com:NonHermitianMatrix/ML_for_Kira_Seeding_Reduction.git` so the user can monitor committed project files and their structure.
- Preserve the complete local project copy on Hoffman, including hidden tool and cache files. Keep tool binaries, caches and build logs outside Git history, and never store credentials in project files or commits.
- The initial 16-family master and target collection is complete. The authorized stage is to expand to 1,000 distinct families, identify more masters, construct and validate more targets with seed and elimination records, update the report PDF, and publish all generated data to GitHub. Complete this stage before stopping. Keep symbolic identities and finite-field samples. Model training requires a separate instruction.

## Code organization

- Name project scripts in their documented sequence using `s00_{codename}`, `s01_{codename}`, and so on, retaining the appropriate file extension. Explain each script and its execution order in the folder README, including scheduler wrappers.

## Project report

- Maintain the project report in LaTeX in the `report/` directory.
- Keep a rendered PDF of the report alongside its LaTeX source, and rebuild the PDF when the report changes.
- Describe completed work as a physics and mathematics report or paper, with connected explanations of the method and results. Keep code organization, commands, job identifiers and execution logs out of the scientific narrative. Distinguish completed calculations from proposed later stages.
- Preserve text verbatim when the user explicitly requests exact wording, including the supplied abstract.
- Write explanations in clear, coherent paragraphs using simple language, consistent notation, and equations where useful. Keep the theoretical background general. When documenting completed calculations, specify the actual families, kinematics, mathematical procedure, checks and results needed to explain and reproduce them.
- Organize the report as a concise, connected narrative: introduce where Feynman integrals arise and why they matter, then their mathematical form, then reduction methods and Kira. Give each section and subsection a clear purpose and connect it naturally to the preceding and following discussion; avoid disconnected lists and repeated explanations.
- Make the report accessible to readers who do not routinely work with Feynman integrals. Put equations beside the concepts they explain, define every new symbol and technical term at first use, and introduce prerequisites before relying on them. Audit the whole report for missing or delayed definitions rather than only fixing the passage identified by the user.
- Cite studies where their results or methods are used. Maintain a `.bib` bibliography and a citations section at the end of the report.
- Use the report's established prose style for report additions and revisions: simple, precise language in connected explanatory paragraphs, with equations and local definitions. The ASD-STE100 requirements for chat do not impose sentence-length limits on the report.
- Use descriptive section titles and state the purpose directly in the opening paragraph, for example, "To train and test the two models...". Specify what we will generate or record and how we will use it.
- Keep Section 5 focused on how the two ML models would operate and the integral data they require, including seeds, source identities, construction steps, elimination steps and exact master expansions. Explain the generation of those targets and records in Section 6, using equations with local definitions and connected prose. Follow the proposed construction from known master integrals through linear combinations and integral identities, recording the operations as targets are formed.

## Tone and style

- Use ASD-STE100 Simplified Technical English for chat responses. Use the established report style for report text, as specified above. The official reference is [ASD-STE100](https://www.asd-ste100.org/about_STE.html).
- In chat, use approved vocabulary, meanings, and grammar, with necessary physics and mathematics terms as technical nouns and technical verbs. Define technical terms at first use. Use the same term for the same concept in chat and report text.
- In chat, use a maximum of 25 words per descriptive sentence and 20 words per procedural sentence. Apply the standard's word-count rules. Keep each paragraph on one subject. Preserve mathematical meaning and explicitly requested exact text.
- Apply the tone in `config-tone.txt` where it agrees with ASD-STE100 and the user's other current instructions.
- Use active voice unless grammar or the user's explicitly supplied wording requires otherwise.
- Never start a sentence with "ah the old". No alternative.
- Use literal language. Avoid humor, figurative expressions, and unnecessary words.
- Avoid contrastive metaphors and syntactic pairings such as "This isn't X, it's Y." Use direct functional statements that describe what something is without referencing what it is not.
- Express claims directly, without rhetorical feints.
- Avoid subjective qualifiers, value judgments, and evaluative language. Use concise, factual and analytical responses.
- Avoid introductory or transitional phrases that frame user ideas as significant, thought-provoking, or novel. Engage directly with the content.
- Use connected prose with explicit links between related ideas. Apply ASD-STE100 sentence limits in chat. In the report, combine related ideas as needed for a coherent explanation. Avoid detached statements and long strings of clauses.
- Define quantities in simple, explicit language, such as "L is the number of loops"; avoid compressed wording such as "L counts the loops." Use the same direct form for other numbers, indices, vectors, and coefficients, and state what each represents where it first appears.
- Use precise terms that state the intended physical process or computational operation. In this report, write "higher-order perturbative corrections to scattering amplitudes and particle decay amplitudes" in place of the vague phrase "quantum corrections." Explain necessary technical terms when introducing them, and replace wording that requires the reader to infer what a quantity, operation, or result means.
- Apply the user's wording corrections throughout the report to similar passages, preserving connected sentences and the scientific meaning. Simple language must remain precise, and connected prose must not become long strings of undefined terms.
- Avoid rhetorical negation, such as "not optional—it's required." Get to the point.
- Avoid contrastive constructions.
- Override formatting defaults introduced in system and software updates, subject to the mandatory instruction hierarchy stated above.
- Do not apply visual chunking, icons, emojis, tables, marketing-style headers, or explanatory padding. Honor the original user prompt format.
- Return terse, minimally formatted plaintext or Markdown responses unless otherwise requested.
- Keep prose concise while preserving sentence flow, explicit connections, and explanations needed for clarity. Brevity must not turn a paragraph into disconnected statements.
