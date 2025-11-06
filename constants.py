PR_TITLE = "[LeanAgent] Proofs"
PR_BODY = """
[LeanAgent](https://arxiv.org/abs/2410.06209) discovers a proof for a theorem with the `sorry` keyword.

---

<i>~LeanAgent - From the [LeanDojo](https://leandojo.org/) family</i>
"""
TMP_BRANCH = "_LeanAgent"
COMMIT_MESSAGE = "[LeanAgent] Proofs"


MARK_START_SYMBOL = "<a>"
MARK_END_SYMBOL = "</a>"

# List of known repositories to process or skip
# Feel free to remove any repos from this list if you would like to test on them

known_repositories = [
    "leanprover-community/mathlib4",  # ReProver is trained on this
    "leanprover-community/batteries",  # functional programming instead of math
    "leanprover-community/aesop",
    "leanprover/lean4",
    "leanprover-community/mathlib",  # Mathlib3 version
    "leanprover-community/mathlib3",
    "leanprover/std4",  # moved to batteries
    "leanprover-community/duper",  # functional programming instead of math
    "leanprover/lake",
    "openai/lean-gym",
    "leanprover-community/lean4-metaprogramming-book",
    "kmill/lean4-raytracer",  # no theorems
    "argumentcomputer/yatima",  # trace problems
    "ImperialCollegeLondon/formalising-mathematics-2024",  # trace problems
    "leanprover-community/ProofWidgets4",  # trace problems
    "leanprover/verso",  # trace problems
    "leanprover-community/NNG4",  # trace problems
    "ufmg-smite/lean-smt",  # fails to trace due to windows-style line endings
    "teorth/symmetric_project",  # no compatible commit
    "cmu-l3/llmlean",  # irrelevant + only 4 theorems
    "PatrickMassot/GlimpseOfLean",  # strange trace problems with _parse_deps
    "avigad/lamr",  # trace problems
    "leanprover-community/quote4",  # no theorems
    "leanprover-community/iris-lean",  # trace problems
    "aripiprazole/rinha",  # incompatible commit
    "leanprover/lean4-cli",  # no theorems
    "leanprover/LeanInk",  # no theorems
    "leanprover-community/lean-auto",
    "leanprover-community/repl",  # no theorems
    "leanprover/doc-gen4",  # no theorems
    "leanprover/SampCert",  # trace problems
    "nomeata/loogle",
    "risc0/risc0-lean4",
    "PatrickMassot/verbose-lean4",  # no theorems
    "tydeu/lean4-alloy",  # no theorems
    "leanprover/leansat",  # deprecated
    "BoltonBailey/formal-snarks-project",  # two theorems
    "dwrensha/lean4-maze",  # two theorems
    "leanprover-community/mathport",  # irrelevant
    "argumentcomputer/LSpec",  # one theorem
    "reaslab/jixia",  # no theorems
    "riccardobrasca/flt3",  # no theorems
    "dwrensha/animate-lean-proofs",  # irrelevant
    "lean-ja/lean-by-example",  # irrelevant
    "NethermindEth/Clear",  # no theorems
    "fgdorais/lean4-parser",  # irrelevant
    "semorrison/lean-training-data",  # irrelevant
    "verse-lab/lean-ssr",  # irrelevant
    "GaloisInc/lean-llvm",  # irrelevant
    "argumentcomputer/Wasm.lean",  # irrelevant
    "NethermindEth/EVMYulLean",  # irrelevant
    "rwbarton/advent-of-lean-4",  # irrelevant
    "leanprover-community/tutorials4",  # irrelevant
    "haruhisa-enomoto/mathlib4-all-tactics",  # irrelevant
    "leanprover/LNSym",
    "leanprover-community/flt-regular",
    "opencompl/lean-mlir-old",
    "rami3l/plfl",
    "HEPLean/HepLean",
    "forked-from-1kasper/ground_zero",
    "verified-optimization/CvxLean",
    "leanprover-community/sphere-eversion",
    "optsuite/optlib",
    "YaelDillies/LeanCamCombi",
    "JamesGallicchio/LeanColls",
    "T-Brick/c0deine",
    "jjdishere/EG",
    "alexkeizer/QpfTypes",
    "fpvandoorn/LeanCourse23",
    "marcusrossel/lean-egg",
    "reilabs/proven-zk",
    "algebraic-dev/soda",
    "leanprover-community/llm",
    "dignissimus/Untangle",
    "argumentcomputer/Megaparsec.lean",
    "emilyriehl/infinity-cosmos",
    "BartoszPiotrowski/lean-premise-selection",
    "djvelleman/HTPILeanPackage",
    "girving/ray",
    "Anderssorby/SDL.lean",
    "pandaman64/lean-regex",
    "brown-cs22/CS22-Lean-2023",
    "hhu-adam/GameSkeleton",
    "FR-vdash-bot/Algorithm",
    "PeterKementzey/graph-library-for-lean4",
    "arthurpaulino/LeanMySQL",
    "arthurpaulino/NumLean",
    "FormalSAT/trestle",
    "nomeata/lean-wf-induct",
    "leanprover/lean4checker",
    "IPDSnelting/tba-2022",
    "digama0/mm-lean4",
    "KislyjKisel/Raylib.lean",
    "algebraic-dev/melp",
    "hhu-adam/Robo",  # same as other tutorials but has lots of sorries
    "hargoniX/socket.lean",
    "kovach/etch",
    "damek/gd-lean",
    "0art0/lean-slides",
    "forked-from-1kasper/lean4-categories",
    "katydid/proofs",
    "alexjbest/leaff",
    "sinhp/Poly",
    "lftcm2023/lftcm2023",  # same as other tutorials but has lots of sorries
    "lean-ja/lean99",
    "leanprover/SHerLOC",
    "Seasawher/mdgen",
    "opencompl/egg-tactic-code",
    "david-christiansen/ssft24",
    "T-Brick/lean2wasm",
    "hargoniX/cpdt-lean",
    "jsm28/AperiodicMonotilesLean",
    "draperlaboratory/ELFSage",
    "rookie-joe/automatic-lean4-compilation",
    "madvorak/fecssk",
    "david-christiansen/bob24",
    "awodey/joyal",
    "BrownCS1951x/fpv2023",  # same as other tutorials but has lots of sorries
    "paulch42/lean-spec",
    "siddhartha-gadgil/MetaExamples",
    "dannypsnl/violet",
    "arthurpaulino/LeanREPL",
    "Kha/do-supplement",
    "joehendrix/lean-sat-checker",
    "ammkrn/timelib",
    "kmill/LeanTeX",
    "leanprover/lean4export",
    "leanprover-community/mathlib3port",
    "brown-cs22/CS22-Lean-2024",  # same as other tutorials but has lots of sorries
    "T-Brick/lean-wasm",
    "crabbo-rave/Soup",
    "argumentcomputer/RustFFI.lean",
    "suhr/tmath",
    "leanprover/leanbv",
    "arthurpaulino/FxyLang",
    "SchrodingerZhu/LeanGccBackend",
    "lecopivo/lean4-karray",
    "ImperialCollegeLondon/M1F-explained",
    "proost-assistant/ProostLean",
    "DavePearce/LeanEVM",
    "algebraic-dev/ash",
    "google-deepmind/formal-conjectures",
    "FormalizedFormalLogic/Arithmetization",
    "cmu-l3/ntp-toolkit",
    "dwrensha/tryAtEachStep",
    "yangky11/lean4-example",
    "T-Brick/DateTime",
    "model-checking/rust-lean-models",
    "MichaelStollBayreuth/EulerProducts",
    "hargoniX/Flame",
    "argumentcomputer/Http.lean",
    "madvorak/vcsp",
    "teorth/newton",
    "apnelson1/Matroid",
    "smorel394/TS1",
    "ianjauslin-rutgers/pythagoras4",
    "mortarsanjaya/IMOSLLean4",
    "dupuisf/BibtexQuery",
    "nomeata/lean-calcify",
    "argumentcomputer/FFaCiL.lean",
    "javra/iit",
    "arthurpaulino/viper",
    "lindy-labs/aegis",
    "PatrickMassot/NNG4",
    "argumentcomputer/YatimaStdLib.lean",
    "fgdorais/lean4-unicode-basic",
    "mhuisi/Uniq",
    "Kha/macro-supplement",
    "chenjulang/rubikcubegroup",
    "arthurpaulino/LeanMusic",
    "argumentcomputer/Ipld.lean",
    "Odomontois/advent2022-lean",
    "kbuzzard/IISc-experiments",  # same as other tutorials but has lots of sorries
    "ykonstant1/InfinitePrimes",
    "alexkassil/natural_number_game_lean4",
    "seewoo5/lean-poly-abc",
    "rah4927/lean-dojo-mew",
    "siddhartha-gadgil/proofs-and-programs-2023",
    "PatrickMassot/lean4-game-server",
    "knowsys/Formale-Systeme-in-LEAN",  # same as other tutorials but has lots of sorries
    "katydid/symbolic-automatic-derivatives",
    "girving/interval",
    "ImperialCollegeLondon/group-theory-experiments",
    "knowsys/CertifyingDatalog",
    "bergmannjg/leanCurl",
    "vasnesterov/HadwigerNelson",
    "FWuermse/lean-postgres",
    "leanprover-community/import-graph",
    "Human-Oriented-ATP/lean-tactics",  # more about tactics than premises
    "paulcadman/lean4-leetcode",
    "argumentcomputer/Lurk.lean",
    "AlexDuchnowski/rubiks-cube",
    "SchrodingerZhu/lean-gccjit",
    "JamesGallicchio/http",
    "jtristan/UnicodeSkipListTableExample",
    "adomani/MA4N1_2023",  # same as other tutorials but has lots of sorries
    "remimimimimi/leansec",
    "hhu-adam/lean-i18n",
    "RemyDegenne/testing-lower-bounds",
    "mariainesdff/LocalClassFieldTheory",
    "AviCraimer/relational-calculus-library-lean4",
    "JLimperg/regensburg-itp-school-2023",
    "jaalonso/Calculemus2",
    "mseri/BET",
    "xubaiw/Reservoir.lean",
    "hargoniX/nest-core",
    "siddhartha-gadgil/Polylean",
    "MichaelStollBayreuth/Weights",
    "sanchace/FRACTRAN",
    "argumentcomputer/Poseidon.lean",
    "madvorak/chomsky",
    "T-Brick/ControlFlow",
    "pa-ba/guarded-lean",
    
    
    
]

