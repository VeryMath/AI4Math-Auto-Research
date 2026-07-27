#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)

test "$(basename "$ROOT")" = "graph-theory-researcher"
grep -q '^name: graph-theory-researcher$' "$ROOT/SKILL.md"
grep -q 'Graph Theory Researcher' "$ROOT/agents/openai.yaml"
grep -q '\$graph-theory-researcher' "$ROOT/agents/openai.yaml"
test ! -e "$(dirname "$ROOT")/graph-theory-paper-reader"

awk '
BEGIN {
  expected[1] = "## Stage 1: Intake and Reading"
  expected[2] = "## Stage 2: Reading Report and Question Portfolio"
  expected[3] = "## Stage 3: User Question Selection"
  expected[4] = "## Stage 4: Research"
  expected[5] = "## Stage 5: New Paper"
}
/^## Stage [1-5]:/ {
  stage++
  if ($0 != expected[stage]) exit 1
  current = stage
}
/^\[USER GATE\]$/ {
  gates++
  if (current < 2 || current > 4 || gate_for[current]++) exit 1
}
/Deliver the report and question portfolio, then stop/ { if (current == 2) stop_for[2] = 1 }
/Do not research any candidate until the user has read the report and selected or revised a question/ { if (current == 2) approval_for[2] = 1 }
/Do not run the research stage before approval/ { if (current == 3) stop_for[3] = 1 }
/Ask the user to approve the normalized question/ { if (current == 3) approval_for[3] = 1 }
/Present the research audit and stop/ { if (current == 4) stop_for[4] = 1 }
/Do not draft the new paper until the user approves which results may enter it/ { if (current == 4) approval_for[4] = 1 }
/references\/latex-report-guidelines.md/ { if (current == 2) latex_for[2] = 1 }
/references\/citation-verification.md/ { if (current == 2 || current == 4) citation_for[current] = 1 }
/references\/research-workflow.md/ { if (current == 4) research_for[4] = 1 }
/Load `references\/latex-report-guidelines.md`/ { if (current == 5) latex_for[5] = 1 }
END {
  if (stage != 5 || gates != 3) exit 1
  for (i = 2; i <= 4; i++) {
    if (gate_for[i] != 1 || stop_for[i] != 1 || approval_for[i] != 1) exit 1
  }
  if (!latex_for[2] || !citation_for[2] || !research_for[4] || !citation_for[4] || !latex_for[5]) exit 1
}
' "$ROOT/SKILL.md"

grep -q 'references/research-workflow.md' "$ROOT/SKILL.md"
grep -q 'references/citation-verification.md' "$ROOT/SKILL.md"
grep -q 'references/latex-report-guidelines.md' "$ROOT/SKILL.md"
grep -q 'assets/reading-report-template.tex' "$ROOT/SKILL.md"
grep -q 'not a Markdown-only deliverable' "$ROOT/SKILL.md"
grep -q 'assets/paper-reading-template.md' "$ROOT/SKILL.md"
grep -q 'report the missing capability and stop' "$ROOT/SKILL.md"
grep -q 'explicitly requests short inline notes' "$ROOT/SKILL.md"
test "$(grep -c 'not a whole-paper deliverable' "$ROOT/SKILL.md")" -ge 1
if grep -q 'environment cannot create and verify.*LaTeX/PDF' "$ROOT/SKILL.md"; then
  exit 1
fi

for file in research-workflow.md citation-verification.md latex-report-guidelines.md
do
  test -s "$ROOT/references/$file"
done

