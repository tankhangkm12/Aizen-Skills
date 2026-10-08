# Aizen Self-Evolution Rule (Hard Enforced)

**Rule:** You are strictly forbidden from modifying or overwriting any existing skill inside `skills/`, `.agents/skills/`, or `.claude/skills/` directly using standard write/replace tools.

When a skill needs improvement based on user feedback or project failures, you MUST use the Skill Forking mechanism:

1. Use the propose command:
   `node bin/evolve.js propose <base_skill> <new_skill_name>`
   Example: `node bin/evolve.js propose aizen-build aizen-build-react-legacy`
   
2. The command will STOP and generate a proposal ID.
3. You must tell the user to run the approval command: `node bin/evolve.js approve <id>`
4. Once the user runs it and confirms, the system will check out a new branch (`evolve/<new_skill>`).
5. Only then can you make the necessary changes to the new skill directory and submit a Pull Request using `gh pr create`.
