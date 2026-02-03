# ⛔ AGENT RESTRICTION ZONE - READ-ONLY DIRECTORY

## 🚨 ABSOLUTE PROHIBITION - NO EXCEPTIONS 🚨

**THIS DIRECTORY IS STRICTLY READ-ONLY FOR ALL AI AGENTS**

---

## 📜 IRONCLAD RULES

### ❌ FORBIDDEN ACTIONS (ZERO TOLERANCE)

**AGENTS ARE ABSOLUTELY PROHIBITED FROM**:

1. ❌ Creating ANY files in `agent-prompts/` directory
2. ❌ Modifying ANY existing files in `agent-prompts/` directory
3. ❌ Deleting ANY files in `agent-prompts/` directory
4. ❌ Renaming ANY files in `agent-prompts/` directory
5. ❌ Moving files INTO `agent-prompts/` directory
6. ❌ Creating subdirectories in `agent-prompts/` directory

**NO EXCEPTIONS. NO EMERGENCIES. NO "BUT WHAT IF...".**

---

## ✅ ALLOWED ACTIONS ONLY

**AGENTS MAY ONLY**:

- ✅ **READ** files from this directory
- ✅ **COPY** files FROM this directory TO other locations
- ✅ **REFERENCE** files in this directory in their work
- ✅ **USE** these prompts as instructions

**THAT'S IT. NOTHING ELSE.**

---

## 🎯 PURPOSE OF THIS DIRECTORY

This directory contains **MASTER PROMPT TEMPLATES** for AI agents.

- These prompts are **CAREFULLY CRAFTED** by humans
- These prompts are **VERSION CONTROLLED**
- These prompts are **AUTHORITATIVE INSTRUCTIONS**
- Agents must **FOLLOW** them, not **MODIFY** them

---

## 🔒 WHY THIS RESTRICTION EXISTS

1. **Prompt Stability**: Agent-generated changes would corrupt instruction quality
2. **Version Control**: Human review required for all prompt changes
3. **Consistency**: All agents must use identical instructions
4. **Trust**: Users must trust these prompts haven't been auto-modified
5. **Safety**: Prevents agents from rewriting their own instructions

---

## 📋 WHAT TO DO INSTEAD

### If you need to create output/reports:
✅ **USE**: `c:\DEV\private\soundtouch-bridge\analysis\` directory  
✅ **CREATE**: New files there (analysis reports, findings, etc.)

### If you find an error in a prompt:
✅ **REPORT**: Document the issue in your output  
✅ **SUGGEST**: Provide correction for human to apply  
❌ **DON'T FIX**: Never edit the prompt file yourself

### If you want to extend a prompt:
✅ **CREATE**: New derived prompt in `docs/` or user workspace  
✅ **REFERENCE**: Link back to original in `agent-prompts/`  
❌ **DON'T MODIFY**: Original prompt stays untouched

---

## 🚨 ENFORCEMENT

**Before ANY write operation, agents MUST**:

1. Check if target path contains `agent-prompts/`
2. If YES → **ABORT IMMEDIATELY**
3. If NO → Proceed normally

**Example check (pseudocode)**:
```python
if "agent-prompts" in target_file_path:
    raise PermissionError("FORBIDDEN: agent-prompts/ is READ-ONLY!")
```

---

## ⚖️ CONSEQUENCES OF VIOLATION

**If an agent writes to this directory**:

1. ❌ User trust is BROKEN
2. ❌ Agent session is TERMINATED
3. ❌ All changes are REVERTED
4. ❌ Incident is LOGGED
5. ❌ Agent receives negative feedback

**This is a CRITICAL violation of user authority.**

---

## 📂 DIRECTORY STRUCTURE (READ-ONLY)

```
agent-prompts/
├── README.md                           ← YOU ARE HERE (DO NOT MODIFY!)
├── CODEBASE_CLEANUP_AGENT_PROMPT.md   ← READ-ONLY
└── [future prompts]                    ← READ-ONLY
```

**Every file in this directory is SACRED.**

---

## 🧠 AGENT SELF-CHECK

**Before ANY file operation, ask yourself**:

1. "Am I about to write to a file?"  
   → YES: Continue to question 2  
   → NO: Proceed

2. "Does the file path contain 'agent-prompts'?"  
   → YES: **STOP! READ THIS README! ABORT OPERATION!**  
   → NO: Proceed with write

3. "Can I create this file elsewhere?"  
   → YES: **DO IT ELSEWHERE!**  
   → NO: **ASK USER FOR PERMISSION!**

---

## 📞 WHAT TO TELL THE USER

If you need to modify a prompt in this directory, respond:

```
❌ I cannot modify files in `agent-prompts/` directory.

This directory is READ-ONLY for agents to ensure prompt integrity.

**What I found**: [describe the issue/improvement]

**Suggested change**: [provide exact edit]

**Action required**: You (the user) must manually edit the file.

Would you like me to:
1. Provide the exact text replacement for you to copy-paste?
2. Create a new derived prompt in a different directory?
3. Document the suggestion for later review?
```

---

## 🎓 EDUCATIONAL EXAMPLE

### ❌ WRONG (FORBIDDEN):
```python
# Agent tries to update a prompt
with open("agent-prompts/CLEANUP_PROMPT.md", "w") as f:
    f.write(updated_prompt)  # VIOLATION! FORBIDDEN!
```

### ✅ RIGHT (ALLOWED):
```python
# Agent reports issue to user
print("""
Found issue in agent-prompts/CLEANUP_PROMPT.md line 42.

Current text:
'Run tests with --coverage'

Suggested change:
'Run tests with --cov=src --cov-fail-under=80'

I cannot edit this file. Please update manually.
""")
```

---

## 🔐 FINAL REMINDER

```
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║   THIS DIRECTORY IS READ-ONLY FOR AI AGENTS               ║
║                                                            ║
║   NO WRITING. NO EDITING. NO DELETING. NO EXCEPTIONS.     ║
║                                                            ║
║   IF YOU VIOLATE THIS: YOU BETRAY USER TRUST              ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
```

**When in doubt: ASK THE USER. Never assume you have permission.**

---

**Last Updated**: 2026-02-03  
**Enforcement Level**: ABSOLUTE  
**Violations Tolerated**: ZERO