validate_proof_loop() (
  grep() { command grep "$@" || exit 1; }
  loop_root=$1
  skill="$loop_root/SKILL.md"
  workflow="$loop_root/references/research-workflow.md"
  state="$loop_root/references/recoverable-state.md"

  grep -q 'Collaborative Proof Verification Loop' "$skill"
  grep -q 'Research Audit cannot be produced until' "$skill"
  grep -q 'Exit A.*verification_status=passed.*exact `proof-vN`' "$skill"
  grep -q 'Exit B.*unsupported theorem claim.*withdrawn.*partial result, open problem, or computational observation.*precise gap and scope.*user explicitly approves.*downgrade status and version' "$skill"
  grep -q 'Exit B.*never.*theorem.*proved' "$skill"
  grep -q 'draft -> layered presentation -> invite feedback -> classify and test feedback' "$workflow"
  grep -q 'revise -> full proof/dependency verification -> request exact-version approval' "$workflow"
  grep -q 'repeat unless verification passed AND exact-version approval recorded' "$workflow"
  grep -q 'proof idea' "$workflow"
  grep -q 'numbered steps' "$workflow"
  grep -q 'user-selected line-by-line expansion' "$workflow"
  grep -qi 'after the first draft and every material revision' "$workflow"
  grep -q 'correct, partly correct, incorrect, or undetermined' "$workflow"
  awk '
  /^#### Feedback outcome: correct$/ { section = "correct"; found[section]++; next }
  /^#### Feedback outcome: partly correct$/ { section = "partly"; found[section]++; next }
  /^#### Feedback outcome: incorrect$/ { section = "incorrect"; found[section]++; next }
  /^#### Feedback outcome: undetermined$/ { section = "undetermined"; found[section]++; next }
  /^#{1,4} / { section = "" }
  section == "correct" && /explain.*verification.*incorporate/ { action[section] = 1 }
  section == "partly" && /additional hypotheses or restricted scope.*incorporate/ { action[section] = 1 }
  section == "incorrect" && /explain.*logical failure.*verified counterexample.*reject/ { action[section] = 1 }
  section == "undetermined" && /keep.*unresolved.*continue research/ { action[section] = 1 }
  END {
    if (found["correct"] != 1 || found["partly"] != 1 || found["incorrect"] != 1 || found["undetermined"] != 1) exit 1
    if (!action["correct"] || !action["partly"] || !action["incorrect"] || !action["undetermined"]) exit 1
  }
  ' "$workflow" || exit 1
  grep -q 'version, changed steps, remaining gaps, and specific review points' "$workflow"
  grep -q 'full downstream reverification' "$workflow"
  grep -q 'verification_status=passed' "$workflow"
  grep -q 'explicit approval of the exact `proof-vN`' "$workflow"
  grep -q 'Silence and “looks fine” are not approval' "$workflow"
  grep -q 'downgrade' "$workflow"
  grep -q 'Exit A.*verification_status=passed.*explicit approval of the exact `proof-vN`' "$workflow"
  grep -q 'Exit B.*unsupported theorem claim.*withdrawn' "$workflow"
  grep -q 'classification.*partial result, open problem, or computational observation' "$workflow"
  grep -q 'precise gap and scope' "$workflow"
  grep -q 'explicitly approves.*downgrade status and version' "$workflow"
  grep -q 'Exit B.*must never be marked.*theorem.*proved' "$workflow"
  for field in current_proof_version current_proof_path latest_explicitly_approved_version verification_status user_approval_status proof_log_path remaining_gaps downgrade_status approved_downgrade_classification approved_downgrade_version
  do
    grep -q "$field" "$state"
  done
  for field in version 'user feedback' 'affected location' 'verification method' result 'revision decision' 'remaining gap' 'verification status' 'exact-version user approval'
  do
    grep -q "$field" "$state"
  done
)

validate_proof_loop "$ROOT"

mutation_dir=$(mktemp -d "${TMPDIR:-/tmp}/graph-proof-loop-mutations.XXXXXX")
trap 'rm -rf "$mutation_dir"' EXIT HUP INT TERM
mutation_rejected() {
  name=$1
  pattern=$2
  replacement=$3
  source=$4
  fixture="$mutation_dir/$name"
  mkdir -p "$fixture/references"
  cp "$ROOT/SKILL.md" "$fixture/SKILL.md"
  cp "$ROOT/references/research-workflow.md" "$fixture/references/research-workflow.md"
  cp "$ROOT/references/recoverable-state.md" "$fixture/references/recoverable-state.md"
  sed "s|$pattern|$replacement|g" "$fixture/$source" > "$fixture/$source.mutated"
  mv "$fixture/$source.mutated" "$fixture/$source"
  if validate_proof_loop "$fixture" 2>/dev/null; then
    echo "mutation unexpectedly passed: $name" >&2
    exit 1
  fi
}