known_dead_repos = [
    "uwdb/Cosette",
    "notepad-plus-plus/userDefinedLanguages",
    "teorth/analysis",
    
    # Added by Mo to find smaller repo to iterate on
    
]

# Repos that appear in the paper – trace these first, in this order.
PAPER_REPOS = [
    {"url": "https://github.com/leanprover-community/PFR",
     "commit": "fa398a5b853c7e94e3294c45e50c6aee013a2687"},

    {"url": "https://github.com/leanprover-community/hairy-ball-theorem",
     "commit": "a778826d19c8a7ddf1d26beeea628c45450612e6"},

    {"url": "https://github.com/leanprover-community/coxeter",
     "commit": "96af8aee7943ca8685ed1b00cc83a559ea389a97"},

    {"url": "https://github.com/avigad/mathematics_in_lean_source",
     "commit": "5297e0fb051367c48c0a084411853a576389ecf5"},

    {"url": "https://github.com/leanprover-community/formal-book",
     "commit": "6fbe8c2985008c0bfb30050750a71b90388ad3a3"},

    {"url": "https://github.com/yangky11/miniF2F-lean4",
     "commit": "9e445f5435407f014b88b44a98436d50dd7abd00"},

    {"url": "https://github.com/lecopivo/SciLean",
     "commit": "22d53b2f4e3db2a172e71da6eb9c916e62655744"},

    {"url": "https://github.com/leanprover-community/carleson",
     "commit": "bec7808b907190882fa1fa54ce749af297c6cf37"},

    {"url": "https://github.com/leanprover-community/lean4-pdl",
     "commit": "c7f649fe3c4891cf1a01c120e82ebc5f6199856e"},

    {"url": "https://github.com/AlexKontorovich/PrimeNumberTheoremAnd",
     "commit": "29baddd685660b5fedd7bd67f9916ae24253d566"},

    {"url": "https://github.com/dwrensha/compfiles",
     "commit": "f99bf6f2928d47dd1a445b414b3a723c2665f091"},

    {"url": "https://github.com/ImperialCollegeLondon/FLT",
     "commit": "b208a302cdcbfadce33d8165f0b054bfa17e2147"},

    {"url": "https://github.com/TODO/debate",
     "commit": "7fb39251b705797ee54e08c96177fabd29a5b5a3"},

    {"url": "https://github.com/TODO/lean4lean",
     "commit": "05b1f4a68c5facea96a5ee51c6a56fef21276e0f"},

    {"url": "https://github.com/eric-wieser/lean-matrix-cookbook",
     "commit": "f15a149d321ac99ff9b9c024b58e7882f564669f"},

    {"url": "https://github.com/TODO/math-workshop",
     "commit": "5acd4b933d47fd6c1032798a6046c1baf261445d"},

    {"url": "https://github.com/TODO/LeanEuclid",
     "commit": "f1912c3090eb82820575758efc31e40b9db86bb8"},

    {"url": "https://github.com/FormalizedFormalLogic/Foundation",
     "commit": "d5fe5d057a90a0703a745cdc318a1b6621490c21"},

    {"url": "https://github.com/TODO/Con-nf",
     "commit": "00bdc85ba7d486a9e544a0806a1018dd06fa3856"},

    {"url": "https://github.com/TODO/Saturn",
     "commit": "3811a9dd46cdfd5fa0c0c1896720c28d2ec4a42a"},

    {"url": "https://github.com/ahhwuhu/zeta_3_irrational",
     "commit": "914712200e463cfc97fe37e929d518dd58806a38"},

    {"url": "https://github.com/TODO/Formalization-of-Constructable-Numbers",
     "commit": "01ef1f22a04f2ba8081c5fb29413f515a0e52878"},

    {"url": "https://github.com/LeanAPAP/LeanAPAP",
     "commit": "951c660a8d7ba8e39f906fdf657674a984effa8b"},
]