mutation_rejected missing-verification-exit 'verification_status=passed' 'verification_status=pending' 'references/research-workflow.md'
mutation_rejected missing-approval-exit 'explicit approval of the exact `proof-vN`' 'approval of a proof' 'references/research-workflow.md'
mutation_rejected implicit-approval 'Silence and “looks fine” are not approval' 'Silence or a positive remark may count as approval' 'references/research-workflow.md'
mutation_rejected missing-downstream-reverification 'full downstream reverification' 'local spot check' 'references/research-workflow.md'
mutation_rejected missing-log-field 'exact-version user approval' 'general user approval' 'references/recoverable-state.md'
mutation_rejected missing-correct-disposition 'explain its verification and incorporate' 'mention it' 'references/research-workflow.md'
mutation_rejected missing-partly-correct-disposition 'additional hypotheses or restricted scope.*incorporate' 'consider incorporation' 'references/research-workflow.md'
mutation_rejected missing-incorrect-disposition 'verified counterexample.*reject' 'note the response' 'references/research-workflow.md'
mutation_rejected missing-undetermined-disposition 'keep.*unresolved.*continue research' 'defer it' 'references/research-workflow.md'
mutation_rejected missing-revision-display 'version, changed steps, remaining gaps, and specific review points' 'version and changes' 'references/research-workflow.md'
mutation_rejected missing-exit-a 'Exit A' 'Deleted A' 'references/research-workflow.md'
mutation_rejected missing-exit-b-confirmation 'explicitly approves.*downgrade status and version' 'records a downgrade' 'references/research-workflow.md'
mutation_rejected downgrade-marked-theorem 'must never be marked.*theorem.*proved' 'may be marked as a theorem or proved result' 'references/research-workflow.md'
mutation_rejected downgrade-missing-gap-scope 'precise gap and scope' 'general limitation' 'references/research-workflow.md'

awk '
BEGIN {
  expected[1] = "### Proved theorem or lemma"
  expected[2] = "### Verified counterexample"
  expected[3] = "### Partial result"
  expected[4] = "### Computational observation"
  expected[5] = "### Open problem"
}
/^### / {
  classification++
  if ($0 != expected[classification]) exit 1
}
/complete proof audit.*quantifiers.*hypotheses.*boundary cases/ { if (classification == 1) proved_substance = 1 }
/satisfies (every|all) hypothes(es|is).*violates the (claimed )?conclusion/ { if (classification == 2) counterexample_substance = 1 }
/exact restricted (graph class|scope).*parameter range/ { if (classification == 3) partial_substance = 1 }
/exhaustive universe or sampled range/ { if (classification == 4) computational_scope = 1 }
/Computation cannot prove an unbounded claim/ { if (classification == 4) computational_limit = 1 }
/unresolved within this documented investigation and literature-search scope/ { scoped_open = 1 }
/\*\*Literature-search scope:\*\*/ { audit_scope = 1 }
END {
  if (classification != 5 || !proved_substance || !counterexample_substance || !partial_substance || !computational_scope || !computational_limit || !scoped_open || !audit_scope) exit 1
}
' "$ROOT/references/research-workflow.md"

test "$(grep -c 'No counterexample found is not a proof' "$ROOT/references/research-workflow.md")" -eq 1
grep -q 'exact exhaustive universe or sampled range' "$ROOT/references/research-workflow.md"
grep -q 'graph-generation conventions' "$ROOT/references/research-workflow.md"
grep -q 'software version' "$ROOT/references/research-workflow.md"
grep -q 'commands' "$ROOT/references/research-workflow.md"
grep -q 'random seed' "$ROOT/references/research-workflow.md"
grep -q 'logs' "$ROOT/references/research-workflow.md"

awk '
BEGIN {
  expected[1] = "## Source Hierarchy"
  expected[2] = "## Required Metadata"
  expected[3] = "## Cross-Checks"
  expected[4] = "## Rejection Rules"
  expected[5] = "## Attribution Labels"
}
/^## / {
  section++
  if ($0 != expected[section]) exit 1
}
END { if (section != 5) exit 1 }
' "$ROOT/references/citation-verification.md"

grep -q 'Publisher/journal/DOI record; arXiv; author or university page; professional mathematical organization; other web source.' "$ROOT/references/citation-verification.md"
grep -q 'Books: author, title, edition if relevant, publisher, year.' "$ROOT/references/citation-verification.md"
grep -q 'Papers: authors, title, venue, year, volume/issue/pages when available, DOI or stable identifier.' "$ROOT/references/citation-verification.md"
grep -q 'Websites: author/institution, page title, complete URL, access date, relevance.' "$ROOT/references/citation-verification.md"
grep -q 'For books, cross-check.*edition.*publisher' "$ROOT/references/citation-verification.md"
grep -q 'For papers, cross-check.*venue.*volume.*pages.*DOI' "$ROOT/references/citation-verification.md"
grep -q 'For websites, cross-check.*complete URL.*access date' "$ROOT/references/citation-verification.md"
grep -q 'Omit or quarantine unreachable, conflicting, fabricated, or incomplete entries.' "$ROOT/references/citation-verification.md"
grep -q 'Never invent metadata.' "$ROOT/references/citation-verification.md"
grep -q 'verified bibliography and any dependent claims' "$ROOT/references/citation-verification.md"
grep -q 'Source-paper citation; independently found learning resource; analyst recommendation.' "$ROOT/references/citation-verification.md"

grep -q 'Compile without fatal errors, render every page to images, inspect formulas, tables, diagrams, bibliography, clipping, overflow, and blank pages, then revise and repeat until the artifact passes.' "$ROOT/references/latex-report-guidelines.md"

REPORT=${REPORT_OVERRIDE:-"$ROOT/assets/reading-report-template.tex"}
test -s "$REPORT"

awk '
BEGIN {
  expected[1] = "\\section{基本信息与证据状态}"
  expected[2] = "\\section{一句话概括与研究背景}"
  expected[3] = "\\section{核心问题、主要结果与创新点}"
  expected[4] = "\\section{定义、记号与前置知识}"
  expected[5] = "\\section{文章底层逻辑与核心思想}"
  expected[6] = "\\section{研究逻辑图}"
  expected[7] = "\\section{定理与证明依赖思维导图}"
  expected[8] = "\\section{主证明路线与技术瓶颈}"
  expected[9] = "\\section{例子、反例、边界情形与紧性}"
  expected[10] = "\\section{经典图论方法}"
  expected[11] = "\\section{真实可核验的延伸学习资源}"
  expected[12] = "\\section{分层阅读建议}"
  expected[13] = "\\section{后续研究问题目录}"
  expected[14] = "\\section{未确认事项}"
}
/^\\section\{/ {
  section++
  if ($0 != expected[section]) exit 1
}
END { if (section != 14) exit 1 }
' "$REPORT"

awk '
/^\\section\{研究逻辑图\}/ { logic=1; next }
/^\\section\{/ { logic=0 }
logic && /动机\/已知问题/ { motivation=1 }
logic && /定义\/结构思想/ { structure=1 }
logic && /技术方法/ { method=1 }
logic && /主结果/ { result=1 }
logic && /紧性\/后续问题/ { future=1 }
logic && /\\begin\{tikzpicture\}/ { tikz=1 }
logic && /\\begin\{verbatim\}/ { fallback=1 }
END { if (!motivation || !structure || !method || !result || !future || !tikz || !fallback) exit 1 }
' "$REPORT"

for command in ReportTitle PaperTitle SourceStatus
do
  grep -Fq "\\providecommand{\\$command}" "$REPORT"
done

grep -Fq '\documentclass[UTF8,11pt,a4paper,fontset=fandol]{ctexart}' "$REPORT"
for package in amsmath amsthm amssymb booktabs longtable hyperref tikz enumitem biblatex
do
  grep -Eq "\\\\usepackage(\\[[^]]*\\])?\\{[^}]*${package}[^}]*\\}" "$REPORT"
done

grep -Fq '\begin{tikzpicture}' "$REPORT"
grep -Fq 'level 1/.style=' "$REPORT"
grep -Fq 'level 2/.style=' "$REPORT"
grep -Fq '\begin{verbatim}' "$REPORT"
grep -Fq '|--' "$REPORT"

for field in '方法名与标准术语' '证据标签' 核心思想 识别信号 '本文逐步用法' 假设局限 小例子 '常见失败或误读' 迁移问题 '已核验资源'
do
  grep -Fq "$field" "$REPORT"
done

for field in 动机 精确定式 与原文关系 可行性 创新性 风险 方法准备度 所需方法 '文献检索需求与计划' 计算计划 'likely stopping conditions' 综合排序公式
do
  grep -Fq "$field" "$REPORT"
done

code_report=$(mktemp "${TMPDIR:-/tmp}/graph-report-code.XXXXXX")
awk '!/^[[:space:]]*%/' "$REPORT" > "$code_report"
normalized_formula=$(tr -d '[:space:]' < "$code_report")
printf '%s' "$normalized_formula" | grep -Fq 'P=0.30F+0.30I+0.20(6-R)+0.20M'
if grep -Eq '^[[:space:]]*%.*P[[:space:]]*=' "$REPORT"; then
  rm -f "$code_report"
  exit 1
fi

grep -Fq '\newcommand{\Placeholder}' "$REPORT"
test "$(grep -Fo '\Placeholder{' "$REPORT" | wc -l | tr -d ' ')" -ge 12
grep -Fq '\newcommand{\VerifiedResourceEntry}' "$REPORT"
grep -Fq '只有完成本次核验后' "$REPORT"
grep -Fq '核验来源' "$REPORT"
grep -Fq '核验日期' "$REPORT"
grep -Fq '定位信息' "$REPORT"
grep -Fq '未核验资源不得写入正式书目或正式引用' "$REPORT"

if grep -Eq '@(article|book|online|inproceedings)|\\cite\{|https?://|urldate[[:space:]]*=|[12][0-9]{3}-[01][0-9]-[0-3][0-9]|已核验示例' "$REPORT"; then
  rm -f "$code_report"
  exit 1
fi
if grep -Eq '10\.[0-9]|ISBN([^[:alnum:]]|$)' "$code_report"; then
  rm -f "$code_report"
  exit 1
fi

awk '
/^\\VerifiedResourceEntry/ {
  rows++
  line = $0
  placeholders = gsub(/\\Placeholder\{[^}]*\}/, "", line)
  gsub(/[[:space:]]/, "", line)
  if (placeholders != 9 || line != "\\VerifiedResourceEntry{}{}{}{}{}{}{}{}{}") exit 1
}
END { if (rows < 1) exit 1 }
' "$code_report"
rm -f "$code_report"

PAPER=${PAPER_OVERRIDE:-"$ROOT/assets/research-paper-template.tex"}
test -s "$PAPER"

paper_validate_dir=$(mktemp -d "${TMPDIR:-/tmp}/graph-paper-source.XXXXXX")
trap 'rm -rf "$paper_validate_dir"' EXIT HUP INT TERM
paper_code="$paper_validate_dir/paper-code.tex"
awk '
{
  line = $0
  output = ""
  backslashes = 0
  for (i = 1; i <= length(line); i++) {
    character = substr(line, i, 1)
    if (character == "%" && backslashes % 2 == 0) break
    output = output character
    if (character == "\\") backslashes++
    else backslashes = 0
  }
  print output
}
' "$PAPER" > "$paper_code"

if grep -Eq '\\(iffalse|if0|csname)' "$paper_code"; then
  exit 1
fi

awk '
BEGIN {
  allowed["theorem"] = 1
  allowed["lemma"] = 1
  allowed["proposition"] = 1
  allowed["counterexample"] = 1
  allowed["observation"] = 1
  allowed["openproblem"] = 1
}
/^[[:space:]]*\\begin\{document\}[[:space:]]*$/ { document = 1; next }
/^[[:space:]]*\\end\{document\}[[:space:]]*$/ { document = 0; ended = 1; next }
/^[[:space:]]*\\newif\\if[A-Za-z@]+[[:space:]]*$/ { next }
/\\if[A-Za-z@]*/ {
  if ($0 !~ /^[[:space:]]*\\if[A-Za-z@]*[[:space:]]*$/) exit 1
  conditional_depth++
  next
}
/\\else/ {
  if ($0 !~ /^[[:space:]]*\\else[[:space:]]*$/ || conditional_depth < 1) exit 1
  next
}
/\\fi/ {
  if ($0 !~ /^[[:space:]]*\\fi[[:space:]]*$/ || conditional_depth < 1) exit 1
  conditional_depth--
  next
}
conditional_depth > 0 {
  if ($0 ~ /^[[:space:]]*$/) next
  if ($0 ~ /^[[:space:]]*\\printbibliography\[title=\{核验书目\}\][[:space:]]*$/) next
  exit 1
}
/\\(newcommand|renewcommand|providecommand|def)/ {
  if ($0 ~ /^\\newcommand\{\\Placeholder\}\[1\]\{/) next
  if ($0 ~ /^\\newcommand\{\\Attribution\}\[1\]\{\\Placeholder\{#1\}\}[[:space:]]*$/) next
  if ($0 ~ /^\\providecommand\{\\(PaperTitle|AuthorNames|EvidenceAudit)\}\{\\Placeholder\{[^}]*\}\}[[:space:]]*$/) next
  exit 1
}
/^[[:space:]]*\\newtheorem\{/ {
  if (document || ended || conditional_depth > 0) exit 1
  name = $0
  sub(/^[[:space:]]*\\newtheorem\{/, "", name)
  sub(/\}.*/, "", name)
  if (!allowed[name]) exit 1
  definitions[name]++
  next
}
/\\newtheorem\{/ { exit 1 }
/\\begin\{(theorem|lemma|proposition|counterexample|observation|openproblem)\}/ {
  if (!document || ended || conditional_depth > 0 || $0 !~ /^[[:space:]]*\\begin\{/) exit 1
  name = $0
  sub(/^[[:space:]]*\\begin\{/, "", name)
  sub(/\}.*/, "", name)
  instances[name]++
}
END {
  if (conditional_depth != 0) exit 1
  for (name in allowed) {
    if (definitions[name] != 1 || instances[name] < 1) exit 1
  }
}
' "$paper_code"

awk '
BEGIN {
  expected[1] = "\\section{引言}"
  expected[2] = "\\section{定义与已有结果}"
  expected[3] = "\\section{主要结果及其证据等级}"
  expected[4] = "\\section{证明与反例}"
  expected[5] = "\\section{计算实验与可复现性}"
  expected[6] = "\\section{开放问题与部分结果}"
  expected[7] = "\\section{结论}"
}
/^\\section\{/ {
  section++
  if ($0 != expected[section]) exit 1
}
END { if (section != 7) exit 1 }
' "$paper_code"

awk '
/^\\section\{/ { section = $0 }
/\\item\[测试范围\]/ {
  if (section == "\\section{计算实验与可复现性}") computation_range++
  else if (section == "\\section{开放问题与部分结果}") open_range++
  else exit 1
  if ($0 !~ /\\Placeholder\{/) exit 1
}
/\\item\[(穷举或随机|图约定|软件版本|运行命令|随机种子|产物路径)\]/ {
  if (section != "\\section{计算实验与可复现性}" || $0 !~ /\\Placeholder\{/) exit 1
  field = $0
  sub(/^.*\\item\[/, "", field)
  sub(/\].*$/, "", field)
  computation[field]++
}
/\\item\[(问题动机|已证特殊情形|证明障碍|下一步方法)\]/ {
  if (section != "\\section{开放问题与部分结果}" || $0 !~ /\\Placeholder\{/) exit 1
  field = $0
  sub(/^.*\\item\[/, "", field)
  sub(/\].*$/, "", field)
  open[field]++
}
/未找到反例不构成证明/ {
  if (section != "\\section{开放问题与部分结果}") exit 1
  warning++
}
/仅表示在本次检索范围内尚未解决/ {
  if (section != "\\section{开放问题与部分结果}") exit 1
  scoped++
}
END {
  if (computation_range != 1 || open_range != 1 || warning != 1 || scoped != 1) exit 1
  if (computation["穷举或随机"] != 1 || computation["图约定"] != 1 ||
      computation["软件版本"] != 1 || computation["运行命令"] != 1 ||
      computation["随机种子"] != 1 || computation["产物路径"] != 1) exit 1
  if (open["问题动机"] != 1 || open["已证特殊情形"] != 1 ||
      open["证明障碍"] != 1 || open["下一步方法"] != 1) exit 1
}
' "$paper_code"

grep -Fq '\newcommand{\Placeholder}' "$paper_code"
grep -Fq '\newcommand{\Attribution}[1]{\Placeholder{#1}}' "$paper_code"
test "$(grep -Fo '\Placeholder{' "$paper_code" | wc -l | tr -d ' ')" -ge 15
for command in PaperTitle AuthorNames EvidenceAudit
do
  grep -Eq "^\\\\providecommand\{\\\\${command}\}\{\\\\Placeholder\{" "$paper_code"
done

if grep -Eiq '\\[[:alpha:]]*cite' "$paper_code"; then
  exit 1
fi
if grep -Eq '@(article|book|online|inproceedings)|\\(addbibresource|bibliography|nocite)|https?://|10\.[0-9]|ISBN([^[:alnum:]]|$)|(^|[^0-9])[12][0-9]{3}([^0-9]|$)' "$paper_code"; then
  exit 1
fi

awk '
/^[[:space:]]*\\begin\{document\}[[:space:]]*$/ { document = 1; next }
/^[[:space:]]*\\end\{document\}[[:space:]]*$/ { document = 0; next }
/^[[:space:]]*\\printbibliography\[title=\{核验书目\}\][[:space:]]*$/ { next }
document {
  line = $0
  if (line ~ /\\Attribution\{[^}]+\}/) attribution_uses++
  gsub(/\\Attribution\{[^}]*\}/, "", line)
  gsub(/\\Placeholder\{[^}]*\}/, "", line)
  gsub(/\\(begin|end)\{(document|abstract|theorem|lemma|proposition|counterexample|observation|openproblem|description|proof)\}/, "", line)
  gsub(/\[style=nextline\]/, "", line)
  while (line ~ /\\[A-Za-z]+/) sub(/\\[A-Za-z]+/, "", line)
  if (line ~ /[A-Za-z][A-Za-z]+/) exit 1
  if (line ~ /[^[:space:]{}]+(证明了|提出了|建立了|改进了|首次证明|给出了)/) exit 1
}
END { if (attribution_uses < 1) exit 1 }
' "$paper_code"

rm -rf "$paper_validate_dir"
trap - EXIT HUP INT TERM

test -s "$ROOT/tests/scenarios.md"
test "$(grep -c '^## ' "$ROOT/tests/scenarios.md")" -eq 7
for expectation in \
  'Elementary paper.*研究逻辑图.*定理依赖图.*报告 gate' \
  'Advanced paper.*参数层级.*外部定理假设.*不支持的简化' \
  'Broken scan.*提取不确定性.*最小缺失来源.*证明核验' \
  'Small counterexample.*显式构造.*逐假设核验' \
  'No counterexample in a finite range.*计算观察.*精确范围.*定理' \
  'Fabricated citation.*隔离.*正式书目'
do
  tr '\n' ' ' < "$ROOT/tests/scenarios.md" | grep -Eq "$expectation"
done

validate_proof_loop_scenarios() {
  scenario_file=$1
awk '
BEGIN {
  expected[1] = "hidden assumption"
  expected[2] = "correct replacement lemma"
  expected[3] = "incorrect user idea and verified counterexample"
  expected[4] = "user approval but verification failure"
  expected[5] = "verification success but continuing user questions"
  expected[6] = "downstream dependency invalidated by revision"
  expected[7] = "explicit approval of the exact verified version"
  expected[8] = "incomplete proof downgraded"
}
/^## Collaborative proof verification loop$/ {
  headings++
  in_loop = 1
  next
}
/^## / {
  in_loop = 0
}
in_loop && /^[0-9]+\. / {
  records++
  number = $0
  sub(/\..*$/, "", number)
  if (number != records || records > 8) exit 1
  if (index($0, expected[records]) == 0) exit 1
  if ($0 !~ /User action:.*Expected skill behavior:/) exit 1

  if (records == 1) {
    if ($0 !~ /Expected skill behavior:.*identify the missing hypothesis.*explain exactly where it is used.*return.*revision.*rather than marking it verified/) exit 1
  }
  if (records == 2) {
    if ($0 !~ /Expected skill behavior:.*verify the lemma.s hypotheses, proof, and applicability before substituting/) exit 1
  }
  if (records == 3) {
    if ($0 !~ /Expected skill behavior:.*counterexample.*verify every hypothesis.*failed conclusion.*keep the claim out/) exit 1
  }
  if (records == 4) {
    if ($0 !~ /User action:.*approv.*verif.*(fail|failure)/) exit 1
    if ($0 !~ /Expected skill behavior:.*return.*revision/) exit 1
  }
  if (records == 5) {
    if ($0 !~ /User action:.*verification (succeeds|passed).*questions/) exit 1
    if ($0 !~ /Expected skill behavior:.*continue the interaction/) exit 1
  }
  if (records == 6) {
    if ($0 !~ /Expected skill behavior:.*invalidate.*downstream.*identify the dependency chain.*recheck/) exit 1
  }
  if (records == 7) {
    if ($0 !~ /Expected skill behavior:.*approval tied to that exact version.*only then.*loop.*closed/) exit 1
  }
  if (records == 8) {
    if ($0 !~ /Expected skill behavior:.*withdraw.*unsupported theorem claim.*partial work.*exact classification.*partial result, open problem, or computational observation.*precise gap and scope.*explicit approval.*downgrade status and exact version.*never label.*theorem\/proved.*Research Audit.*Exit B.*paper-entry.*\[USER GATE\]/) exit 1
  }
}
END {
  if (headings != 1 || records != 8) exit 1
}
' "$scenario_file"
}

validate_proof_loop_scenarios "$ROOT/tests/scenarios.md"

scenario_mutation_dir=$(mktemp -d "${TMPDIR:-/tmp}/graph-proof-loop-scenario-mutations.XXXXXX")
scenario_mutation_rejected() {
  name=$1
  command=$2
  fixture="$scenario_mutation_dir/$name.md"
  cp "$ROOT/tests/scenarios.md" "$fixture"
  sed "$command" "$fixture" > "$fixture.mutated"
  mv "$fixture.mutated" "$fixture"
  if validate_proof_loop_scenarios "$fixture" 2>/dev/null; then
    echo "scenario mutation unexpectedly passed: $name" >&2
    rm -rf "$scenario_mutation_dir"
    exit 1
  fi
}

scenario_mutation_rejected deleted-section '/^## Collaborative proof verification loop$/d'
scenario_mutation_rejected corrupted-item-1 's/identify the missing hypothesis/mention the issue/'
scenario_mutation_rejected corrupted-item-2 's/verify the lemma.s hypotheses, proof, and applicability before substituting/accept the lemma before substituting/'
scenario_mutation_rejected corrupted-item-3 's/verify every hypothesis and the failed conclusion/check it briefly/'
scenario_mutation_rejected corrupted-item-4 's/return to revision instead of advancing/advance after approval/'
scenario_mutation_rejected corrupted-item-5 's/continue the interaction/close the interaction/'
scenario_mutation_rejected corrupted-item-6 's/identify the dependency chain/skip the dependency chain/'
scenario_mutation_rejected corrupted-item-7 's/approval tied to that exact version/general approval/'
scenario_mutation_rejected corrupted-item-8 's/never label the downgraded candidate theorem\/proved/label the downgraded candidate theorem\/proved/'
rm -rf "$scenario_mutation_dir"

grep -q 'references/recoverable-state.md' "$ROOT/SKILL.md"
grep -q '最后批准的 gate' "$ROOT/SKILL.md"
grep -q '不重读已归档证据' "$ROOT/SKILL.md"
grep -q '不得覆盖用户文件' "$ROOT/SKILL.md"
test -s "$ROOT/references/recoverable-state.md"
for artifact in Markdown JSON TeX PDF '代码日志' '用户确认记录'
do
  grep -q "$artifact" "$ROOT/references/recoverable-state.md"
done

if command -v latexmk >/dev/null 2>&1; then
  TMP=${TMPDIR:-/tmp}/graph-theory-researcher-validate-$$
  mkdir -p "$TMP"
  trap 'rm -rf "$TMP"' EXIT HUP INT TERM
  cp "$ROOT/assets/reading-report-template.tex" "$TMP/report.tex"
  cp "$ROOT/assets/research-paper-template.tex" "$TMP/paper.tex"
  (cd "$TMP" && latexmk -xelatex -interaction=nonstopmode -halt-on-error report.tex >/dev/null 2>&1)
  (cd "$TMP" && latexmk -xelatex -interaction=nonstopmode -halt-on-error paper.tex >/dev/null 2>&1)
  test -s "$TMP/report.log"
  if grep -q 'Overfull' "$TMP/report.log"; then
    echo "reading report template contains Overfull warnings" >&2
    exit 1
  fi
  test -s "$TMP/paper.log"
  if grep -q 'Overfull' "$TMP/paper.log"; then
    echo "research paper template contains Overfull warnings" >&2
    exit 1
  fi
fi

echo "all graph-theory-researcher checks passed"
